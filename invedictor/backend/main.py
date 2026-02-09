from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import prediction_engine

app = FastAPI()

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# Serve static files
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# -- Data Models --
class SalesRecord(BaseModel):
    date: str
    quantity: int

class PredictionRequest(BaseModel):
    productId: str
    currentStock: int
    safetyStock: int
    salesHistory: List[SalesRecord]

class PredictionResponse(BaseModel):
    productId: str
    predictedMonthlyDemand: int
    averageDailySales: float
    trend: str
    reorderQuantity: int
    riskLevel: str

# -- Endpoints --

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def read_root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"Backend running, frontend not found at {index_path}"}

@app.post("/predict", response_model=PredictionResponse)
def predict_demand_endpoint(data: PredictionRequest):
    try:
        # Convert Pydantic models to list of dicts for the engine
        sales_data = [{"date": r.date, "quantity": r.quantity} for r in data.salesHistory]
        
        result = prediction_engine.predict_demand(
            sales_data, 
            data.currentStock, 
            data.safetyStock
        )
        
        return PredictionResponse(
            productId=data.productId,
            predictedMonthlyDemand=result['predicted_monthly_demand'],
            averageDailySales=result['average_daily_sales'],
            trend=result['trend'],
            reorderQuantity=result['reorder_quantity'],
            riskLevel=result['risk_level']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
