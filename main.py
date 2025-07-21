from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, firestore, initialize_app
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os

# Load env vars
load_dotenv()

# initialize app
app = FastAPI()

# Allow CORS for both local + production frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase setup
FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH", "firebase_key.json")

cred = credentials.Certificate(FIREBASE_KEY_PATH)
initialize_app(cred)
db = firestore.client()

# Model
class Order(BaseModel):
    customerName: str
    product: str
    quantity: int
    price: float
    status: str

# Routes
@app.get("/orders")
async def get_orders():
    try:
        orders_ref = db.collection("Orders")
        docs = orders_ref.stream()
        orders = []
        for doc in docs:
            order_data = doc.to_dict()
            order_data["id"] = doc.id
            orders.append(order_data)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orders")
async def add_order(order: Order):
    try:
        order_dict = order.dict()
        doc_ref = db.collection("Orders").add(order_dict)
        order_dict["id"] = doc_ref[1].id
        return order_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
