from database import engine, Base
from models import User, Flight, Passenger, Reservation

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")