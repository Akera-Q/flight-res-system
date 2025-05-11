import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Set
from datetime import datetime, date, timedelta
import json

import pytz
from multipledispatch import dispatch

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Date,
    ForeignKey,
    MetaData,
    Text,
    text
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    scoped_session,
    relationship
)
from sqlalchemy.exc import SQLAlchemyError



from PIL import Image, ImageTk  # Import Pillow modules


# If you have a local module for database session setup
#from .database import get_session   !!!Adjust the relative path as needed

filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

engine = create_engine(
    f'sqlite:///{filename}.db',
    echo=False,
    future=True           # Use SQLAlchemy 2.0-style returns and behaviors
)

# Declarative base class: all ORM models will inherit from this
Base = declarative_base()
    
# Session factory: create Session objects to interact with the database
# Session factory
def get_session():
    SessionLocal = sessionmaker(bind=engine, autoflush=False)
    return SessionLocal()



# Initialize the database (create tables for all Base subclasses)
def init_db():
    """
    Import all ORM models before calling this, then run to create tables .
    """
    Base.metadata.create_all(bind=engine)



# Start of Nada part idk
class Airport(Base):
    __tablename__ = 'airports'

    code = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String)
    country_code = Column(String, ForeignKey('countries.code'))  # ✅ Foreign key to Country.code
    number_of_terminals = Column(Integer)

    # Relationships
    country = relationship("Country", back_populates="airports")  # ✅ Works with Country.airports
    airlines = relationship("Airline", back_populates="base_airport")

    def __init__(self, name: str, code: str, location: str, country_code: str, number_of_terminals: int):
        self.name = name
        self.code = code
        self.location = location
        self.country_code = country_code
        self.number_of_terminals = number_of_terminals

    def save(self):
        session = get_session()
        session.add(self)
        session.commit()
        session.close()

    @staticmethod
    def create_flight(session, departure_code: str, flight_number: str, destination_code: str,
                      departure_time: str, arrival_time: str, total_seats: int,
                      gate: str, terminal: str, airline_id: int, days_of_operation: int):
        flight = Flight(
            flight_number=flight_number,
            departure_code=departure_code,
            destination_code=destination_code,
            departure_time=departure_time,
            arrival_time=arrival_time,
            total_seats=total_seats,
            gate=gate,
            terminal=terminal,
            airline_id=airline_id,
            days_of_operation=days_of_operation
        )
        session.add(flight)
        session.commit()
        print(f"Flight {flight_number} created departing from Airport {departure_code}.")

    @staticmethod
    def remove_flight(session, flight_number):
        try:
            flight = session.query(Flight).filter_by(flight_number=flight_number).first()
            if not flight:
                print(f"Flight {flight_number} does not exist.")
                return
            session.delete(flight)
            session.commit()
            print(f"Flight {flight_number} removed.")
        except Exception as e:
            session.rollback()
            print(f"Error while removing flight: {e}")

    @staticmethod
    def manage_seats(session, flight_number: int):
        flight = session.query(Flight).filter_by(flight_number=flight_number).first()
        if not flight:
            print(f"No flight found with ID {flight_number}")
            return
        print(f"Managing seats for Flight {flight.flight_number}:")
        for seat in flight.seats:
            print(f"Seat Number {seat.seat_number} - Available: {seat.is_available} Class type {seat.class_type}")

class Airline(Base):
    __tablename__ = 'airlines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    iata_code = Column(String, unique=True)
    icao_code = Column(String, unique=True)
    headquarters = Column(String)
    year_founded = Column(Integer)
    base_airport_code = Column(String, ForeignKey('airports.code'))

    base_airport = relationship("Airport", back_populates="airlines")
    flights = relationship("Flight", back_populates="airline")

    def __init__(self, name, iata_code, icao_code, headquarters, year_founded, base_airport_code):
        self.name = name
        self.iata_code = iata_code
        self.icao_code = icao_code
        self.headquarters = headquarters
        self.year_founded = year_founded
        self.base_airport_code = base_airport_code

    @staticmethod
    def create_flight(session, airline_id: int, flight_number: str, departure_code: str, destination_code: str,
                      departure_time: str, arrival_time: str, total_seats: int, gate: str, terminal: str, days_of_operation: int):
        try:
            flight = Flight(
                flight_number=flight_number,
                departure_code=departure_code,
                destination_code=destination_code,
                departure_time=departure_time,
                arrival_time=arrival_time,
                total_seats=total_seats,
                gate=gate,
                terminal=terminal,
                airline_id=airline_id,
                days_of_operation=days_of_operation
            )
            session.add(flight)
            session.commit()
            print(f"Flight {flight_number} created for Airline ID {airline_id}.")
        except Exception as e:
            session.rollback()
            print(f"Error creating flight: {e}")

    @staticmethod
    def delete_flight(session, airline_id: int, flight_number: str):
        try:
            flight = session.query(Flight).filter_by(airline_id=airline_id, flight_number=flight_number).first()
            if not flight:
                print(f"Flight {flight_number} does not exist for Airline ID {airline_id}.")
                return
            session.delete(flight)
            session.commit()
            print(f"Flight {flight_number} deleted for Airline ID {airline_id}.")
        except Exception as e:
            session.rollback()
            print(f"Error deleting flight: {e}")

    def get_flight(self, flight_number):
        for flight in self.flights:
            if flight.flight_number == flight_number:
                return flight
        return None

    @staticmethod
    def manage_seats(session, flight_number: int):
        flight = session.query(Flight).filter_by(flight_number=flight_number).first()
        if not flight:
            print(f"No flight found with ID {flight_number}")
            return
        print(f"Managing seats for Flight {flight.flight_number}:")
        for seat in flight.seats:
            print(f"Seat Number {seat.seat_number} - Available: {seat.is_available} Class type {seat.class_type}")
        




class Administrator(Base):
    __tablename__ = 'administrators'

    adminID = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String)
    contactEmail = Column(String)
    hasManagementAccess = Column(Boolean, default=False)

    def __init__(self, adminID: str, name: str, role: str, contactEmail: str, hasManagementAccess: bool):
        self.adminID = adminID
        self.name = name
        self.role = role
        self.contactEmail = contactEmail
        self.hasManagementAccess = hasManagementAccess

    @staticmethod
    def create_flight(session, airline_id: int, flight_number: str, departure_code: str, destination_code: str,
                      departure_time: str, arrival_time: str, total_seats: int, gate: str, terminal: str, days_of_operation: int):
        try:
            flight = Flight(
                flight_number=flight_number,
                departure_code=departure_code,
                destination_code=destination_code,
                departure_time=departure_time,
                arrival_time=arrival_time,
                total_seats=total_seats,
                gate=gate,
                terminal=terminal,
                airline_id=airline_id,
                days_of_operation=days_of_operation
            )
            session.add(flight)
            session.commit()
            print(f"Flight {flight_number} created for Airline ID {airline_id}.")
        except Exception as e:
            session.rollback()
            print(f"Error creating flight: {e}")

    @staticmethod
    def remove_flight(session, flight_number: str):
        try:
            flight = session.query(Flight).filter_by(flight_number=flight_number).first()
            if not flight:
                print(f"Flight {flight_number} does not exist.")
                return
            session.delete(flight)
            session.commit()
            print(f"Flight {flight_number} removed successfully.")
        except Exception as e:
            session.rollback()
            print(f"Error removing flight: {e}")

    @staticmethod
    def approve_reservation(session, reservation_id: int):
       
        try:
            reservation = session.query(Reservation).filter_by(id=reservation_id, status="Pending").first()
            if not reservation:
                print(f"Reservation {reservation_id} does not exist or is not pending.")
                return
            reservation.status = "Confirmed"

            session.commit()
            print(f"Reservation {reservation_id} approved successfully.")
        except Exception as e:
            session.rollback()
            print(f"Error approving reservation: {e}")

    @staticmethod
    def cancel_reservation(session, reservation_id: int):
        try:
            reservation = session.query(Reservation).filter_by(id=reservation_id).first()
            if not reservation:
                print(f"Reservation {reservation_id} does not exist.")
                return
            reservation.status = "Canceled"

            
            session.commit()
            print(f"Reservation {reservation_id} canceled successfully.")
        except Exception as e:
            session.rollback()
            print(f"Error canceling reservation: {e}")

    # @staticmethod
    # def update_flight_details(session, flight_number: str, updated_data: dict):
    #     try:
    #         flight = session.query(Flight).filter_by(flight_number=flight_number).first()
    #         if not flight:
    #             print(f"Flight {flight_number} does not exist.")
    #             return
    #         for key, value in updated_data.items():
    #             setattr(flight, key, value)
    #         session.commit()
    #         print(f"Flight {flight_number} updated successfully.")
    #     except Exception as e:
    #         session.rollback()
    #         print(f"Error updating flight details: {e}")

    @staticmethod
    def view_all_reservations(session):
        try:
            reservations = session.query(Reservation).all()
            if not reservations:
                print("No reservations found.")
                return
            print("Reservations:")
            for reservation in reservations:
                print(f"Reservation ID: {reservation.id}, Passenger: {reservation.passenger.name}, Flight: {reservation.flight.flight_number}, Status: {reservation.status}")
        except Exception as e:
            print(f"Error viewing reservations: {e}")

    @staticmethod
    def view_all_flights(session):
        try:
            flights = session.query(Flight).all()
            if not flights:
                print("No flights found.")
                return
            print("Flights:")
            for flight in flights:
                print(f"Flight Number: {flight.flight_number}, Departure: {flight.departure_code}, Destination: {flight.destination_code}, Seats Available: {flight.available_seats}")
        except Exception as e:
            print(f"Error viewing flights: {e}")




class Country(Base):
    __tablename__ = 'countries'

    name = Column(String, nullable=False)
    code = Column(String, primary_key=True)
    continent = Column(String)
    official_language = Column(String)
    is_schengen_zone_member = Column(Boolean, default=False)

    airports = relationship("Airport", back_populates="country")  # if defined on Airport
    # You can also define relationships to flights if needed

    def __init__(self, name: str, code: str, continent: str, official_language: str, is_schengen_zone_member: bool):
        self.name = name
        self.code = code
        self.continent = continent
        self.official_language = official_language
        self.is_schengen_zone_member = is_schengen_zone_member

    def __repr__(self):
        return f"<Country(name={self.name}, code={self.code})>"

