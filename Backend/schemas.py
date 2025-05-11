from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from pydantic.types import Decimal
import re

# Base Config
model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserPublic(UserBase):
    id: int
    is_active: bool

# Flight Schemas
class FlightBase(BaseModel):
    flight_number: str = Field(..., min_length=2, max_length=10, pattern=r'^[A-Za-z0-9]+$')
    departure_code: str = Field(..., min_length=3, max_length=3, pattern=r'^[A-Z]{3}$')
    destination_code: str = Field(..., min_length=3, max_length=3, pattern=r'^[A-Z]{3}$')
    departure_time: datetime
    arrival_time: datetime
    total_seats: int = Field(..., gt=0)
    available_seats: int = Field(..., ge=0)
    airline_id: Optional[int] = None

    @field_validator('departure_code', 'destination_code')
    @classmethod
    def validate_airport_codes(cls, v: str) -> str:
        return v.upper()

    @field_validator('arrival_time')
    @classmethod
    def validate_arrival_time(cls, v: datetime, values) -> datetime:
        if 'departure_time' in values.data and v <= values.data['departure_time']:
            raise ValueError("Arrival must be after departure")
        return v

class FlightCreate(FlightBase):
    pass

class FlightPublic(FlightBase):
    id: int
    user_id: int

# Passenger Schemas
class PassengerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    national_id: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    phone_number: str = Field(..., min_length=5, max_length=20)
    nationality: str = Field(..., min_length=2, max_length=50)

class PassengerCreate(PassengerBase):
    passport_number: str = Field(..., min_length=5, max_length=20)
    date_of_birth: datetime
    is_vip: bool = False
    address: Optional[str] = None
    gender: Optional[str] = None
    frequent_flyer_number: Optional[str] = None

class PassengerPublic(PassengerBase):
    id: int
    passport_number: str
    is_vip: bool

# Reservation Schemas
class ReservationBase(BaseModel):
    passenger_id: int
    flight_id: int
    seat_number: str = Field(..., pattern=r'^[0-9]+[A-Z]$')

class ReservationCreate(ReservationBase):
    status: str = "Pending"
    booking_agent_id: Optional[str] = None

class ReservationPublic(ReservationBase):
    id: int
    status: str
    created_at: datetime
    flight: FlightPublic
    passenger: PassengerPublic

# Ticket Schemas
class TicketBase(BaseModel):
    passenger_id: int
    flight_id: int
    seat_number: str
    ticket_class: str = Field(..., pattern=r'^(economy|premium economy|business|first)$')
    reservation_id: int

class TicketCreate(TicketBase):
    status: str = "active"
    is_changeable: Optional[bool] = None
    is_refundable: Optional[bool] = None
    promotion_id: Optional[str] = None

class TicketPublic(TicketBase):
    id: int
    status: str
    issue_date: datetime
    base_price: Decimal = Field(..., gt=0)
    final_price: Decimal = Field(..., gt=0)

# Payment Schemas
class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    method: str = Field(..., pattern=r'^(credit card|debit card|bank transfer|cash)$')
    reservation_id: int
    currency: str = Field(..., min_length=3, max_length=3)

class PaymentCreate(PaymentBase):
    status: str = "pending"
    transaction_id: Optional[str] = None

class PaymentPublic(PaymentBase):
    id: str
    status: str
    payment_date: datetime
    is_refundable: bool

# Airport Schemas
class AirportBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=3, pattern=r'^[A-Z]{3}$')
    name: str
    country_code: str = Field(..., min_length=2, max_length=2)
    number_of_terminals: int = Field(..., ge=1)

class AirportPublic(AirportBase):
    location: Optional[str] = None

# Airline Schemas
class AirlineBase(BaseModel):
    name: str
    iata_code: str = Field(..., min_length=2, max_length=2)
    icao_code: str = Field(..., min_length=3, max_length=3)
    base_airport_code: str = Field(..., min_length=3, max_length=3)

class AirlinePublic(AirlineBase):
    id: int
    headquarters: Optional[str] = None
    year_founded: Optional[int] = None

# Seat Schemas
class SeatBase(BaseModel):
    seat_number: str
    class_type: str
    is_available: bool
    flight_id: int

class SeatPublic(SeatBase):
    id: int
    seat_type: str
    additional_features: List[str]

# Promotion Schemas
class PromotionBase(BaseModel):
    description: str
    discount_percentage: Decimal = Field(..., ge=0, le=100)
    start_date: datetime
    end_date: datetime
    promo_code: str
    min_purchase: Decimal = Field(..., ge=0)

class PromotionCreate(PromotionBase):
    max_discount: Decimal = Field(..., ge=0)
    usage_limit: int = Field(..., gt=0)

class PromotionPublic(PromotionBase):
    id: str
    usage_count: int
    is_active: bool

# Response Models for Relationships
class FlightWithSeats(FlightPublic):
    seats: List[SeatPublic] = []

class PassengerWithReservations(PassengerPublic):
    reservations: List[ReservationPublic] = []

class ReservationWithTickets(ReservationPublic):
    tickets: List[TicketPublic] = []