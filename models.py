from sqlalchemy import Column, Integer, String, ForeignKey, Date
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    status = Column(Integer, ForeignKey('status_name.id'), nullable=False)


class Travels(Base):
    __tablename__ = 'travels'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    from_city = Column(Integer, ForeignKey('cities.id'), nullable=False)
    to_city = Column(Integer, ForeignKey('cities.id'), nullable=False)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    distance = Column(Integer, nullable=False)
    travel_time = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    driver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    current_number_of_seats = Column(Integer, nullable=False)


class Forbidden(Base):
    __tablename__ = 'forbidden'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    forbidden_name = Column(String, nullable=False)


class ForbiddenOfTravel(Base):
    __tablename__ = 'forbidden_of_travel'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    travel_id = Column(Integer, ForeignKey('travels.id'), nullable=False)
    forbidden_id = Column(Integer, ForeignKey('forbidden.id'), nullable=False)


class StatusName(Base):
    __tablename__ = 'status_name'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    status_name = Column(String, nullable=False)


class Cars(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    car_name = Column(String, nullable=False)
    car_model = Column(String, nullable=False)
    car_year = Column(Integer, nullable=False)
    car_color = Column(String, nullable=False)
    avg_speed = Column(Integer, nullable=False)
    total_number_of_seats = Column(Integer, nullable=False)


class Ratings(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    value = Column(Integer, nullable=False)


class UserTrips(Base):
    __tablename__ = 'user_trips'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    trip_id = Column(Integer, ForeignKey('travels.id'), nullable=False)


class Cities(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    city_name = Column(String, nullable=False)
    region = Column(String, nullable=False)
