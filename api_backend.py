# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, Form, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
from typing import Optional

app = FastAPI(title="Atreyu Editorial API")

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

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS imprints (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, lang TEXT, color TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS authors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, bio TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS series (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, author_id INTEGER)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author_id INTEGER, imprint_id INTEGER, 
        status TEXT, ku BOOLEAN DEFAULT 0, prod_cost_cover REAL DEFAULT 0, 
        prod_cost_trans REAL DEFAULT 0, prod_cost_edit REAL DEFAULT 0)''')
    cursor.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, date TEXT, priority TEXT, status TEXT DEFAULT "pendiente")')
    cursor.execute('CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, month TEXT, revenue REAL DEFAULT 0, ads_spend REAL DEFAULT 0)')
    conn.commit()
    conn.close()

async def verify_token(authorization: Optional[str] = Header(None)):
    if authorization != f"Bearer {ADMIN_PASSWORD}":
        raise HTTPException(status_code=401)
    return True

@app.post("/api/login")
async def login(password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        return {"token": ADMIN_PASSWORD}
    raise HTTPException(status_code=401)

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
        "metrics": [dict(r) for r in cursor.execute("SELECT * FROM metrics").fetchall()]
    }
    conn.close()
    return data
