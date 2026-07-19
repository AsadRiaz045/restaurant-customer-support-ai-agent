from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy import Column, Integer, String
from database import Base, engine

# Yeh hamari pehli table hai User ke data ke liye
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    # Customer ki Table Reservations
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # User ke sath connection
    party_size = Column(Integer)                      # Kitne log aayenge
    reservation_date = Column(String)                 # Maslan "2026-07-20"
    reservation_time = Column(String)                 # Maslan "20:00"
    status = Column(String, default="Confirmed")      # Status

# Yeh command database mein is table ko actually create kar degi
Base.metadata.create_all(bind=engine)
from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import relationship

# Restaurant ki Menu Table
class Menu(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)

# Customer ke Orders ki Table
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # User ka connection
    item_id = Column(Integer, ForeignKey("menu.id"))  # Menu item ka connection
    quantity = Column(Integer)
    status = Column(String, default="Pending")        # Order ki status (Pending, Delivered)

# Yeh lazmi check karein ke sab se aakhir mein yeh line likhi ho:
Base.metadata.create_all(bind=engine)