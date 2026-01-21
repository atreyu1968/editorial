# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, Form, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI(title="Atreyu Editorial Pro API")

ADMIN_PASSWORD = "697457"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = "/opt/atreyu"
DB_PATH = os.path.join(BASE_DIR, "editorial.db")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Helpers de Base de Datos
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # Tablas de alta fidelidad
    cursor.execute('CREATE TABLE IF NOT EXISTS imprints (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, lang TEXT, color TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS authors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, bio TEXT, drive_url TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS series (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, author_id INTEGER, drive_url TEXT)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author_id INTEGER, imprint_id INTEGER, series_id INTEGER,
        status TEXT, ku BOOLEAN DEFAULT 0, prod_cost_cover REAL DEFAULT 0, prod_cost_trans REAL DEFAULT 0, 
        prod_cost_edit REAL DEFAULT 0, drive_url TEXT, amazon_url TEXT, keywords TEXT, categories TEXT)''')
    cursor.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, date TEXT, priority TEXT, status TEXT DEFAULT "pendiente")')
    cursor.execute('CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, month TEXT, revenue REAL DEFAULT 0, ads_spend REAL DEFAULT 0)')
    conn.commit()
    conn.close()

# Seguridad
async def verify_token(authorization: Optional[str] = Header(None)):
    if authorization != f"Bearer {ADMIN_PASSWORD}":
        raise HTTPException(status_code=401, detail="No autorizado")
    return True

@app.post("/api/login")
async def login(password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        return {"token": ADMIN_PASSWORD}
    raise HTTPException(status_code=401)

# LECTURA DE DATOS
@app.get("/api/data")
async def get_data(authenticated: bool = Depends(verify_token)):
    conn = get_db()
    cursor = conn.cursor()
    data = {
        "imprints": [dict(r) for r in cursor.execute("SELECT * FROM imprints").fetchall()],
        "authors": [dict(r) for r in cursor.execute("SELECT * FROM authors").fetchall()],
        "series": [dict(r) for r in cursor.execute("SELECT * FROM series").fetchall()],
        "books": [dict(r) for r in cursor.execute("SELECT * FROM books").fetchall()],
        "tasks": [dict(r) for r in cursor.execute("SELECT * FROM tasks").fetchall()],
        "metrics": [dict(r) for r in cursor.execute("SELECT * FROM metrics ORDER BY month DESC").fetchall()]
    }
    conn.close()
    return data

# ESCRITURA DE DATOS (AÑADIR TAREA EJEMPLO)
@app.post("/api/add_task")
async def add_task(title: str = Form(...), date: str = Form(...), priority: str = Form(...), auth: bool = Depends(verify_token)):
    conn = get_db()
    conn.execute('INSERT INTO tasks (title, date, priority) VALUES (?, ?, ?)', (title, date, priority))
    conn.commit()
    conn.close()
    return {"status": "success"}

# ESCRITURA DE DATOS (AÑADIR LIBRO EJEMPLO)
@app.post("/api/add_book")
async def add_book(title: str = Form(...), author_id: int = Form(...), status: str = Form(...), auth: bool = Depends(verify_token)):
    conn = get_db()
    conn.execute('INSERT INTO books (title, author_id, status) VALUES (?, ?, ?)', (title, author_id, status))
    conn.commit()
    conn.close()
    return {"status": "success"}

# ELIMINACIÓN DE DATOS
@app.delete("/api/delete/{table}/{id}")
async def delete_item(table: str, id: int, auth: bool = Depends(verify_token)):
    allowed_tables = ["books", "authors", "tasks", "series", "imprints"]
    if table not in allowed_tables: raise HTTPException(status_code=400)
    conn = get_db()
    conn.execute(f'DELETE FROM {table} WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}