class Flight(Base):
    __tablename__ = 'flights'

    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_number = Column(String, nullable=False, unique=True)
    departure_code = Column(String, ForeignKey('airports.code'), nullable=False)
    destination_code = Column(String, ForeignKey('airports.code'), nullable=False)
    departure_time = Column(DateTime)  # Changed to DateTime
    arrival_time = Column(DateTime)    # Changed to DateTime
    total_seats = Column(Integer)
    gate = Column(String)
    terminal = Column(String)
    airline_id = Column(Integer, ForeignKey('airlines.id'))
    days_of_operation = Column(Integer)

    # Relationships
    seats = relationship("Seat", back_populates="flight", cascade="all, delete-orphan")
    airline = relationship("Airline", back_populates="flights")
    departure_airport = relationship("Airport", foreign_keys=[departure_code])
    destination_airport = relationship("Airport", foreign_keys=[destination_code])
    reservations = relationship("Reservation", back_populates="flight", cascade="all, delete-orphan")

    def __init__(self, flight_number: str, departure_code: str, destination_code: str,
                 departure_time: datetime, arrival_time: datetime, total_seats: int, gate: str,
                 terminal: str, airline_id: int, days_of_operation: int):
        self.flight_number = flight_number
        self.departure_code = departure_code
        self.destination_code = destination_code
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.total_seats = total_seats
        self.available_seats = total_seats
        self.gate = gate
        self.terminal = terminal
        self.airline_id = airline_id
        self.days_of_operation = days_of_operation

    def add_reservation(self, reservation):
        if reservation.seat.is_available:
            reservation.seat.reserve_seat()
            self.reservations.append(reservation)
            self.available_seats -= 1
        else:
            print(f"Seat {reservation.seat.seat_number} is already reserved!")

    def remove_reservation(self, reservation):
        if reservation in self.reservations:
            reservation.seat.release_seat()
            self.reservations.remove(reservation)
            self.available_seats += 1

    @staticmethod
    def calculate_empty_seats(session, flight_id: int):
        flight = session.query(Flight).filter_by(id=flight_id).first()
        if not flight:
            print(f"No flight found with ID {flight_id}")
            return
        empty_seats = session.query(Seat).filter_by(flight_id=flight_id, is_available=True).count()
        print(f"Flight {flight.flight_number} has {empty_seats} empty seats.")
        return empty_seats

    @staticmethod
    def calculate_duration(departure_time: datetime, arrival_time: datetime) -> str:
        # Duration calculation with proper DateTime objects
        duration = arrival_time - departure_time
        return str(duration)

    def __repr__(self):
        return f"<Flight({self.flight_number}: {self.departure_code} -> {self.destination_code})>"
# End of Nada part



# Start of Hend's part
class ReservationStatus(Enum):
    pending = "Pending" 
    confirmed = "Confirmed"
    canceled = "Canceled" 

class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(String, ForeignKey('passengers.id'))
    flight_id = Column(Integer, ForeignKey('flights.id'))
    seat_number = Column(String)
    status = Column(String, default="Pending")
    final_price = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    flight = relationship("Flight", back_populates="reservations")
    passenger = relationship("Passenger", back_populates="reservations")
    tickets = relationship("Ticket", back_populates="reservation", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="reservation", cascade="all, delete-orphan")

    def __init__(self, passenger: "Passenger", flight: "Flight", seat_number: str, status: str = "Pending"):

        self.passenger = passenger
        self.flight = flight
        self.seat_number = seat_number
        self.status = status
        self.final_price = 0.0

    def confirm(self):
        """Confirm the reservation and update flight availability"""
        if self.status == "Pending":
            self.status = "Confirmed"
            self.flight.available_seats -= 1
            return True
        return False

    def cancel(self):
        """Cancel the reservation and update flight availability"""
        if self.status != "Canceled":
            self.status = "Canceled"
            self.flight.available_seats += 1
            if self.payment:
                self.payment.refund()
            return True
        return False

    def calculate_duration(self) -> timedelta:
        """Calculate flight duration"""
        return self.flight.arrival_time - self.flight.departure_time

    def add_ticket(self, ticket: "Ticket"):
        """Add a ticket to the reservation"""
        if ticket not in self.tickets:
            self.tickets.append(ticket)
            self.final_price += ticket.price
            ticket.reservation = self

class Ticket(Base):
    __tablename__ = 'tickets'

    ticket_number = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(String, ForeignKey('passengers.id'))
    flight_id = Column(Integer, ForeignKey('flights.id'))
    seat_number = Column(String)
    ticket_class = Column(String)
    status = Column(String)
    issue_date = Column(DateTime)
    expiration_date = Column(DateTime)
    base_price = Column(Float)
    final_price = Column(Float)
    
    # Foreign key reference to Reservation
    reservation_id = Column(Integer, ForeignKey('reservations.id'))

    # Relationship to Reservation (one ticket belongs to one reservation)
    reservation = relationship("Reservation", back_populates="tickets")

    base_prices = {
        "first": 6000.0,
        "business": 3000.0,
        "premium economy": 2000.0,
        "economy": 1000.0,
    }

    def __init__(self, passenger: "Passenger", flight: "Flight", seat_number: str, 
                 ticket_class: str, reservation: "Reservation" = None,
                 is_changeable: Optional[bool] = None, 
                 is_refundable: Optional[bool] = None,
                 promotion: Optional["Promotion"] = None):
        
        ticket_class = ticket_class.strip().lower()
        if ticket_class not in Ticket.base_prices:
            raise ValueError(f"Invalid ticket class: {ticket_class}. Must be one of {list(Ticket.base_prices.keys())}")
        
        self.passenger = passenger
        self.flight = flight
        self.seat_number = seat_number
        self.ticket_class = ticket_class
        self.status = "active"
        self.issue_date = datetime.now()
        self.promotion = promotion
        self.expiration_date = None
        self.base_price = Ticket.base_prices[ticket_class]
        self.final_price = self.get_final_price()
        self.reservation = reservation

        self.is_changeable = is_changeable if is_changeable is not None else self.ticket_class in {"first", "business"}
        self.is_refundable = is_refundable if is_refundable is not None else self.ticket_class == "first"

        # Add the ticket to the latest reservation if available
        if reservation is None:
            latest_reservation = self.passenger.get_latest_reservation()
            if latest_reservation:
                latest_reservation.add_ticket(self)

    def get_ticket_number(self):
        return self.ticket_number  # Use auto-generated ticket_number

    def issue_ticket(self):
        self.expiration_date = self.issue_date.replace(year=self.issue_date.year + 1)

    def cancel_ticket(self):
        if self.is_refundable:
            self.status = "canceled"
            return "The Ticket was canceled and your money was refunded"
        else:
            return "This ticket is Nonrefundable."

    def change_seat(self, new_seat: str):
        if self.is_changeable:
            self.seat_number = new_seat
            return f"Your Seat changed to {new_seat}."
        else:
            return "This ticket is not changeable."

    def is_ticket_valid(self):
        if self.expiration_date and datetime.now() > self.expiration_date:
            self.status = "expired"
            return False
        return True

    def get_final_price(self):
        if self.promotion:
            return self.promotion.apply_discount(self.base_price)
        return self.base_price

    def set_promotion(self, promotion: "Promotion"):
        if promotion.is_valid():
            self.promotion = promotion
            self.final_price = self.get_final_price()

    @property
    def price(self):
        return self.final_price

    def ticket_information(self):
        promo_information = (f"The added offer: {self.promotion.promo_code} "
                             f"({self.promotion.discount_percentage}% discount)"
                             if self.promotion else "There is no discount")
        
        return (
            f"Ticket Number: {self.ticket_number}\n"
            f"Passenger: {self.passenger}\n"
            f"Flight: {self.flight.flight_number}\n"
            f"Seat: {self.seat_number}\n"
            f"Ticket Class: {self.ticket_class}\n"
            f"Original Price: {self.base_price}\n"
            f"Price After Discount: {self.final_price}\n"
            f"Status: {self.status}\n"
            f"Issue Date: {self.issue_date}\n"
            f"Expiration Date: {self.expiration_date if self.expiration_date else 'Not defined'}\n"
            f"{promo_information}"
        )

class Promotion(Base):
    __tablename__ = 'promotions'
    
    promo_id = Column(String, primary_key=True)
    description = Column(String)
    discount_percentage = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    promo_code = Column(String)
    min_purchase = Column(Float)
    max_discount = Column(Float)
    usage_limit = Column(Integer)
    usage_count = Column(Integer)

    def __init__(self, promo_id: str, description: str, discount_percentage: float, start_date: datetime, 
                 end_date: datetime, promo_code: str, min_purchase: float, max_discount: float, usage_limit: int):
        self.promo_id = promo_id
        self.description = description
        self.discount_percentage = discount_percentage
        self.start_date = start_date
        self.end_date = end_date
        self.promo_code = promo_code
        self.min_purchase = min_purchase
        self.max_discount = max_discount
        self.usage_limit = usage_limit
        self.usage_count = 0

    @staticmethod
    def check_promotion_validity(session, promo_id: str) -> bool:
        promotion = session.query(Promotion).filter_by(promo_id=promo_id).first()
        if not promotion:
            raise ValueError(f"No promotion found with ID: {promo_id}")

        now = datetime.now()
        # Promotion is valid if the current date is within the promotion period and usage limit is not exceeded
        is_valid = promotion.start_date <= now <= promotion.end_date and promotion.usage_count < promotion.usage_limit
        return is_valid

    @staticmethod
    def apply_discount(session, promo_id: str, original_price: float) -> float:
        promotion = session.query(Promotion).filter_by(promo_id=promo_id).first()
        if not promotion:
            raise ValueError(f"No promotion found with ID: {promo_id}")

        if not Promotion.check_promotion_validity(session, promo_id):
            raise ValueError(f"Promotion {promo_id} is not valid or has expired.")
        
        discounted_price = original_price * (1 - promotion.discount_percentage / 100)
        discounted_price = min(discounted_price, promotion.max_discount)  # Ensure max discount is respected

        # Update usage_count and commit to the database to prevent multiple usage
        promotion.usage_count += 1
        session.commit()

        return discounted_price

    @staticmethod
    def extend_promotion(session, promo_id: str, new_end_date: datetime):
        promotion = session.query(Promotion).filter_by(promo_id=promo_id).first()
        if not promotion:
            raise ValueError(f"No promotion found with ID: {promo_id}")

        if new_end_date > promotion.end_date:
            promotion.end_date = new_end_date
            session.commit()
            print(f"Promotion {promo_id} has been extended to {new_end_date.strftime('%Y-%m-%d')}.")
        else:
            raise ValueError("The new date must be after the current end date.")

    @staticmethod
    def get_promotion_info(session, promo_id: str) -> str:
        promotion = session.query(Promotion).filter_by(promo_id=promo_id).first()
        if not promotion:
            raise ValueError(f"No promotion found with ID: {promo_id}")

        # Check if the promotion is valid at the moment
        promo_validity = 'Active' if Promotion.check_promotion_validity(session, promo_id) else 'Expired'
        
        return (f"Promo ID: {promotion.promo_id}\n"
                f"Description: {promotion.description}\n"
                f"Discount: {promotion.discount_percentage}% (Max: {promotion.max_discount})\n"
                f"Min Purchase: {promotion.min_purchase}\n"
                f"Promo Code: {promotion.promo_code}\n"
                f"Usage Limit: {promotion.usage_limit}, Usage Count: {promotion.usage_count}\n"
                f"Start Date: {promotion.start_date.strftime('%Y-%m-%d')}\n"
                f"End Date: {promotion.end_date.strftime('%Y-%m-%d')}\n"
                f"Status: {promo_validity}")

