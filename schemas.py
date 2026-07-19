from pydantic import BaseModel

# Yeh schema check karega ke user ne name, email aur password sahi diya hai
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    # Yeh schema menu item ka data validate karega
class MenuCreate(BaseModel):
    item_name: str
    price: float
    description: str
    # Yeh schema chat message receive karne ke liye hai
class ChatRequest(BaseModel):
    message: str
    # --- NAYA CODE: Order Create karne ke liye Data Validation Schema ---
class OrderCreate(BaseModel):
    user_id: int
    item_id: int
    quantity: int
    # --- NAYA CODE: Table Reservation ke liye Data Validation Schema ---
class ReservationCreate(BaseModel):
    user_id: int
    party_size: int
    reservation_date: str
    reservation_time: str