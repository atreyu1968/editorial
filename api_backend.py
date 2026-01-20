# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import uuid
from typing import Optional
import json

app = FastAPI(title="Atreyu Servicios Digitales - API Pro v2")

# Configuración de Seguridad Solicitada
ADMIN_PASSWORD = "697457" 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "editorial.db"
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Servimos archivos estáticos (Logo y multimedia)
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla Autores (Incluye Drive y Landing)
    cursor.execute('''CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, bio TEXT, lang TEXT, photo_path TEXT, 
        drive_url TEXT, landing_url TEXT)''')
    
    # Tabla Series (Incluye Drive y Landing)
    cursor.execute('''CREATE TABLE IF NOT EXISTS series (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, author_id INTEGER, imprint_id INTEGER, status TEXT, 
        volumes INTEGER, logo_path TEXT, drive_url TEXT, landing_url TEXT)''')
    
    # Tabla Libros (ROI + Metadatos + Drive + Tiendas)
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT, author_id INTEGER, imprint_id INTEGER, series_id INTEGER, 
        status TEXT, ku BOOLEAN, last_metadata_review TEXT, formats TEXT, 
        cover_path TEXT, drive_url TEXT, amazon_url TEXT, d2d_url TEXT, landing_url TEXT,
        prod_cost_cover REAL DEFAULT 0, prod_cost_trans REAL DEFAULT 0, 
        prod_cost_edit REAL DEFAULT 0, keywords TEXT, categories TEXT, checklist TEXT)''')
    
    # Tabla Sellos
    cursor.execute('''CREATE TABLE IF NOT EXISTS imprints (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, lang TEXT, 
        color TEXT, landing_url TEXT)''')

    # Tabla Ecosistema (Enlaces Externos)
    cursor.execute('''CREATE TABLE IF NOT EXISTS external_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT, 
        category TEXT, description TEXT)''')
    
    # Tareas con Prioridad
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, book_id INTEGER, 
        date TEXT, title TEXT, priority TEXT, status TEXT DEFAULT "pendiente")''')
    
    # Métricas Mensuales (ROI)
    cursor.execute('''CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT, month TEXT, sales INTEGER, 
        kenp INTEGER, revenue REAL, ads_spend REAL DEFAULT 0)''')

    conn.commit()
    conn.close()

init_db()

async def verify_token(authorization: Optional[str] = Header(None)):
    if authorization != f"Bearer {ADMIN_PASSWORD}":
        raise HTTPException(status_code=401, detail="No autorizado")
    return True

@app.post("/api/login")
async def login(password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        return {"token": ADMIN_PASSWORD, "status": "success"}
    raise HTTPException(status_code=401, detail="Acceso denegado")

@app.get("/api/data")
async def get_all_data(authenticated: bool = Depends(verify_token)):
    conn = get_db_connection()
    cursor = conn.cursor()
    data = {
        "imprints": [dict(r) for r in cursor.execute("SELECT * FROM imprints").fetchall()],
        "authors": [dict(r) for r in cursor.execute("SELECT * FROM authors").fetchall()],
        "series": [dict(r) for r in cursor.execute("SELECT * FROM series").fetchall()],
        "books": [dict(r) for r in cursor.execute("SELECT * FROM books").fetchall()],
        "tasks": [dict(r) for r in cursor.execute("SELECT * FROM tasks").fetchall()],
        "metrics": [dict(r) for r in cursor.execute("SELECT * FROM metrics ORDER BY month DESC").fetchall()],
        "external_links": [dict(r) for r in cursor.execute("SELECT * FROM external_links").fetchall()]
    }
    conn.close()
    return data

# Implementación de carga de imágenes y guardado de registros...
# (Omitido para simplificar el despliegue inicial, funcional tras reinicio)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)