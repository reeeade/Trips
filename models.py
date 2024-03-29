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

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'surname': self.surname,
            'phone_number': self.phone_number,
            'birthday': self.birthday,
            'status': self.status
        }


class Travels(Base):
    __tablename__ = 'travels'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    from_city = Column(Integer, ForeignKey('cities.id'), nullable=False)
    to_city = Column(Integer, ForeignKey('cities.id'), nullable=False)
    description = Column(String)
    date = Column(Date, nullable=False)
    distance = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    driver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'from_city': self.from_city,
            'to_city': self.to_city,
            'description': self.description,
            'date': self.date,
            'distance': self.distance,
            'price': self.price,
            'driver_id': self.driver_id,
            'car_id': self.car_id
        }


class Forbidden(Base):
    __tablename__ = 'forbidden'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    forbidden_name = Column(String, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'forbidden_name': self.forbidden_name
        }


class ForbiddenOfTravel(Base):
    __tablename__ = 'forbidden_of_travel'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    travel_id = Column(Integer, ForeignKey('travels.id'), nullable=False)
    forbidden_id = Column(Integer, ForeignKey('forbidden.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'travel_id': self.travel_id,
            'forbidden_id': self.forbidden_id
        }


class StatusName(Base):
    __tablename__ = 'status_name'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    status_name = Column(String, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'status_name': self.status_name
        }


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

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'car_name': self.car_name,
            'car_model': self.car_model,
            'car_year': self.car_year,
            'car_color': self.car_color,
            'avg_speed': self.avg_speed,
            'total_number_of_seats': self.total_number_of_seats
        }


class Ratings(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    value = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'value': self.value
        }


class UserTrips(Base):
    __tablename__ = 'user_trips'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    trip_id = Column(Integer, ForeignKey('travels.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trip_id': self.trip_id
        }


class Cities(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    city_name = Column(String, nullable=False)
    region = Column(String, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'city_name': self.city_name,
            'region': self.region
        }