class Special_promotion(Promotion):
    __tablename__ = 'special_promotions'

    # Foreign key to the parent Promotion table
    promo_id = Column(String, ForeignKey('promotions.promo_id'), primary_key=True)
    extra_bonus = Column(Float, nullable=False)  # Additional attribute for Special_promotion

    def __init__(self, promo_id: str, description: str, discount_percentage: float, start_date: datetime, 
                 end_date: datetime, promo_code: str, min_purchase: float, max_discount: float, 
                 usage_limit: int, extra_bonus: float):
        super().__init__(promo_id, description, discount_percentage, start_date, end_date, promo_code, 
                         min_purchase, max_discount, usage_limit)
        self.extra_bonus = extra_bonus

    def apply_discount(self, original_price: float) -> float:
        # Apply both discount and extra bonus
        total_discount = self.discount_percentage + self.extra_bonus
        discounted_price = original_price * (1 - total_discount / 100)
        
        # Ensure the discount does not exceed the max discount
        discounted_price = min(discounted_price, self.max_discount)
        
        return discounted_price

    def promotion_information(self) -> str:
        # Include base promotion info and extra bonus
        base_information = super().promotion_information()
        return base_information + f" Extra Bonus: {self.extra_bonus}%"

from typing import Tuple

class Base_luggage(Base):
    __abstract__ = True

    def __init__(self, luggage_id: str, passenger: "Passenger", ticket: "Ticket", weight: float,
                 volume: int = (0, 0, 0), luggage_fee: float = 0.0, 
                 status: str = "Pending", is_checked_in: bool = False, is_fragile: bool = False):
        self.luggage_id = luggage_id
        self.passenger = passenger
        self.ticket = ticket
        self.weight = weight
        self.volume = volume
        self.is_fragile = is_fragile
        self.status = status
        self.is_checked_in = is_checked_in
        self.tracking_history = []  # Keeps track of status changes over time.
        self.luggage_fee = luggage_fee  # Fee to be calculated based on weight and other factors.
        self.fine = 0  # Default fine is set to zero.

    @abstractmethod
    def calculate_fee(self):
        pass

