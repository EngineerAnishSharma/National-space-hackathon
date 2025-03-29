# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.api import placement, search, waste, simulate, logs, import_export
from app.api import import_export
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(placement.router)
# app.include_router(search.router)
# app.include_router(waste.router)
# app.include_router(simulate.router)
app.include_router(import_export.router)
# app.include_router(logs.router)

@app.get("/")
async def root():
    return {"message": "ISS Cargo Management API"}