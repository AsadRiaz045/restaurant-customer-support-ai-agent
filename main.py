import json 
import os
chat_memory = []
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, Depends,Request
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal

# .env file load karne ke liye
load_dotenv()

# FastAPI app initialize kar rahe hain
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app ko allow karne ke liye
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq Client Setup (Sirf ek dafa yahan define hoga)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Database se connect hone ka function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Hamari Pehli API - User Signup
@app.post("/signup/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(name=user.name, email=user.email, password=user.password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Zabardast! Naya user successfully save ho gaya.", "user_name": new_user.name}

# Menu Item Add Karne Ki API
@app.post("/menu/")
def create_menu_item(item: schemas.MenuCreate, db: Session = Depends(get_db)):
    new_item = models.Menu(item_name=item.item_name, price=item.price, description=item.description)
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return {"message": "Zabardast! Nayi dish menu mein add ho gayi.", "item_name": new_item.item_name}


# Chatbot API


# Chatbot API (Updated with AI Function Calling)
# Chatbot API (Updated with AI Function Calling and Strict Integer Rules)
# Chatbot API (Updated for English, COD Logic, and Loop Prevention)
@app.post("/chat/")
async def chat_with_bot(request: Request):
    data = await request.json()
    user_message = data.get("message")

    # 1. Sab se PEHLE memory ko limit karein
    global chat_memory
    if len(chat_memory) > 6:
        chat_memory = chat_memory[-6:]

    # 2. Phir user ka naya message memory mein save karein
    chat_memory.append({"role": "user", "content": user_message})
    today_date = date.today()
    menu_text = "1. Zinger Burger (Rs 500), 2. Chicken Tikka Pizza (Rs 1200), 3. Fries (Rs 300), 4. Cold Drink (Rs 150)"
    
    system_prompt = f"""
        You are a polite and helpful customer service chatbot for Monal Restaurant Lahore. Today's date is {today_date}.
        Menu: {menu_text}
        
        GREETING BEHAVIOR:
        When a user says "hi", "hello", or greets you, DO NOT show the menu, timings, or location. 
        You MUST ONLY reply exactly with this short message: 
        "Welcome to Monal Restaurant Lahore! What would you like to order? Should I share the menu?"
        
        IMPORTANT INSTRUCTION FOR ORDERS:
        Before using the 'place_order' tool, you MUST politely ask the customer for these 3 details:
        1. Full Name
        2. Phone Number
        3. Delivery Address
        
        CRITICAL RULES FOR CONVERSATION AND TOOLS:
        - NEVER ask the customer for their User ID. Customers do not know their IDs. You must silently and automatically use the integer 1 for the 'user_id' parameter in the background.
        - ALWAYS respond in clear and professional English. DO NOT use Roman Urdu.
        - If the customer has NOT provided the 3 details (Name, Phone, Address) yet, ONLY reply with normal conversational text.
        - ABSOLUTELY DO NOT output any JSON or function tags (like <function=place_order>) in your chat message.
        - CRITICAL: Once an order is placed, do NOT call the 'place_order' tool again if the user simply says "thanks", "ok", or confirms payment.
        - When calling tools, parameters MUST be integers (e.g., use 1, not "1").
        
        PAYMENT AND CLOSING (COD RULE):
        - We accept Cash on Delivery (COD). 
        - If the user agrees to Cash on Delivery or asks about the bill payment, you MUST reply with: 
          "Your payment preference has been saved. The bill will be collected via Cash on Delivery. Thank you so much for your order! Let me know if there is anything else I can assist you with."
    """
    
    # 3. AI ko bhejne ke liye messages
    messages_to_send = [{"role": "system", "content": system_prompt}]
    messages_to_send.extend(chat_memory)
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "place_order",
                "description": "Customer ka order place karne ke liye.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "integer"},
                        "item_id": {"type": "integer", "description": "Menu se dish ki ID"},
                        "quantity": {"type": "integer"}
                    },
                    "required": ["user_id", "item_id", "quantity"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "book_table",
                "description": "Table reserve karne ke liye.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "integer"},
                        "party_size": {"type": "integer"},
                        "reservation_date": {"type": "string"},
                        "reservation_time": {"type": "string"}
                    },
                    "required": ["user_id", "party_size", "reservation_date", "reservation_time"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "cancel_order",
                "description": "Customer ka pending order cancel karne ke liye.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "integer"},
                        "item_id": {"type": "integer"}
                    },
                    "required": ["user_id", "item_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "modify_order",
                "description": "Customer ke order ki quantity update karne ke liye.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "integer"},
                        "item_id": {"type": "integer"},
                        "new_quantity": {"type": "integer"}
                    },
                    "required": ["user_id", "item_id", "new_quantity"]
                }
            }
        }
    ]

    chat_completion = groq_client.chat.completions.create(
        messages=messages_to_send,
        model="llama-3.1-8b-instant",
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = chat_completion.choices[0].message
    reply_text = ""
    
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            
            db = SessionLocal()
            try:
                if tool_call.function.name == "place_order":
                    item = db.query(models.Menu).filter(models.Menu.id == int(args["item_id"])).first()
                    if not item: 
                        reply_text = "I'm sorry, but this dish is not available on the menu."
                    else:
                        new_order = models.Order(user_id=int(args["user_id"]), item_id=int(args["item_id"]), quantity=int(args["quantity"]), status="Pending")
                        db.add(new_order)
                        db.commit()
                        # YAHAN ENGLISH AUR FOLLOW-UP QUESTION ADD KIYA HAI:
                        reply_text = f"Your order for {args['quantity']} '{item.item_name}' has been successfully placed! The total bill is Rs {item.price * int(args['quantity'])}. Would you like to order anything else?"
                
                elif tool_call.function.name == "book_table":
                    new_reservation = models.Reservation(user_id=int(args["user_id"]), party_size=int(args["party_size"]), reservation_date=args["reservation_date"], reservation_time=args["reservation_time"], status="Confirmed")
                    db.add(new_reservation)
                    db.commit()
                    reply_text = f"Your table for {args['party_size']} people on {args['reservation_date']} at {args['reservation_time']} has been confirmed."
                    
                elif tool_call.function.name == "cancel_order":
                    order_to_cancel = db.query(models.Order).filter(models.Order.user_id == int(args["user_id"]), models.Order.item_id == int(args["item_id"]), models.Order.status == "Pending").first()
                    if not order_to_cancel: 
                        reply_text = "I'm sorry, I couldn't find any pending order to cancel."
                    else:
                        order_to_cancel.status = "Cancelled"
                        db.commit()
                        item = db.query(models.Menu).filter(models.Menu.id == int(args["item_id"])).first()
                        reply_text = f"Alright, your order for '{item.item_name}' has been cancelled."
                        
                elif tool_call.function.name == "modify_order":
                    order_to_modify = db.query(models.Order).filter(models.Order.user_id == int(args["user_id"]), models.Order.item_id == int(args["item_id"]), models.Order.status == "Pending").first()
                    if not order_to_modify: 
                        reply_text = "I'm sorry, I couldn't find any pending order to update."
                    else:
                        order_to_modify.quantity = int(args["new_quantity"])
                        db.commit()
                        item = db.query(models.Menu).filter(models.Menu.id == int(args["item_id"])).first()
                        reply_text = f"Your order for '{item.item_name}' has been updated. The new quantity is {args['new_quantity']}."
            finally:
                db.close()
    else:
        reply_text = response_message.content

    # 4. Memory ko Update karna
    chat_memory.append({"role": "assistant", "content": reply_text})
    
    # 5. Memory ko limit mein rakhna
    if len(chat_memory) > 10:
        chat_memory = chat_memory[-10:]
        
    return {"reply": reply_text}
    
    # 5. Memory ko limit mein rakhna
    if len(chat_memory) > 10:
        chat_memory = chat_memory[-10:]
        
    return {"reply": reply_text}
    # 3. Memory ko limit mein rakhna taake payload zyada bada na ho (Pichli 10 baatein yaad rakhega)
    if len(chat_memory) > 10:
        chat_memory = chat_memory[-10:]
        
    return {"reply": reply_text}
@app.post("/order/")
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # 1. Check karein ke User exist karta hai ya nahi
    user = db.query(models.User).filter(models.User.id == order.user_id).first()
    if not user:
        return {"error": "User nahi mila! Pehle signup karein."}

    # 2. Check karein ke Menu Item exist karta hai ya nahi
    item = db.query(models.Menu).filter(models.Menu.id == order.item_id).first()
    if not item:
        return {"error": "Menu item database mein nahi mila!"}

    # 3. Naya Order Database mein save karein
    new_order = models.Order(
        user_id=order.user_id,
        item_id=order.item_id,
        quantity=order.quantity,
        status="Pending"
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # 4. Total Bill Calculate karein
    total_bill = item.price * order.quantity
    
    return {
        "message": "Zabardast! Aap ka order place ho gaya hai.",
        "order_id": new_order.id,
        "item_ordered": item.item_name,
        "quantity": order.quantity,
        "total_bill_rs": total_bill,
        "status": new_order.status
    }
# --- NAYA CODE: Table Reservation Ki API ---
@app.post("/reservation/")
def create_reservation(res: schemas.ReservationCreate, db: Session = Depends(get_db)):
    # Check karein ke kya User exist karta hai?
    user = db.query(models.User).filter(models.User.id == res.user_id).first()
    if not user:
        return {"error": "User nahi mila! Pehle signup karein."}

    # Nayi reservation database mein save karein
    new_reservation = models.Reservation(
        user_id=res.user_id,
        party_size=res.party_size,
        reservation_date=res.reservation_date,
        reservation_time=res.reservation_time,
        status="Confirmed"
    )
    
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    
    return {
        "message": f"Zabardast! Aap ki table {res.party_size} logon ke liye {res.reservation_date} ko {res.reservation_time} baje confirm ho gayi hai.",
        "reservation_id": new_reservation.id,
        "status": new_reservation.status
    }