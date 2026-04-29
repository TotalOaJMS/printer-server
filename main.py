from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os
import psycopg2
import os

def reset_table():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS printer_data;")

    conn.commit()
    cur.close()
    conn.close()
    
app = FastAPI()

reset_table()

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

            drum_cyan INT,
            drum_magenta INT,
            drum_yellow INT,
            drum_black INT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
            INSERT INTO printer_data
            (device_ip, total, toner_cyan, toner_magenta, toner_yellow, toner_black, waste_toner, drum_cyan, drum_magenta, drum_yellow, drum_black)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data.device_ip,
        data.total,
        data.toner_cyan,
        data.toner_magenta,
        data.toner_yellow,
        data.toner_black,
        data.waste_toner

        data.drum_cyan,
        data.drum_magenta,
        data.drum_yellow,
        data.drum_black
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

from fastapi.responses import HTMLResponse

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
    <head>
        <title>프린터 관리</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background-color: #333; color: white; }
        </style>
    </head>
    <body>
        <h2>프린터 상태</h2>
        <table id="table">
            <tr>
                <th>IP</th>
                <th>총 카운터</th>
                <th>검정</th>
                <th>청록</th>
                <th>자홍</th>
                <th>노랑</th>
                <th>폐토너</th>
                <th>업데이트</th>
            </tr>
        </table>

        <script>
            fetch('/api/printers')
                .then(res => res.json())
                .then(data => {
                    const table = document.getElementById("table");

                    data.printers.forEach(p => {
                        const row = table.insertRow();

                        row.insertCell().innerText = p.device_ip;
                        row.insertCell().innerText = p.total;
                        let black = p.toner_black;
                            let cell = row.insertCell();
                                cell.innerText = black + "%";
                                    if (black < 20) {cell.style.color = "red";}
                        row.insertCell().innerText = p.toner_cyan + "%";
                        row.insertCell().innerText = p.toner_magenta + "%";
                        row.insertCell().innerText = p.toner_yellow + "%";
                        let waste = p.waste_toner;
                            let wcell = row.insertCell();
                                if (waste == 1) {wcell.innerText = "교체 필요"; wcell.style.color = "red";} 
                                    else {wcell.innerText = "정상";}
                        let date = new Date(p.updated_at);
                            // 한국시간으로 변환 (+9시간)
                            date.setHours(date.getHours() + 9);
                                row.insertCell().innerText = date.toLocaleString('ko-KR', { hour12: false });
                    });
                });
        </script>
        <script>
            setInterval(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    """
    
