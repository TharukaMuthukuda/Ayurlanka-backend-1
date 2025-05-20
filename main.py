from fastapi import FastAPI, HTTPException,Request, Depends, status
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from typing import Optional, List
import pickle
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os 
import uuid

app = FastAPI(  
    title="AyurLanka Admin",
    description="This is the backend dashboard for AyurLanka Admin. This handles product management, practitioner management, and supplier inquiries.",
    version="1.0.6",
    docs_url="/admin",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

print("💣 CORS enabled. Backend ready to talk to the frontend homie.")


with open("model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

with open("vectorizer.pkl", "rb") as vec_file:
    vectorizer = pickle.load(vec_file)

print("💣 Model & Vectorizer loaded. Locked and loaded homie.")

# Firebase Admin SDK

cred_path = os.environ.get('FIREBASE_ADMIN_SDK_KEY_PATH', 'ayurlanka-2bd6e-firebase-adminsdk-fbsvc-e897ac6ff3.json')

try:
    cred = credentials.Certificate(cred_path)

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://ayurlanka-2bd6e-default-rtdb.asia-southeast1.firebasedatabase.app'
    })
    print("Firebase Admin SDK initialized successfully!")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")




# --- PRODUCTS ---
# products = [
#     {"id": 1, "name": "Ayurvedic Oil", "price": 1200},
#     {"id": 2, "name": "Herbal Tea", "price": 800},
#     { "id": 3, "name": "Neem Capsules", "price": 950 }, 
#     { "id": 4, "name": "Turmeric Face Mask", "price": 1100 }, 
#     { "id": 5, "name": "Ashwagandha Powder", "price": 1350 }, 
#     { "id": 6, "name": "Aloe Vera Gel", "price": 700 }
# ]

class Product(BaseModel):
    id: int
    name: str
    price: int
    category: int
    imgPath: str
    description: str

@app.post("/add-product")
def add_product(product: Product):
    try:
        ref = db.reference('/products')
        all_products = ref.get()
        
        if all_products:
            max_id = max([data.get("id", 0) for data in all_products.values()])
        else:
            max_id = 0

        product.id = max_id + 1
        new_product = ref.push(product.model_dump())
        return {"message": "Product added homie 🛒", "key": new_product.key}
    except Exception as e:
        return {"message": f"Error adding product: {e}", "status": "error"}, 500


@app.get("/products")
def get_products():
    try:
        ref = db.reference('/products')
        snapshot = ref.get()
        if snapshot is None:
            return []
        return [Product(**data) for _, data in snapshot.items()]
    except Exception as e:
        return {"message": f"Error getting products: {e}", "status": "error"}, 500

@app.delete("/delete-product/{product_id}")
def delete_product(product_id: int):
    try:
        ref = db.reference('/products')
        all_data = ref.get()
        if not all_data:
            raise HTTPException(status_code=404, detail="No products found.")
        for key, val in all_data.items():
            if val["id"] == product_id:
                ref.child(key).delete()
                return {"message": "Product deleted 💀"}
        raise HTTPException(status_code=404, detail="Product not found.")
    except Exception as e:
        return {"message": f"Error deleting product: {e}", "status": "error"}, 500
    
# --- ORDERS ---

class OrderedProduct(BaseModel):
    name: str
    price: int
    quantity: int
    total: int
    imgPath: str

class Order(BaseModel):
    order_id: Optional[str]
    customer_name: str
    telephone_1: str
    telephone_2: str
    address: str
    order_summary: List[OrderedProduct]

@app.get("/orders", response_model=List[Order])
def get_orders():
    try:
        ref = db.reference('/orders')
        snapshot = ref.get()
        if not snapshot:
            return []
        return [Order(**order) for order in snapshot.values()]
    except Exception as e:
        return {"message": f"Error fetching orders: {e}", "status": "error"}, 500

@app.post("/add-order")
def add_order(order: Order):
    try:
        ref = db.reference('/orders')
        order_id = str(uuid.uuid4())
        order_dict = order.model_dump()
        order_dict["order_id"] = order_id
        new_order = ref.push(order_dict)
        return {"message": "Order placed homie 📦", "key": new_order.key, "order_id": order_id}
    except Exception as e:
        return {"message": f"Error placing order: {e}", "status": "error"}, 500
    
