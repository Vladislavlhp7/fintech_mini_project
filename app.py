from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

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
