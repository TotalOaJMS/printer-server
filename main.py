from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

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
    print("데이터 수신:", data)
    return {"status": "ok"}