# --- PRACTITIONERS ---
practitioners = [
    {"id": 1, "name": "Dr. Nimal", "contact": "0771234567"},
    {"id": 2, "name": "Dr. Kavindi", "contact": "0767654321"}
]
class Practitioner(BaseModel):
    id: Optional[int] = None  # 🧠 Make ID optional so we assign it manually
    name: str
    contact: str
    specialities: str

@app.post("/add-practitioner")
def add_practitioner(doc: Practitioner):
    try:
        ref = db.reference('/practitioners')
        all_data = ref.get() or {}

        # 🔢 Calculate next ID
        existing_ids = [val.get("id", 0) for val in all_data.values()]
        next_id = max(existing_ids, default=0) + 1
        doc.id = next_id  # set it homie

        new_doc = ref.push(doc.model_dump())
        return {"message": "Practitioner added homie 🧠", "key": new_doc.key}
    except Exception as e:
        return {"message": f"Error adding practitioner: {e}", "status": "error"}, 500


@app.get("/practitioners")
def get_practitioners():
    try:
        ref = db.reference('/practitioners')
        snapshot = ref.get()
        if snapshot is None:
            return []
        return [Practitioner(**data) for _, data in snapshot.items()]
    except Exception as e:
        return {"message": f"Error getting practitioners: {e}", "status": "error"}, 500

@app.delete("/delete-practitioner/{practitioner_id}")
def delete_practitioner(practitioner_id: int):
    try:
        ref = db.reference('/practitioners')
        all_data = ref.get()
        if not all_data:
            raise HTTPException(status_code=404, detail="No practitioners found.")
        for key, val in all_data.items():
            if val["id"] == practitioner_id:
                ref.child(key).delete()
                return {"message": "Practitioner deleted 🔪"}
        raise HTTPException(status_code=404, detail="Practitioner not found.")
    except Exception as e:
        return {"message": f"Error deleting practitioner: {e}", "status": "error"}, 500

# --- SUPPLIER FORM ---
class SupplierForm(BaseModel):
    name: str
    telephone: str
    inquiry: Optional[str] = None

@app.post("/submit-supplier")
def submit_supplier(data: SupplierForm):
    try:
        # Get a reference to the 'suppliers' node
        suppliers_ref = db.reference('/suppliers')

        # Use .push() to add the new supplier data with a unique key
        # model_dump() converts the Pydantic model to a dictionary
        new_supplier_ref = suppliers_ref.push(data.model_dump())

        print(f"Supplier form submitted and saved to Firebase: {data.name} - {data.telephone} - {data.inquiry}")
        print(f"Saved with key: {new_supplier_ref.key}")

        return {"message": "Supplier info received and saved to database 🧾", "database_key": new_supplier_ref.key}

    except Exception as e:
        print(f"Error saving supplier to Firebase: {e}")
        # Return an error response
        return {"message": f"Error saving supplier: {e}", "status": "error"}, 500 # Or use FastAPI's HTTPException


@app.get("/suppliers")
def get_suppliers():
    try:
        # Get a reference to the 'suppliers' node
        suppliers_ref = db.reference('/suppliers')

        # Get all the data under the 'suppliers' node
        # This returns a dictionary where keys are the push IDs
        snapshot = suppliers_ref.get()

        # If snapshot is None, there's no data
        if snapshot is None:
            return []

        # Convert the dictionary of suppliers into a list of SupplierForm objects
        # The snapshot data is a dictionary {key1: {data1}, key2: {data2}, ...}
        # We want a list of the {data} parts
        supplier_list = [SupplierForm(**data) for key, data in snapshot.items()]

        print(f"Retrieved {len(supplier_list)} suppliers from Firebase.")

        return supplier_list

    except Exception as e:
        print(f"Error retrieving suppliers from Firebase: {e}")
        # Return an error response
        return {"message": f"Error retrieving suppliers: {e}", "status": "error"}, 500 # Or use FastAPI's HTTPException

# --- USER FORM ---
class UserForm(BaseModel):
    name: str
    email: str
    message: Optional[str] = None

@app.post("/submit-form")
def submit_form(data: UserForm):
    print(f"Form from {data.name}: {data.message}")
    return {"message": "Form received homie 🎯"}

# --- FEEDBACK ---
class Feedback(BaseModel):
    feedback: str

@app.post("/predict")
def predict(data: Feedback):
    vect = vectorizer.transform([data.feedback])
    pred = model.predict(vect)[0]
    return {"result": pred}