class Luggage(Base_luggage):
    max_weight_limit = 50
    free_weight_limit = 20
    fee_per_kg = 10
    overweight_fine = 100
    __tablename__ = 'luggage'
    luggage_id = Column(String, primary_key=True)
    passenger_id = Column(String, ForeignKey('passengers.id'))
    ticket_id = Column(String, ForeignKey('tickets.ticket_number'))
    weight = Column(Float)
    dimensions = Column(String)
    luggage_fee = Column(Float)
    status = Column(String)
    is_checked_in = Column(Boolean, default=False)
    is_fragile = Column(Boolean, default=False)

    def __init__(self, luggage_id: str, passenger: "Passenger", ticket: "Ticket", weight: float,
                 ticket_class: str, volume: int, luggage_fee: float = 0.0,
                 status: str = "Pending", is_checked_in: bool = False, is_fragile: bool = False):
        super().__init__(luggage_id, passenger, ticket, weight, volume, luggage_fee, status, is_checked_in, is_fragile)
        self.ticket_class = ticket_class
        self.weight_status, self.luggage_fee = self.check_luggage_weight()

    def check_luggage_weight(self):
        ticket_class_limits = {
            "economy": 20,
            "business": 30,
            "first": 40
        }
        allowed_weight = ticket_class_limits.get(self.ticket.ticket_class, 20)
        if self.weight <= self.free_weight_limit:
            return "Within free limit", 0
        elif self.free_weight_limit < self.weight <= self.max_weight_limit:
            extra_weight = self.weight - self.free_weight_limit
            return "Extra Weight", extra_weight * self.fee_per_kg
        else:
            return "Exceeds maximum limit", 0

    def apply_overweight_fine(self):
        if self.weight > self.max_weight_limit:
            self.fine = self.overweight_fine
            self.luggage_fee += self.fine
            return f"Overweight fine of {self.overweight_fine} applied to luggage {self.luggage_id}. New luggage fee: {self.luggage_fee} EGP"
        else:
            return "There is no fine applied."

    def update_luggage_status(self):
        if self.weight > self.max_weight_limit:
            self.status = "Overweight"
            self.apply_overweight_fine()
        else:
            self.status = "Approved"
        if self.is_fragile:
            self.status += " - Fragile item so handle with care."
        self.track_luggage_status()

    def track_luggage_status(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.tracking_history.append(f"{timestamp}: {self.status}")

    def luggage_information(self):
        return (f"Luggage ID: {self.luggage_id}\n"
                f"Passenger: {self.passenger.name}\n"
                f"Weight: {self.weight}\n"
                f"Dimensions (L W H): {self.dimensions}\n"
                f"Fragile: {'Yes' if self.is_fragile else 'No'}\n"
                f"Luggage Fee: {self.luggage_fee} EGP\n"
                f"Luggage Fine: {self.fine} EGP\n"
                f"Status: {self.status}")

class Standard_luggage(Luggage):
    def calculate_fee (self) :
        return max ( 0 , (self.weight - 20 ) * 10 ) 

class Overweight_luggage(Luggage) :
    def calculate_fee (self) :
        return 100 + max( 0 , (self.weight - 30) * 15 ) 

class Loyalty_program(Base):
    __tablename__ = 'loyalty_programs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    program_name = Column(String)
    passenger_id = Column(Integer, ForeignKey('passengers.id'), unique=True)  # One-to-one relationship
    points = Column(Integer)
    tier_level = Column(String)
    required_points_for_next_tier = Column(Integer)
    membership_start_date = Column(DateTime)
    available_rewards = Column(Text)  # Use Text to store JSON as string

    # One-to-one relationship with Passenger
    passenger = relationship("Passenger", back_populates="loyalty_program")

    def __init__(self, program_name: str, passenger: "Passenger", points: int, available_rewards: List[str],
                 membership_start_date: datetime, tier_level: str, required_points_for_next_tier: int):
        self.program_name = program_name
        self.passenger = passenger
        self.points = points
        self.available_rewards = json.dumps(available_rewards)  # Serialize the rewards list
        self.membership_start_date = membership_start_date
        self.tier_level = tier_level
        self.required_points_for_next_tier = required_points_for_next_tier

    def add_points(self, pts: int):
        if pts > 0:
            self.points += pts
            print(f"{pts} points have been added to your account. Total Points: {self.points}")

    def redeem_points(self, pts: int):
        if pts > 0 and pts <= self.points:
            self.points -= pts
            print(f"You have redeemed {pts} points. Remaining points: {self.points}")
        else:
            print("You don't have enough points to redeem.")

    def check_tier_upgrade(self):
        if self.points >= self.required_points_for_next_tier:
            print("You are eligible for an upgrade. You can move to a higher tier.")
            # Optionally, upgrade the tier here
        else:
            print(f"You need {self.required_points_for_next_tier - self.points} more points to upgrade.")

    def get_program_info(self):
        available_rewards_list = self.get_available_rewards()  # Deserialize the rewards list
        return (f"Loyalty Program: {self.program_name}\n"
                f"Passenger: {self.passenger.name}\n"  # Ensure passenger has a `name` attribute
                f"Current Points: {self.points}\n"
                f"Membership Start Date: {self.membership_start_date.strftime('%Y-%m-%d')}\n"
                f"Points Needed for Upgrade: {self.required_points_for_next_tier}\n"
                f"Available Rewards: {', '.join(available_rewards_list)}")

    def get_available_rewards(self):
        return json.loads(self.available_rewards)  # Deserialize the JSON string to a Python list
#  End of Hend's part



# Start of Aya part
class Seat(Base):
    __tablename__ = 'seats'

    seat_id = Column(Integer, primary_key=True, autoincrement=True)
    seat_number = Column(String, nullable=False)
    class_type = Column(String, nullable=False)
    is_available = Column(Boolean, default=True)
    seat_type = Column(String, nullable=False)
    additional_features = Column(Text, default="[]")  # Store as JSON string
    reservation_time = Column(DateTime, nullable=True)
    flight_id = Column(Integer, ForeignKey('flights.id'))
    flight = relationship("Flight", back_populates="seats")

    def __init__(self, seat_number: str, class_type: str, is_available: bool, seat_type: str, flight_id: int, additional_features: List[str] = None):
        self.seat_number = seat_number
        self.class_type = class_type
        self.is_available = is_available
        self.seat_type = seat_type
        self.flight_id = flight_id
        self.additional_features = json.dumps(additional_features) if additional_features else "[]"  # Serialize list to JSON string
        self.reservation_time = None

    @staticmethod
    def calculate_empty_seats(session, flight_id: int):
        empty_seats = session.query(Seat).filter_by(flight_id=flight_id, is_available=True).count()
        print(f"Flight {flight_id} has {empty_seats} empty seats.")
        return empty_seats

    @staticmethod
    def display_reserved_seats(session, flight_id: int):
        reserved_seats = session.query(Seat).filter_by(flight_id=flight_id, is_available=False).all()
        if not reserved_seats:
            print(f"No reserved seats found for Flight ID {flight_id}")
            return

        print(f"Reserved seats for Flight ID {flight_id}:")
        for seat in reserved_seats:
            print(f"Seat Number: {seat.seat_number}, Reserved at: {seat.reservation_time}")

    def reserve_seat(self):
        if self.is_available:
            self.is_available = False
            self.reservation_time = datetime.now()
            print(f"Seat {self.seat_number} has been reserved at {self.reservation_time}.")
        else:
            print(f"Seat {self.seat_number} is already reserved.")

    def release_seat(self):
        if not self.is_available:
            self.is_available = True
            self.reservation_time = None
            print(f"Seat {self.seat_number} is now available.")
        else:
            print(f"Seat {self.seat_number} is not reserved.")

    def get_additional_features(self):
        return json.loads(self.additional_features)  # Deserialize the JSON string to a Python list

    def __str__(self):
        return f"Seat {self.seat_number} - Class: {self.class_type}, Type: {self.seat_type}, Available: {self.is_available}"

class Passenger(Base):
    __tablename__ = 'passengers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    national_id = Column(String, unique=True)  # Make national_id a unique key
    email = Column(String)
    phone_number = Column(String)
    nationality = Column(String)
    is_vip = Column(Boolean)
    address = Column(String)
    date_of_birth = Column(Date)  # Changed to Date type
    passport_number = Column(String)
    gender = Column(String)
    frequent_flyer_number = Column(String, unique=True)  # Unique constraint added

    # One-to-one relationship with Loyalty_program
    loyalty_program = relationship("Loyalty_program", back_populates="passenger", uselist=False)

    reservations = relationship("Reservation", back_populates="passenger", cascade="all, delete-orphan")

    def __init__(self, name: str, national_id: str, email: str, phone_number: str, nationality: str, is_vip: bool, address: str, 
                 date_of_birth: str, passport_number: str, gender: str, frequent_flyer_number: str):
        self.name = name
        self.national_id = national_id
        self.email = email
        self.phone_number = phone_number
        self.nationality = nationality
        self.is_vip = is_vip
        self.address = address
        self.date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d") if isinstance(date_of_birth, str) else date_of_birth
        self.passport_number = passport_number
        self.gender = gender
        self.frequent_flyer_number = frequent_flyer_number

    @staticmethod
    def enroll_in_loyalty_program(session, national_id: str, program_name: str):
        passenger = session.query(Passenger).filter_by(national_id=national_id).first()
        if not passenger:
            print(f"No passenger found with National ID: {national_id}")
            return

        if not passenger.loyalty_program:
            loyalty_program = Loyalty_program(
                program_name=program_name,
                passenger=passenger,
                points=0,
                available_rewards=[],
                membership_start_date=datetime.now(),
                tier_level="Basic",
                required_points_for_next_tier=100
            )
            session.add(loyalty_program)
            session.commit()
            print(f"{passenger.name} has been enrolled in the {program_name} loyalty program.")
        else:
            print(f"{passenger.name} is already enrolled in the {passenger.loyalty_program.program_name} loyalty program.")

    @staticmethod
    def get_passenger_info(session, national_id: str):
        passenger = session.query(Passenger).filter_by(national_id=national_id).first()
        if not passenger:
            return f"No passenger found with National ID: {national_id}"

        loyalty_info = f"Loyalty Program: {passenger.loyalty_program.program_name}" if passenger.loyalty_program else "There is no loyalty program."
        return (f"Passenger ID: {passenger.id}\n"
                f"Name: {passenger.name}\n"
                f"National ID: {passenger.national_id}\n"
                f"Phone Number: {passenger.phone_number}\n"
                f"Nationality: {passenger.nationality}\n"
                f"VIP Status: {passenger.is_vip}\n"
                f"Address: {passenger.address}\n"
                f"Date of Birth: {passenger.date_of_birth.strftime('%Y-%m-%d')}\n"
                f"Passport Number: {passenger.passport_number}\n"
                f"Gender: {passenger.gender}\n"
                f"Frequent Flyer Number: {passenger.frequent_flyer_number}\n"
                f"{loyalty_info}")

    def __str__(self):
        return f"Passenger: {self.name}, National ID: {self.national_id}, Email: {self.email}"

class Currency(Base):
    __tablename__ = 'currencies'
    
    currency_code = Column(String, primary_key=True)
    symbol = Column(String)
    exchange_rate = Column(Float)
    country_name = Column(String)
    last_updated = Column(DateTime)

    def __init__(self, currency_code: str, symbol: str, exchange_rate: float, country_name: str, last_updated: datetime):
        self.currency_code = currency_code
        self.symbol = symbol
        self.exchange_rate = exchange_rate
        self.country_name = country_name
        self.last_updated = last_updated

    @staticmethod
    def convert_to(session, amount: float, source_currency_code: str, target_currency_code: str) -> float:
        source_currency = session.query(Currency).filter_by(currency_code=source_currency_code).first()
        target_currency = session.query(Currency).filter_by(currency_code=target_currency_code).first()

        if not source_currency or not target_currency:
            raise ValueError("One or both currencies do not exist in the database.")

        if source_currency.exchange_rate <= 0 or target_currency.exchange_rate <= 0:
            raise ValueError("Exchange rate must be a positive number.")

        # Perform the conversion
        converted_amount = amount * (target_currency.exchange_rate / source_currency.exchange_rate)
        return round(converted_amount, 2)

    @staticmethod
    def update_exchange_rate(session, currency_code: str, new_rate: float):
        currency = session.query(Currency).filter_by(currency_code=currency_code).first()

        if not currency:
            raise ValueError(f"Currency with code {currency_code} does not exist in the database.")

        if new_rate <= 0:
            raise ValueError("Exchange rate must be a positive number.")

        currency.exchange_rate = new_rate
        currency.last_updated = datetime.now()
        session.commit()
        print(f"Exchange rate updated to {new_rate} for {currency_code}.")

    @staticmethod
    def display_currency_info(session, currency_code: str):
        currency = session.query(Currency).filter_by(currency_code=currency_code).first()

        if not currency:
            raise ValueError(f"Currency with code {currency_code} does not exist in the database.")

        return {
            "Currency": f"{currency.currency_code} ({currency.symbol})",
            "Country": currency.country_name,
            "Exchange Rate": currency.exchange_rate,
            "Last Updated": currency.last_updated
        }

class BookingAgent(Base):
    __tablename__ = 'booking_agents'
    agent_id = Column("agent_id", String, primary_key=True)
    name = Column(String)
    agency = Column(String)
    contact_number = Column(String)
    email = Column(String)
    agency_license_number = Column(String)
    is_certified = Column(Boolean)
    
    # If managed_reservations is related to a Reservation model, it should be a relationship:
    # managed_reservations = relationship("Reservation", backref="agent")

    def __init__(self, agent_id: str, name: str, agency: str, contact_number: str, email: str, managed_reservations, agency_license_number: str, is_certified: bool):
        self.agent_id = agent_id
        self.name = name
        self.agency = agency
        self.contact_number = contact_number
        self.email = email
        self.managed_reservations = managed_reservations
        self.agency_license_number = agency_license_number
        self.is_certified = is_certified

    # No need for properties on simple fields like agent_id, email, etc.
    # Directly access them as attributes. If you want logic in setters/getters, then use them.
    @property
    def contact_number(self):
        return self.contact_number

    @contact_number.setter
    def contact_number(self, new_contact_number):
        self.contact_number = new_contact_number

    @property
    def email(self):
        return self.email

    @email.setter
    def email(self, new_email):
        self.email = new_email

    @property
    def agency_license_number(self):
        return self.agency_license_number

    @property
    def is_certified(self):
        return self.is_certified

    def certify_agent(self):
        self.is_certified = True
        self.certified_date = datetime.now()  # Log certification date

    def _generate_reservation_id(self) -> str:
        return f"reservation-{len(self.managed_reservations) + 1}"

    def create_reservation(self, flight, passenger, seat_number, meal_preference=None):
        reservation_id = self._generate_reservation_id()
        new_reservation = Reservation(
            reservation_id=reservation_id,
            flight=flight,
            passenger=passenger,
            seat_number=seat_number,
            booking_date=datetime.today(),
            is_confirmed=False,
            travel_class=seat_number.class_type,
            special_requests=[],
            meal_preference=meal_preference,
            luggage=[]
        )
        self.managed_reservations.append(new_reservation)
        passenger.add_reservation(new_reservation)
        print(f"Reservation {reservation_id} created by agent {self.name}.")
        return new_reservation

    def cancel_reservation(self, reservation: 'Reservation'):
        if reservation in self.managed_reservations:
            self.managed_reservations.remove(reservation)
            reservation.passenger.cancel_reservation(reservation)
            print(f"Reservation {reservation.reservation_id} canceled by agent {self.name}.")
        else:
            print("Reservation not found.")

    def find_flights(self, departure, destination, date):
        # Here you should query the database or other service for available flights
        available_flights = []  # Replace with actual search logic
        print(f"Searching for flights from {departure} to {destination} on {date}.")
        return available_flights


class Payment(Base):
    __tablename__ = 'payments'

    payment_id = Column(String, primary_key=True)
    amount = Column(Float)
    method = Column(String)
    status = Column(String)
    reservation_id = Column(String, ForeignKey('reservations.id'))
    payment_date = Column(DateTime)
    transaction_id = Column(String)
    currency = Column(String, ForeignKey('currencies.currency_code'))
    is_refundable = Column(Boolean)

    reservation = relationship("Reservation", back_populates="payments")

    def __init__(self, payment_id, amount, method, status, payment_date, transaction_id, currency, is_refundable, reservation_id=None):
        self.payment_id = payment_id
        self.amount = amount
        self.method = method
        self.status = status
        self.payment_date = payment_date
        self.transaction_id = transaction_id
        self.currency = currency
        self.is_refundable = is_refundable
        self.reservation_id = reservation_id

    def process_payment(self) -> bool:
        if self.status == "pending":
            self.status = "completed"
            print(f"Payment {self.payment_id} processed successfully")
            return True
        elif self.status == "completed":
            print(f"Payment {self.payment_id} has already been processed successfully")
            return False
        else:
            print(f"Payment {self.payment_id} could not be processed")
            return False

    def refund(self):
        if self.is_refundable and self.status == "completed":
            self.status = "refunded"
            print(f"Payment {self.payment_id} has been refunded")
        else:
            print(f"Payment {self.payment_id} is not refundable.")
#  End of Aya's part

def test_all_classes_and_relationships():
    # Clean up old database files
    for filename in os.listdir():
        if filename.endswith(".db"):
            os.remove(filename)

    init_db()
    session = get_session()

    try:
        # Create sample data
        country = Country(name="United States", code="US", continent="North America",
                         official_language="English", is_schengen_zone_member=False)
        session.add(country)
        
        airport = Airport(name="JFK International", code="JFK", location="New York",
                         country_code="US", number_of_terminals=5)
        session.add(airport)
        
        airline = Airline(name="Delta Airlines", iata_code="DL", icao_code="DAL",
                         headquarters="Atlanta", year_founded=1924, base_airport_code="JFK")
        session.add(airline)
        
        flight = Flight(
            flight_number="DL123",
            departure_code="JFK",
            destination_code="LAX",
            departure_time=datetime(2023, 6, 15, 8, 0),
            arrival_time=datetime(2023, 6, 15, 11, 0),
            total_seats=150,
            gate="A1",
            terminal="1",
            airline_id=airline.id,
            days_of_operation=7
        )
        session.add(flight)
        
        passenger = Passenger(
            name="John Doe",
            national_id="123456789",
            email="john@example.com",
            phone_number="555-1234",
            nationality="US",
            is_vip=False,
            address="123 Main St",
            date_of_birth="1980-01-01",
            passport_number="P123456",
            gender="Male",
            frequent_flyer_number="FF123"
        )
        session.add(passenger)

        # Create seat
        seat = Seat(
            seat_number="12A",
            class_type="economy",
            is_available=True,
            seat_type="regular",
            flight_id=flight.id
        )
        session.add(seat)
        
        # Create reservation
        reservation = Reservation(
            passenger=passenger,
            flight=flight,
            seat_number="12A"
        )
        session.add(reservation)
        
        # Create ticket - now handled by the test session
        ticket = Ticket(
            passenger=passenger,
            flight=flight,
            seat_number="12A",
            ticket_class="economy",
            reservation=reservation
        )
        session.add(ticket)
        
        # Create payment
        payment = Payment(
            payment_id="PAY001",
            amount=500.0,
            method="Credit Card",
            status="pending",
            payment_date=datetime.now(),
            transaction_id="TXN001",
            currency="USD",
            is_refundable=True
        )
        reservation.payments.append(payment)
        session.add(payment)
        
        # Commit all changes
        session.commit()
        
        # Test operations
        reservation.confirm()
        payment.process_payment()
        session.commit()
        
        print("\n--- Test Results ---")
        print(f"Reservation {reservation.id} confirmed")
        print(f"Payment {payment.payment_id} status: {payment.status}")
        print(f"Flight {flight.flight_number} has {flight.available_seats} seats remaining")
        print("\nAll tests completed successfully!")
        

        # Country
        country = Country(name="Japan", code="JP", continent="Asia", official_language="Japanese", is_schengen_zone_member=False)
        session.add(country)
        session.commit()
        print(country)

        # Airport
        airport = Airport(name="Narita International", code="NRT", location="Tokyo", country_code="JP", number_of_terminals=3)
        session.add(airport)
        session.commit()
        print(airport)

        # Airline
        airline = Airline(name="Japan Airlines", iata_code="JL", icao_code="JAL", headquarters="Tokyo", year_founded=1951, base_airport_code="NRT")
        session.add(airline)
        session.commit()
        print(airline)
        Airport.create_flight(          
            session,  
            flight_number="FK123",
            departure_code="NRT",
            destination_code="LAX",
            departure_time=datetime(2025, 5, 10, 10, 0),
            arrival_time=datetime(2025, 5, 10, 18, 0),
            total_seats=99990,
            gate="Q2",
            terminal="23",
            airline_id=airline.id,
            days_of_operation=99
)
        # Flight
        flight = Flight(
            flight_number="JL123",
            departure_code="NRT",
            destination_code="LAX",
            departure_time=datetime(2025, 5, 10, 10, 0),
            arrival_time=datetime(2025, 5, 10, 18, 0),
            total_seats=200,
            gate="B2",
            terminal="1",
            airline_id=airline.id,
            days_of_operation=7
        )
        session.add(flight)
        session.commit()
        print(flight)

        # Passenger
        passenger = Passenger(
            name="Taro Yamada",
            national_id="987654321",
            email="taro@example.com",
            phone_number="080-1234-5678",
            nationality="Japanese",
            is_vip=True,
            address="Tokyo, Japan",
            date_of_birth="1990-01-01",
            passport_number="JP123456",
            gender="Male",
            frequent_flyer_number="FF987"
        )
        session.add(passenger)
        session.commit()
        Passenger.get_passenger_info(session, "987654321")

        # Seat
        seat = Seat(seat_number="1A", class_type="business", is_available=True, seat_type="window", flight_id=flight.id)
        session.add(seat)
        session.commit()
        print(seat)

        # Reservation
        reservation = Reservation(passenger=passenger, flight=flight, seat_number="1A")
        session.add(reservation)
        session.commit()
        print(reservation)

        # Ticket
        ticket = Ticket(passenger=passenger, flight=flight, seat_number="1A", ticket_class="business", reservation=reservation)
        session.add(ticket)
        session.commit()
        print(ticket)

        # Payment
        payment = Payment(
            payment_id="PAY002",
            amount=1000.0,
            method="Credit Card",
            status="pending",
            payment_date=datetime.now(),
            transaction_id="TXN002",
            currency="JPY",
            is_refundable=True,
            reservation_id=reservation.id
        )
        session.add(payment)
        session.commit()
        print(payment)

        # Promotion
        promotion = Promotion(
            promo_id="PROMO001",
            description="Spring Sale",
            discount_percentage=10.0,
            start_date=datetime(2025, 5, 1),
            end_date=datetime(2025, 5, 31),
            promo_code="SPRING2025",
            min_purchase=500.0,
            max_discount=100.0,
            usage_limit=100
        )
        session.add(promotion)
        session.commit()
        print(promotion)

        # Special Promotion
        special_promotion = Special_promotion(
            promo_id="PROMO002",
            description="VIP Bonus",
            discount_percentage=15.0,
            start_date=datetime(2025, 5, 1),
            end_date=datetime(2025, 5, 31),
            promo_code="VIP2025",
            min_purchase=1000.0,
            max_discount=200.0,
            usage_limit=50,
            extra_bonus=5.0
        )
        session.add(special_promotion)
        session.commit()
        print(special_promotion)

        # Luggage
        luggage = Luggage(
            luggage_id="LUG001",
            passenger=passenger,
            ticket=ticket,
            weight=25.0,
            ticket_class="business",
            volume= 89,
            is_fragile=True
        )
        session.add(luggage)
        session.commit()
        print(luggage)

        # Loyalty Program
        loyalty_program = Loyalty_program(
            program_name="JAL Mileage Bank",
            passenger=passenger,
            points=500,
            available_rewards=["Free Upgrade", "Lounge Access"],
            membership_start_date=datetime(2025, 1, 1),
            tier_level="Silver",
            required_points_for_next_tier=1000
        )
        session.add(loyalty_program)
        session.commit()
        print(loyalty_program)

        # Test methods
        reservation.confirm()
        payment.process_payment()
        seat.reserve_seat()
        seat.release_seat()
        promotion_info = Promotion.get_promotion_info(session, "PROMO001")
        print(promotion_info)


    except Exception as e:
        session.rollback()
        print(f"\nError during testing: {str(e)}")
        raise
    finally:
        session.close()

test_all_classes_and_relationships()



import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine



# Initialize the database
init_db()
session = get_session()

# Create the main application window
class FlightReservationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flight Reservation System")
        self.geometry("800x600")

        # Create a tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Add tabs for each class
        self.add_country_tab()
        self.add_airport_tab()
        self.add_airline_tab()
        self.add_administrator_tab()
        self.add_flight_tab()
        self.add_passenger_tab()
        self.add_seat_tab()
        self.add_reservation_tab()
        self.add_ticket_tab()
        self.add_payment_tab()
        self.add_promotion_tab()
        self.add_luggage_tab()
        self.add_loyalty_program_tab()
        self.add_airport_image_tab()



    def add_country_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Country")

        # Fields for Country
        tk.Label(tab, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(tab)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Code:").grid(row=1, column=0, padx=10, pady=5)
        code_entry = tk.Entry(tab)
        code_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Continent:").grid(row=2, column=0, padx=10, pady=5)
        continent_entry = tk.Entry(tab)
        continent_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(tab, text="Official Language:").grid(row=3, column=0, padx=10, pady=5)
        language_entry = tk.Entry(tab)
        language_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(tab, text="Schengen Zone Member:").grid(row=4, column=0, padx=10, pady=5)
        schengen_var = tk.BooleanVar()
        schengen_checkbox = tk.Checkbutton(tab, variable=schengen_var)
        schengen_checkbox.grid(row=4, column=1, padx=10, pady=5)

        # Add Country Button
        def add_country():
            try:
                country = Country(
                    name=name_entry.get(),
                    code=code_entry.get(),
                    continent=continent_entry.get(),
                    official_language=language_entry.get(),
                    is_schengen_zone_member=schengen_var.get()
                )
                session.add(country)
                session.commit()
                messagebox.showinfo("Success", "Country added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add country: {e}")

        tk.Button(tab, text="Add Country", command=add_country).grid(row=5, column=0, columnspan=2, pady=10)

    def add_airport_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Airport")

        # Fields for Airport Attributes
        tk.Label(tab, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(tab)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Code:").grid(row=1, column=0, padx=10, pady=5)
        code_entry = tk.Entry(tab)
        code_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Location:").grid(row=2, column=0, padx=10, pady=5)
        location_entry = tk.Entry(tab)
        location_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(tab, text="Country Code:").grid(row=3, column=0, padx=10, pady=5)
        country_code_entry = tk.Entry(tab)
        country_code_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(tab, text="Number of Terminals:").grid(row=4, column=0, padx=10, pady=5)
        terminals_entry = tk.Entry(tab)
        terminals_entry.grid(row=4, column=1, padx=10, pady=5)

        # Add Airport Button
        def add_airport():
            try:
                airport = Airport(
                    name=name_entry.get(),
                    code=code_entry.get(),
                    location=location_entry.get(),
                    country_code=country_code_entry.get(),
                    number_of_terminals=int(terminals_entry.get())
                )
                session.add(airport)
                session.commit()
                messagebox.showinfo("Success", "Airport added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add airport: {e}")

        tk.Button(tab, text="Add Airport", command=add_airport).grid(row=5, column=0, columnspan=2, pady=10)

        # Horizontal Line
        ttk.Separator(tab, orient="horizontal").grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        # Fields for Flight Attributes
        tk.Label(tab, text="Flight Number:").grid(row=7, column=0, padx=10, pady=5)
        flight_number_entry = tk.Entry(tab)
        flight_number_entry.grid(row=7, column=1, padx=10, pady=5)

        tk.Label(tab, text="Departure Code:").grid(row=8, column=0, padx=10, pady=5)
        departure_code_entry = tk.Entry(tab)
        departure_code_entry.grid(row=8, column=1, padx=10, pady=5)

        tk.Label(tab, text="Destination Code:").grid(row=9, column=0, padx=10, pady=5)
        destination_code_entry = tk.Entry(tab)
        destination_code_entry.grid(row=9, column=1, padx=10, pady=5)

        tk.Label(tab, text="Departure Time (YYYY-MM-DD HH:MM):").grid(row=10, column=0, padx=10, pady=5)
        departure_time_entry = tk.Entry(tab)
        departure_time_entry.grid(row=10, column=1, padx=10, pady=5)

        tk.Label(tab, text="Arrival Time (YYYY-MM-DD HH:MM):").grid(row=11, column=0, padx=10, pady=5)
        arrival_time_entry = tk.Entry(tab)
        arrival_time_entry.grid(row=11, column=1, padx=10, pady=5)

        tk.Label(tab, text="Total Seats:").grid(row=12, column=0, padx=10, pady=5)
        total_seats_entry = tk.Entry(tab)
        total_seats_entry.grid(row=12, column=1, padx=10, pady=5)

        tk.Label(tab, text="Gate:").grid(row=13, column=0, padx=10, pady=5)
        gate_entry = tk.Entry(tab)
        gate_entry.grid(row=13, column=1, padx=10, pady=5)

        tk.Label(tab, text="Terminal:").grid(row=14, column=0, padx=10, pady=5)
        terminal_entry = tk.Entry(tab)
        terminal_entry.grid(row=14, column=1, padx=10, pady=5)

        tk.Label(tab, text="Airline ID:").grid(row=15, column=0, padx=10, pady=5)
        airline_id_entry = tk.Entry(tab)
        airline_id_entry.grid(row=15, column=1, padx=10, pady=5)

        tk.Label(tab, text="Days of Operation:").grid(row=16, column=0, padx=10, pady=5)
        days_of_operation_entry = tk.Entry(tab)
        days_of_operation_entry.grid(row=16, column=1, padx=10, pady=5)

        # Display Area
        display_area = tk.Text(tab, height=10, width=60)
        display_area.grid(row=17, column=0, columnspan=2, padx=10, pady=10)

        # Add Flight Button
        def create_flight():
            try:
                Airport.create_flight(
                    session,
                    departure_code=departure_code_entry.get(),
                    flight_number=flight_number_entry.get(),
                    destination_code=destination_code_entry.get(),
                    departure_time=datetime.strptime(departure_time_entry.get(), "%Y-%m-%d %H:%M"),
                    arrival_time=datetime.strptime(arrival_time_entry.get(), "%Y-%m-%d %H:%M"),
                    total_seats=int(total_seats_entry.get()),
                    gate=gate_entry.get(),
                    terminal=terminal_entry.get(),
                    airline_id=int(airline_id_entry.get()),
                    days_of_operation=int(days_of_operation_entry.get())
                )
                display_area.insert(tk.END, f"Flight {flight_number_entry.get()} created successfully.\n")
            except Exception as e:
                session.rollback()
                display_area.insert(tk.END, f"Error creating flight: {e}\n")

        def delete_flight():
            try:
                Airline.delete_flight(session, flight_number=flight_number_entry) 
                display_area.insert(tk.END, f"Flight deleted successfully for Airline {name_entry.get()}.\n")
            except Exception as e:
                session.rollback()
                display_area.insert(tk.END, f"Error deleting flight: {e}\n")

        def manage_seats():
            try:
                # Query the flight by flight number
                flight = session.query(Flight).filter_by(flight_number=flight_number_entry.get()).first()
                if not flight:
                    display_area.insert(tk.END, f"No flight found with Flight Number {flight_number_entry.get()}.\n")
                    return

                # Display flight details
                display_area.insert(tk.END, f"Managing seats for Flight {flight.flight_number}:\n")

                # Query and display all seats for the flight
                seats = session.query(Seat).filter_by(flight_id=flight.id).all()
                if not seats:
                    display_area.insert(tk.END, "No seats found for this flight.\n")
                    return

                for seat in seats:
                    display_area.insert(
                        tk.END,
                        f"Seat ID: {seat.seat_id}, Seat Number: {seat.seat_number}, "
                        f"Class Type: {seat.class_type}, Availability: {'Available' if seat.is_available else 'Reserved'}, "
                        f"Seat Type: {seat.seat_type}\n"
                    )
            except Exception as e:
                display_area.insert(tk.END, f"Error managing seats: {e}\n")

        tk.Button(tab, text="Create Flight", command=create_flight).grid(row=18, column=0, columnspan=2, pady=10)
        tk.Button(tab, text="Delete Flight", command=delete_flight).grid(row=19, column=0, columnspan=2, pady=10)
        tk.Button(tab, text="Manage Seats", command=manage_seats).grid(row=20, column=0, columnspan=2, pady=10)


    def add_airline_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Airline")

        # Fields for Airline
        tk.Label(tab, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(tab)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="IATA Code:").grid(row=1, column=0, padx=10, pady=5)
        iata_entry = tk.Entry(tab)
        iata_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="ICAO Code:").grid(row=2, column=0, padx=10, pady=5)
        icao_entry = tk.Entry(tab)
        icao_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(tab, text="Headquarters:").grid(row=3, column=0, padx=10, pady=5)
        hq_entry = tk.Entry(tab)
        hq_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(tab, text="Year Founded:").grid(row=4, column=0, padx=10, pady=5)
        year_entry = tk.Entry(tab)
        year_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(tab, text="Base Airport Code:").grid(row=5, column=0, padx=10, pady=5)
        base_airport_entry = tk.Entry(tab)
        base_airport_entry.grid(row=5, column=1, padx=10, pady=5)

        # Add Airline Button
        def add_airline():
            try:
                airline = Airline(
                    name=name_entry.get(),
                    iata_code=iata_entry.get(),
                    icao_code=icao_entry.get(),
                    headquarters=hq_entry.get(),
                    year_founded=int(year_entry.get()),
                    base_airport_code=base_airport_entry.get()
                )
                session.add(airline)
                session.commit()
                messagebox.showinfo("Success", "Airline added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add airline: {e}")

        tk.Button(tab, text="Add Airline", command=add_airline).grid(row=6, column=0, columnspan=2, pady=10)


    def add_administrator_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Administrator")

        # Fields for Administrator
        tk.Label(tab, text="Admin ID:").grid(row=0, column=0, padx=10, pady=5)
        admin_id_entry = tk.Entry(tab)
        admin_id_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Name:").grid(row=1, column=0, padx=10, pady=5)
        name_entry = tk.Entry(tab)
        name_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Role:").grid(row=2, column=0, padx=10, pady=5)
        role_entry = tk.Entry(tab)
        role_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(tab, text="Contact Email:").grid(row=3, column=0, padx=10, pady=5)
        email_entry = tk.Entry(tab)
        email_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(tab, text="Management Access:").grid(row=4, column=0, padx=10, pady=5)
        has_access_var = tk.BooleanVar()
        has_access_checkbox = tk.Checkbutton(tab, variable=has_access_var)
        has_access_checkbox.grid(row=4, column=1, padx=10, pady=5)

        # Add Administrator Button
        def add_administrator():
            try:
                admin = Administrator(
                    adminID=admin_id_entry.get(),
                    name=name_entry.get(),
                    role=role_entry.get(),
                    contactEmail=email_entry.get(),
                    hasManagementAccess=has_access_var.get()
                )
                session.add(admin)
                session.commit()
                messagebox.showinfo("Success", "Administrator added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add administrator: {e}")

        tk.Button(tab, text="Add Administrator", command=add_administrator).grid(row=5, column=0, columnspan=2, pady=10)

        # Separator
        ttk.Separator(tab, orient="horizontal").grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        # Fields for Full Flight Details
        tk.Label(tab, text="Flight Number:").grid(row=7, column=0, padx=10, pady=5)
        flight_number_entry = tk.Entry(tab)
        flight_number_entry.grid(row=7, column=1, padx=10, pady=5)

        tk.Label(tab, text="Departure Code:").grid(row=8, column=0, padx=10, pady=5)
        departure_code_entry = tk.Entry(tab)
        departure_code_entry.grid(row=8, column=1, padx=10, pady=5)

        tk.Label(tab, text="Destination Code:").grid(row=9, column=0, padx=10, pady=5)
        destination_code_entry = tk.Entry(tab)
        destination_code_entry.grid(row=9, column=1, padx=10, pady=5)

        tk.Label(tab, text="Departure Time (YYYY-MM-DD HH:MM):").grid(row=10, column=0, padx=10, pady=5)
        departure_time_entry = tk.Entry(tab)
        departure_time_entry.grid(row=10, column=1, padx=10, pady=5)

        tk.Label(tab, text="Arrival Time (YYYY-MM-DD HH:MM):").grid(row=11, column=0, padx=10, pady=5)
        arrival_time_entry = tk.Entry(tab)
        arrival_time_entry.grid(row=11, column=1, padx=10, pady=5)

        tk.Label(tab, text="Total Seats:").grid(row=12, column=0, padx=10, pady=5)
        total_seats_entry = tk.Entry(tab)
        total_seats_entry.grid(row=12, column=1, padx=10, pady=5)

        tk.Label(tab, text="Gate:").grid(row=13, column=0, padx=10, pady=5)
        gate_entry = tk.Entry(tab)
        gate_entry.grid(row=13, column=1, padx=10, pady=5)

        tk.Label(tab, text="Terminal:").grid(row=14, column=0, padx=10, pady=5)
        terminal_entry = tk.Entry(tab)
        terminal_entry.grid(row=14, column=1, padx=10, pady=5)

        tk.Label(tab, text="Airline ID:").grid(row=15, column=0, padx=10, pady=5)
        airline_id_entry = tk.Entry(tab)
        airline_id_entry.grid(row=15, column=1, padx=10, pady=5)

        tk.Label(tab, text="Days of Operation:").grid(row=16, column=0, padx=10, pady=5)
        days_of_operation_entry = tk.Entry(tab)
        days_of_operation_entry.grid(row=16, column=1, padx=10, pady=5)

        tk.Label(tab, text="Reservation to be managed (ID):").grid(row=17, column=0, padx=10, pady=5)
        reservation_id_entry = tk.Entry(tab)
        reservation_id_entry.grid(row=17, column=1, padx=10, pady=5)

        # Display Area
        display_area = tk.Text(tab, height=10, width=60)
        display_area.grid(row=18, column=0, columnspan=2, padx=10, pady=10)

        # Methods for Administrator
        def create_flight():
            try:
                Administrator.create_flight(
                    session,
                    airline_id=int(airline_id_entry.get()),
                    flight_number=flight_number_entry.get(),
                    departure_code=departure_code_entry.get(),
                    destination_code=destination_code_entry.get(),
                    departure_time=datetime.strptime(departure_time_entry.get(), "%Y-%m-%d %H:%M"),
                    arrival_time=datetime.strptime(arrival_time_entry.get(), "%Y-%m-%d %H:%M"),
                    total_seats=int(total_seats_entry.get()),
                    gate=gate_entry.get(),
                    terminal=terminal_entry.get(),
                    days_of_operation=int(days_of_operation_entry.get())
                )
                display_area.insert(tk.END, f"Flight {flight_number_entry.get()} created successfully.\n")
            except Exception as e:
                session.rollback()
                display_area.insert(tk.END, f"Error creating flight: {e}\n")

        def remove_flight():
            try:
                Administrator.remove_flight(session, flight_number_entry.get())
                display_area.insert(tk.END, f"Flight {flight_number_entry.get()} removed successfully.\n")
            except Exception as e:
                session.rollback()
                display_area.insert(tk.END, f"Error removing flight: {e}\n")

        def approve_reservation():
            try:
                reservation_id = int(reservation_id_entry.get())  # Assuming reservation ID is entered in the flight number field
                Administrator.approve_reservation(session, reservation_id)
                display_area.insert(tk.END, f"Reservation {reservation_id} approved successfully.\n")
            except Exception as e:
                session.rollback()
                display_area.insert(tk.END, f"Error approving reservation: {e}\n")

        def view_all_flights():
            try:
                flights = session.query(Flight).all()
                display_area.insert(tk.END, "Flights:\n")
                for flight in flights:
                    display_area.insert(tk.END, f"{flight}\n")
            except Exception as e:
                display_area.insert(tk.END, f"Error viewing flights: {e}\n")

        def view_all_reservations():
            try:
                reservations = session.query(Reservation).all()
                display_area.insert(tk.END, "Reservations:\n")
                for reservation in reservations:
                    display_area.insert(tk.END, f"ID: {reservation.id} Passenger ID {reservation.passenger_id} Seat Number {reservation.seat_number} Status {reservation.status}\n")
            except Exception as e:
                display_area.insert(tk.END, f"Error viewing reservations: {e}\n")

        # Buttons for Administrator Methods
        tk.Button(tab, text="Create Flight", command=create_flight).grid(row=19, column=0, padx=10, pady=5)
        tk.Button(tab, text="Remove Flight", command=remove_flight).grid(row=19, column=1, padx=10, pady=5)
        tk.Button(tab, text="Approve Reservation", command=approve_reservation).grid(row=20, column=0, padx=10, pady=5)
        tk.Button(tab, text="View All Flights", command=view_all_flights).grid(row=20, column=1, padx=10, pady=5)
        tk.Button(tab, text="View All Reservations", command=view_all_reservations).grid(row=21, column=0, columnspan=2, pady=5)


    def add_flight_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Flight")

        # Fields for Flight
        tk.Label(tab, text="Flight Number:").grid(row=0, column=0, padx=10, pady=5)
        flight_number_entry = tk.Entry(tab)
        flight_number_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Departure Code:").grid(row=1, column=0, padx=10, pady=5)
        departure_code_entry = tk.Entry(tab)
        departure_code_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Destination Code:").grid(row=2, column=0, padx=10, pady=5)
        destination_code_entry = tk.Entry(tab)
        destination_code_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(tab, text="Departure Time (YYYY-MM-DD HH:MM):").grid(row=3, column=0, padx=10, pady=5)
        departure_time_entry = tk.Entry(tab)
        departure_time_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(tab, text="Arrival Time (YYYY-MM-DD HH:MM):").grid(row=4, column=0, padx=10, pady=5)
        arrival_time_entry = tk.Entry(tab)
        arrival_time_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(tab, text="Total Seats:").grid(row=5, column=0, padx=10, pady=5)
        total_seats_entry = tk.Entry(tab)
        total_seats_entry.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(tab, text="Gate:").grid(row=6, column=0, padx=10, pady=5)
        gate_entry = tk.Entry(tab)
        gate_entry.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(tab, text="Terminal:").grid(row=7, column=0, padx=10, pady=5)
        terminal_entry = tk.Entry(tab)
        terminal_entry.grid(row=7, column=1, padx=10, pady=5)

        tk.Label(tab, text="Airline ID:").grid(row=8, column=0, padx=10, pady=5)
        airline_id_entry = tk.Entry(tab)
        airline_id_entry.grid(row=8, column=1, padx=10, pady=5)

        tk.Label(tab, text="Days of Operation:").grid(row=9, column=0, padx=10, pady=5)
        days_of_operation_entry = tk.Entry(tab)
        days_of_operation_entry.grid(row=9, column=1, padx=10, pady=5)

        # Add Flight Button
        def add_flight():
            try:
                flight = Flight(
                    flight_number=flight_number_entry.get(),
                    departure_code=departure_code_entry.get(),
                    destination_code=destination_code_entry.get(),
                    departure_time=datetime.strptime(departure_time_entry.get(), "%Y-%m-%d %H:%M"),
                    arrival_time=datetime.strptime(arrival_time_entry.get(), "%Y-%m-%d %H:%M"),
                    total_seats=int(total_seats_entry.get()),
                    gate=gate_entry.get(),
                    terminal=terminal_entry.get(),
                    airline_id=int(airline_id_entry.get()),
                    days_of_operation=int(days_of_operation_entry.get())
                )
                session.add(flight)
                session.commit()
                messagebox.showinfo("Success", "Flight added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add flight: {e}")

        tk.Button(tab, text="Add Flight", command=add_flight).grid(row=10, column=0, columnspan=2, pady=10)

    def add_passenger_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Passenger")

        # Fields for Passenger
        tk.Label(tab, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(tab)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="National ID:").grid(row=1, column=0, padx=10, pady=5)
        national_id_entry = tk.Entry(tab)
        national_id_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Email:").grid(row=2, column=0, padx=10, pady=5)
        email_entry = tk.Entry(tab)
        email_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(tab, text="Phone Number:").grid(row=3, column=0, padx=10, pady=5)
        phone_number_entry = tk.Entry(tab)
        phone_number_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(tab, text="Nationality:").grid(row=4, column=0, padx=10, pady=5)
        nationality_entry = tk.Entry(tab)
        nationality_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(tab, text="VIP Status:").grid(row=5, column=0, padx=10, pady=5)
        is_vip_var = tk.BooleanVar()
        is_vip_checkbox = tk.Checkbutton(tab, variable=is_vip_var)
        is_vip_checkbox.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(tab, text="Address:").grid(row=6, column=0, padx=10, pady=5)
        address_entry = tk.Entry(tab)
        address_entry.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(tab, text="Date of Birth (YYYY-MM-DD):").grid(row=7, column=0, padx=10, pady=5)
        dob_entry = tk.Entry(tab)
        dob_entry.grid(row=7, column=1, padx=10, pady=5)

        tk.Label(tab, text="Passport Number:").grid(row=8, column=0, padx=10, pady=5)
        passport_number_entry = tk.Entry(tab)
        passport_number_entry.grid(row=8, column=1, padx=10, pady=5)

        tk.Label(tab, text="Gender:").grid(row=9, column=0, padx=10, pady=5)
        gender_entry = tk.Entry(tab)
        gender_entry.grid(row=9, column=1, padx=10, pady=5)

        tk.Label(tab, text="Frequent Flyer Number:").grid(row=10, column=0, padx=10, pady=5)
        frequent_flyer_entry = tk.Entry(tab)
        frequent_flyer_entry.grid(row=10, column=1, padx=10, pady=5)

        # Add Passenger Button
        def add_passenger():
            try:
                passenger = Passenger(
                    name=name_entry.get(),
                    national_id=national_id_entry.get(),
                    email=email_entry.get(),
                    phone_number=phone_number_entry.get(),
                    nationality=nationality_entry.get(),
                    is_vip=is_vip_var.get(),
                    address=address_entry.get(),
                    date_of_birth=dob_entry.get(),
                    passport_number=passport_number_entry.get(),
                    gender=gender_entry.get(),
                    frequent_flyer_number=frequent_flyer_entry.get()
                )
                session.add(passenger)
                session.commit()
                messagebox.showinfo("Success", "Passenger added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add passenger: {e}")

        tk.Button(tab, text="Add Passenger", command=add_passenger).grid(row=11, column=0, columnspan=2, pady=10)
    
    def add_seat_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Seat")

        # Fields for Seat
        tk.Label(tab, text="Seat Number:").grid(row=0, column=0, padx=10, pady=5)
        seat_number_entry = tk.Entry(tab)
        seat_number_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Class Type:").grid(row=1, column=0, padx=10, pady=5)
        class_type_entry = tk.Entry(tab)
        class_type_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Seat Type:").grid(row=2, column=0, padx=10, pady=5)
        seat_type_entry = tk.Entry(tab)
        seat_type_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(tab, text="Flight ID:").grid(row=3, column=0, padx=10, pady=5)
        flight_id_entry = tk.Entry(tab)
        flight_id_entry.grid(row=3, column=1, padx=10, pady=5)

        # Add Seat Button
        def add_seat():
            try:
                seat = Seat(
                    seat_number=seat_number_entry.get(),
                    class_type=class_type_entry.get(),
                    is_available=True,
                    seat_type=seat_type_entry.get(),
                    flight_id=int(flight_id_entry.get())
                )
                session.add(seat)
                session.commit()
                messagebox.showinfo("Success", "Seat added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add seat: {e}")

        tk.Button(tab, text="Add Seat", command=add_seat).grid(row=4, column=0, columnspan=2, pady=10)


    def add_reservation_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reservation")

        # Fields for Reservation
        tk.Label(tab, text="Passenger ID:").grid(row=0, column=0, padx=10, pady=5)
        passenger_id_entry = tk.Entry(tab)
        passenger_id_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Flight ID:").grid(row=1, column=0, padx=10, pady=5)
        flight_id_entry = tk.Entry(tab)
        flight_id_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Seat Number:").grid(row=2, column=0, padx=10, pady=5)
        seat_number_entry = tk.Entry(tab)
        seat_number_entry.grid(row=2, column=1, padx=10, pady=5)

        # Add Reservation Button
        def add_reservation():
            try:
                reservation = Reservation(
                    passenger_id=int(passenger_id_entry.get()),
                    flight_id=int(flight_id_entry.get()),
                    seat_number=seat_number_entry.get()
                )
                session.add(reservation)
                session.commit()
                messagebox.showinfo("Success", "Reservation added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add reservation: {e}")

        tk.Button(tab, text="Add Reservation", command=add_reservation).grid(row=3, column=0, columnspan=2, pady=10)

    def add_ticket_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Ticket")

        # Fields for Ticket
        tk.Label(tab, text="Passenger ID:").grid(row=0, column=0, padx=10, pady=5)
        passenger_id_entry = tk.Entry(tab)
        passenger_id_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Flight ID:").grid(row=1, column=0, padx=10, pady=5)
        flight_id_entry = tk.Entry(tab)
        flight_id_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Seat Number:").grid(row=2, column=0, padx=10, pady=5)
        seat_number_entry = tk.Entry(tab)
        seat_number_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(tab, text="Ticket Class:").grid(row=3, column=0, padx=10, pady=5)
        ticket_class_entry = tk.Entry(tab)
        ticket_class_entry.grid(row=3, column=1, padx=10, pady=5)

        # Add Ticket Button
        def add_ticket():
            try:
                ticket = Ticket(
                    passenger_id=int(passenger_id_entry.get()),
                    flight_id=int(flight_id_entry.get()),
                    seat_number=seat_number_entry.get(),
                    ticket_class=ticket_class_entry.get()
                )
                session.add(ticket)
                session.commit()
                messagebox.showinfo("Success", "Ticket added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add ticket: {e}")

        tk.Button(tab, text="Add Ticket", command=add_ticket).grid(row=4, column=0, columnspan=2, pady=10)

    def add_payment_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Payment")

        # Fields for Payment
        tk.Label(tab, text="Payment ID:").grid(row=0, column=0, padx=10, pady=5)
        payment_id_entry = tk.Entry(tab)
        payment_id_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Amount:").grid(row=1, column=0, padx=10, pady=5)
        amount_entry = tk.Entry(tab)
        amount_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Method:").grid(row=2, column=0, padx=10, pady=5)
        method_entry = tk.Entry(tab)
        method_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(tab, text="Reservation ID:").grid(row=3, column=0, padx=10, pady=5)
        reservation_id_entry = tk.Entry(tab)
        reservation_id_entry.grid(row=3, column=1, padx=10, pady=5)

        # Add Payment Button
        def add_payment():
            try:
                payment = Payment(
                    payment_id=payment_id_entry.get(),
                    amount=float(amount_entry.get()),
                    method=method_entry.get(),
                    status="pending",
                    payment_date=datetime.now(),
                    reservation_id=int(reservation_id_entry.get())
                )
                session.add(payment)
                session.commit()
                messagebox.showinfo("Success", "Payment added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add payment: {e}")

        tk.Button(tab, text="Add Payment", command=add_payment).grid(row=4, column=0, columnspan=2, pady=10)

    def add_promotion_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Promotion")

        # Fields for Promotion
        tk.Label(tab, text="Promo ID:").grid(row=0, column=0, padx=10, pady=5)
        promo_id_entry = tk.Entry(tab)
        promo_id_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Description:").grid(row=1, column=0, padx=10, pady=5)
        description_entry = tk.Entry(tab)
        description_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Discount Percentage:").grid(row=2, column=0, padx=10, pady=5)
        discount_entry = tk.Entry(tab)
        discount_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(tab, text="Start Date (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=5)
        start_date_entry = tk.Entry(tab)
        start_date_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(tab, text="End Date (YYYY-MM-DD):").grid(row=4, column=0, padx=10, pady=5)
        end_date_entry = tk.Entry(tab)
        end_date_entry.grid(row=4, column=1, padx=10, pady=5)

        # Add Promotion Button
        def add_promotion():
            try:
                promotion = Promotion(
                    promo_id=promo_id_entry.get(),
                    description=description_entry.get(),
                    discount_percentage=float(discount_entry.get()),
                    start_date=datetime.strptime(start_date_entry.get(), "%Y-%m-%d"),
                    end_date=datetime.strptime(end_date_entry.get(), "%Y-%m-%d")
                )
                session.add(promotion)
                session.commit()
                messagebox.showinfo("Success", "Promotion added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add promotion: {e}")

        tk.Button(tab, text="Add Promotion", command=add_promotion).grid(row=5, column=0, columnspan=2, pady=10)

    def add_luggage_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Luggage")

        # Fields for Luggage
        tk.Label(tab, text="Luggage ID:").grid(row=0, column=0, padx=10, pady=5)
        luggage_id_entry = tk.Entry(tab)
        luggage_id_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Passenger ID:").grid(row=1, column=0, padx=10, pady=5)
        passenger_id_entry = tk.Entry(tab)
        passenger_id_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Weight:").grid(row=2, column=0, padx=10, pady=5)
        weight_entry = tk.Entry(tab)
        weight_entry.grid(row=2, column=1, padx=10, pady=5)

        # Add Luggage Button
        def add_luggage():
            try:
                luggage = Luggage(
                    luggage_id=luggage_id_entry.get(),
                    passenger_id=int(passenger_id_entry.get()),
                    weight=float(weight_entry.get())
                )
                session.add(luggage)
                session.commit()
                messagebox.showinfo("Success", "Luggage added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add luggage: {e}")

        tk.Button(tab, text="Add Luggage", command=add_luggage).grid(row=3, column=0, columnspan=2, pady=10)

    def add_loyalty_program_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Loyalty Program")

        # Fields for Loyalty Program
        tk.Label(tab, text="Program Name:").grid(row=0, column=0, padx=10, pady=5)
        program_name_entry = tk.Entry(tab)
        program_name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(tab, text="Passenger ID:").grid(row=1, column=0, padx=10, pady=5)
        passenger_id_entry = tk.Entry(tab)
        passenger_id_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(tab, text="Points:").grid(row=2, column=0, padx=10, pady=5)
        points_entry = tk.Entry(tab)
        points_entry.grid(row=2, column=1, padx=10, pady=5)

        # Add Loyalty Program Button
        def add_loyalty_program():
            try:
                loyalty_program = Loyalty_program(
                    program_name=program_name_entry.get(),
                    passenger_id=int(passenger_id_entry.get()),
                    points=int(points_entry.get())
                )
                session.add(loyalty_program)
                session.commit()
                messagebox.showinfo("Success", "Loyalty Program added successfully!")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Failed to add loyalty program: {e}")

        tk.Button(tab, text="Add Loyalty Program", command=add_loyalty_program).grid(row=3, column=0, columnspan=2, pady=10)




    def add_airport_image_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Airport Image")

        # Field for Airport Code
        tk.Label(tab, text="Airport Code:").grid(row=0, column=0, padx=10, pady=5)
        airport_code_entry = tk.Entry(tab)
        airport_code_entry.grid(row=0, column=1, padx=10, pady=5)

        # Display Area for Image
        image_label = tk.Label(tab)  # Define the image_label here
        image_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Function to Query Airport and Display Image
        def display_airport_image():
            try:
                # Query the airport by code
                airport_code = airport_code_entry.get()
                airport = session.query(Airport).filter_by(code=airport_code).first()

                if not airport:
                    messagebox.showerror("Error", f"No airport found with code {airport_code}.")
                    return

                # Get the location and construct the image filename
                location = airport.location
                image_filename = f"{location}.jpg"

                # Check if the image file exists
                if not os.path.exists(image_filename):
                    messagebox.showerror("Error", f"No image found for location: {location}.")
                    return

                # Open the image using Pillow
                img = Image.open(image_filename)

                # Resize the image to fit the display area (optional)
                img = img.resize((400, 300), Image.Resampling.LANCZOS)  # Resize to 400x300 pixels

                # Convert the image to a format compatible with Tkinter
                img_tk = ImageTk.PhotoImage(img)

                # Display the image
                image_label.config(image=img_tk)
                image_label.image = img_tk  # Keep a reference to avoid garbage collection

            except Exception as e:
                messagebox.showerror("Error", f"Failed to display image: {e}")

        # Button to Trigger the Display Function
        tk.Button(tab, text="Show Image", command=display_airport_image).grid(row=1, column=0, columnspan=2, pady=10)


if __name__ == "__main__":
    app = FlightReservationApp()
    app.mainloop()