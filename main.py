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
