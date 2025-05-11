from contextlib import asynccontextmanager
from typing import List, Annotated
from datetime import datetime
import hashlib
import secrets

from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, engine
from db_init import init_db

from datetime import datetime, timedelta
import hashlib
import secrets
import binascii
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = "your-secret-key-here"  # Change this to a strong random key in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    init_db()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
credentials_dependency = Annotated[HTTPBasicCredentials, Depends(security)]

# Authentication Utilities
def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Secure password hashing using PBKDF2-HMAC-SHA256"""
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        10  # Number of iterations
    )
    hashed = binascii.hexlify(dk).decode()
    return hashed, salt

def verify_password(plain_password: str, hashed_password: str, salt: str) -> bool:
    """Verify password against stored hash"""
    new_hash, _ = hash_password(plain_password, salt)
    return secrets.compare_digest(new_hash, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user by username/email and password"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        user = db.query(models.User).filter(models.User.email == username).first()
        if not user:
            return None
    
    if not user.verify_password(password):
        return None
    return user

def get_current_user(
    db: db_dependency,
    credentials: credentials_dependency
):
    """Dependency to get current authenticated user"""
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

current_user_dependency = Annotated[models.User, Depends(get_current_user)]

# Authentication Endpoints

# endpoint for token verification
@app.get("/verify-token")
async def verify_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Updated /token endpoint to include username
@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            # "is_admin": user.is_admin
        },
        expires_delta=access_token_expires
    )
    
    return {  # Include username in response
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        # "is_admin": user.is_admin 
    }

# @app.post("/make-me-admin")
# def make_me_admin(
#     username: str = "Ebrahem",  # Hardcode your test username
#     db: Session = Depends(get_db)
# ):
#     user = db.query(models.User).filter(models.User.username == username).first()
#     if not user:
#         return {"error": "User not found"}
    
#     user.is_admin = True
#     db.commit()
#     return {"message": f"{username} is now an admin"}

@app.post("/register/", response_model=schemas.UserPublic)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print("\n=== Registration Attempt ===")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    
    try:
        # Check for existing username
        existing_user = db.query(models.User).filter(
            models.User.username == user.username
        ).first()
        if existing_user:
            print("❌ Username already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check for existing email
        existing_email = db.query(models.User).filter(
            models.User.email == user.email
        ).first()
        if existing_email:
            print("❌ Email already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user - let the model handle password hashing
        print("Creating new user...")
        db_user = models.User(
            username=user.username,
            email=user.email,
            password=user.password  # Plain password
        )
        
        db.add(db_user)
        db.flush()  # Test if we can persist without full commit
        print("User flushed successfully")
        
        db.commit()
        print("✅ User committed to database")
        db.refresh(db_user)
        
        # Verify what was actually stored
        stored_user = db.query(models.User).filter(
            models.User.username == user.username
        ).first()
        print("Stored user details:")
        print(f"Username: {stored_user.username}")
        print(f"Email: {stored_user.email}")
        print(f"Salt: {stored_user.salt}")
        print(f"Password hash: {stored_user.hashed_password}")
        
        return db_user
        
    except Exception as e:
        db.rollback()
        print(f"❌ Registration failed: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# User Endpoints
@app.get("/users/me/", response_model=schemas.UserPublic)
def read_current_user(current_user: current_user_dependency):
    """Get current user details"""
    return current_user

# Flight Endpoints
@app.post("/flights/", response_model=schemas.FlightPublic)
def create_flight(
    db: db_dependency,
    current_user: current_user_dependency,
    flight: schemas.FlightCreate
):
    """Create a new flight"""
    db_flight = models.Flight(**flight.model_dump(), user_id=current_user.id)
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight

@app.get("/flights/", response_model=List[schemas.FlightPublic])
def read_flights(
    db: db_dependency,
    skip: int = 0,
    limit: int = 100,
    departure_code: str = None,
    destination_code: str = None,
    departure_date: datetime = None
):
    """Get list of flights with optional filters"""
    query = db.query(models.Flight)
    
    if departure_code:
        query = query.filter(models.Flight.departure_code == departure_code)
    if destination_code:
        query = query.filter(models.Flight.destination_code == destination_code)
    if departure_date:
        query = query.filter(models.Flight.departure_time >= departure_date)
    
    flights = query.offset(skip).limit(limit).all()
    return flights

# Passenger Endpoints
@app.post("/passengers/", response_model=schemas.PassengerPublic)
def create_passenger(
    db: db_dependency,
    passenger: schemas.PassengerCreate
):
    """Create a new passenger"""
    db_passenger = models.Passenger(**passenger.model_dump())
    db.add(db_passenger)
    db.commit()
    db.refresh(db_passenger)
    return db_passenger

@app.get("/passengers/", response_model=List[schemas.PassengerPublic])
def read_passengers(
    db: db_dependency,
    skip: int = 0,
    limit: int = 100
):
    """Get list of passengers"""
    passengers = db.query(models.Passenger).offset(skip).limit(limit).all()
    return passengers

# Reservation Endpoints
@app.post("/reservations/", response_model=schemas.ReservationPublic)
def create_reservation(
    db: db_dependency,
    current_user: current_user_dependency,
    reservation: schemas.ReservationCreate
):
    """Create a new reservation"""
    # Check if flight exists
    db_flight = db.query(models.Flight).filter(
        models.Flight.id == reservation.flight_id
    ).first()
    if not db_flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    # Check if passenger exists
    db_passenger = db.query(models.Passenger).filter(
        models.Passenger.id == reservation.passenger_id
    ).first()
    if not db_passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")
    
    # Check seat availability
    seat = db.query(models.Seat).filter(
        models.Seat.flight_id == reservation.flight_id,
        models.Seat.seat_number == reservation.seat_number,
        models.Seat.is_available == True
    ).first()
    if not seat:
        raise HTTPException(status_code=400, detail="Seat not available")
    
    db_reservation = models.Reservation(**reservation.model_dump())
    seat.is_available = False
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

# Ticket Endpoints
@app.post("/tickets/", response_model=schemas.TicketPublic)
def create_ticket(
    db: db_dependency,
    ticket: schemas.TicketCreate
):
    """Create a new ticket"""
    # Check reservation exists
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == ticket.reservation_id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    db_ticket = models.Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

# Payment Endpoints
@app.post("/payments/", response_model=schemas.PaymentPublic)
def create_payment(
    db: db_dependency,
    payment: schemas.PaymentCreate
):
    """Create a new payment"""
    db_payment = models.Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

# Airport Endpoints
@app.get("/airports/", response_model=List[schemas.AirportPublic])
def read_airports(
    db: db_dependency,
    country_code: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Get list of airports"""
    query = db.query(models.Airport)
    if country_code:
        query = query.filter(models.Airport.country_code == country_code)
    airports = query.offset(skip).limit(limit).all()
    return airports