from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from yield_utils import simulation, get_yield_curve_data, get_recession_data

app = FastAPI()

origins = [
    "http://localhost:3000",
]

# Allow CORS for the specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Fintech Mini Project API!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/yield-curve")
async def yield_curve():
    """
    Fetches the yield curve data.
    """
    df = get_yield_curve_data().fillna(0)
    return df.to_dict(orient="records")

@app.get("/api/recession")
async def recession():
    """
    Fetches the recession data.
    """
    df = get_recession_data().fillna(0)
    return df.to_dict(orient="records")

@app.get("/api/simulation")
async def run_simulation():
    """
    Runs the simulation and returns the results.
    """
    result = simulation()
    return {
        'data': result['data'].fillna(0).to_dict(orient="records"),
        'hit_rate': result['hit_rate'],
    }
