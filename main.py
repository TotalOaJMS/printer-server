from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

def save_to_db(data):
    DATABASE_URL = os.environ.get("DATABASE_URL")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS printer_data (
            id SERIAL PRIMARY KEY,
            device_ip TEXT,
            total INT,
            toner_cyan INT,
            toner_magenta INT,
            toner_yellow INT,
            toner_black INT,
            waste_toner INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        INSERT INTO printer_data 
        (device_ip, total, toner_cyan, toner_magenta, toner_yellow, toner_black, waste_toner)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        data.device_ip,
        data.total,
        data.toner_cyan,
        data.toner_magenta,
        data.toner_yellow,
        data.toner_black,
        data.waste_toner
    ))

    conn.commit()
    cur.close()
    conn.close()
    
class PrinterData(BaseModel):
    device_ip: str
    total: int
    toner_cyan: int
    toner_magenta: int
    toner_yellow: int
    toner_black: int
    waste_toner: int

@app.get("/")
def root():
    return {"status": "server running"}

@app.post("/api/printer")
def receive(data: PrinterData):
    save_to_db(data)
    print("데이터 저장:", data)
    return {"status": "saved"}

@app.get("/test-db")
def test_db():
    import psycopg2
    import os
    
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("SELECT * FROM printer_data ORDER BY id DESC LIMIT 5")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return {"data": rows}

@app.get("/api/printers")
def get_printers():
    import psycopg2
    import os

    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT ON (device_ip)
            device_ip,
            total,
            toner_cyan,
            toner_magenta,
            toner_yellow,
            toner_black,
            waste_toner,
            created_at
        FROM printer_data
        ORDER BY device_ip, created_at DESC
    """)

    rows = cur.fetchall()

    result = []
    for r in rows:
        result.append({
            "device_ip": r[0],
            "total": r[1],
            "toner_cyan": r[2],
            "toner_magenta": r[3],
            "toner_yellow": r[4],
            "toner_black": r[5],
            "waste_toner": r[6],
            "updated_at": str(r[7])
        })

    cur.close()
    conn.close()

    return {"printers": result}
