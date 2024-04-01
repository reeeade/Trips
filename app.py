import datetime
import random

from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy.orm import aliased

import database
import models

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'


@app.route('/')
def hello_world():
    return redirect('/travels')


@app.route('/register', methods=['GET', 'POST'])
def register():
    database.init_db()
    status_list = database.db_session.query(models.StatusName).all()
    if request.method == 'GET':
        return render_template('register.html', status_list=status_list)
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm')
    if password != confirm_password:
        return render_template('register.html', message='Passwords do not match', status_list=status_list)
    status = request.form.get('status')
    email = request.form.get('email')
    if database.db_session.query(models.User).filter_by(email=email).first() is not None:
        return render_template('register.html', message='Email already in use', status_list=status_list)
    if database.db_session.query(models.User).filter_by(username=username).first() is not None:
        return render_template('register.html', message='Username already in use', status_list=status_list)
    name = request.form.get('name')
    surname = request.form.get('surname')
    phone_number = request.form.get('phone_number')
    birthday_str = request.form.get('birthday')
    birthday = datetime.datetime.strptime(birthday_str, '%Y-%m-%d').date()
    user = models.User(username=username, password=password, email=email, name=name, surname=surname,
                       phone_number=phone_number, birthday=birthday, status=status)
    database.db_session.add(user)
    database.db_session.commit()
    rating = models.Ratings(user_id=user.id, value=0)
    database.db_session.add(rating)
    database.db_session.commit()

    return render_template('login.html', message='User created successfully')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm')
    if password != confirm_password:
        return render_template('login.html', message='Passwords do not match')
    database.init_db()
    user = database.db_session.query(models.User).filter_by(username=username).first()
    if user is not None and user.password == password:
        session['username'] = username
        return redirect('/edit_user')
    if user is not None and user.password != password:
        return render_template('login.html', message='Passwords is not correct')
    if user is None:
        return render_template('login.html', message='Username is not correct')
    else:
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


@app.route('/delete_user', methods=['GET'])
def delete_user():
    current_username = session['username']
    database.init_db()
    user = database.db_session.query(models.User).filter_by(username=current_username).first()
    database.db_session.delete(user)
    database.db_session.commit()
    return render_template('login.html', message='User deleted successfully')


@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    current_username = session.get('username')
    database.init_db()
    user = database.db_session.query(models.User).filter_by(username=current_username).first()
    user_rating = database.db_session.query(models.Ratings.value).filter_by(user_id=user.id).first()[0]
    if user is None:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('edit_user.html', user=user, user_rating=user_rating)
    name = request.form.get('name')
    surname = request.form.get('surname')
    phone_number = request.form.get('phone_number')
    birthday_str = request.form.get('birthday')
    birthday = datetime.datetime.strptime(birthday_str, '%Y-%m-%d').date()
    user.name = name
    user.surname = surname
    user.phone_number = phone_number
    user.birthday = birthday
    database.db_session.commit()
    message = 'User updated successfully'
    return render_template('edit_user.html', user=user, message=message, user_rating=user_rating)


@app.route('/edit_car', methods=['GET', 'POST'])
def edit_car():
    current_username = session['username']
    database.init_db()
    user = database.db_session.query(models.User).filter_by(username=current_username).first()
    car = database.db_session.query(models.Cars).filter_by(user_id=user.id).first()
    if request.method == 'GET':
        return render_template('edit_car.html', user=user, car=car)
    car_name = request.form.get('car_name')
    car_model = request.form.get('car_model')
    car_year = request.form.get('car_year')
    car_color = request.form.get('car_color')
    avg_speed = request.form.get('avg_speed')
    total_number_of_seats = request.form.get('total_seats')
    if car:
        car.car_name = car_name
        car.car_model = car_model
        car.car_year = car_year
        car.car_color = car_color
        car.avg_speed = avg_speed
        car.total_number_of_seats = total_number_of_seats
    else:
        car = models.Cars(user_id=user.id, car_name=car_name, car_model=car_model, car_year=car_year,
                          car_color=car_color, avg_speed=avg_speed, total_number_of_seats=total_number_of_seats)
        database.db_session.add(car)
    database.db_session.commit()
    message = 'Car updated successfully'
    return render_template('edit_user.html', user=user, message=message)


@app.route('/edit_password', methods=['GET', 'POST'])
def edit_password():
    current_username = session['username']
    database.init_db()
    user = database.db_session.query(models.User).filter_by(username=current_username).first()
    if request.method == 'GET':
        return render_template('edit_password.html', user=user)
    old_password = request.form.get('old_password')
    password = request.form.get('new_password')
    confirm_password = request.form.get('confirm')
    if password != confirm_password:
        return render_template('edit_password.html', message='Passwords do not match')
    if user.password != old_password:
        return render_template('edit_password.html', message='Old password is not correct')
    user.password = password
    database.db_session.commit()
    return render_template('edit_user.html', user=user, message='Password changed successfully')


@app.route('/travels', methods=['GET', 'POST'])
def travels():
    user = None
    current_username = session.get('username')
    if current_username:
        user = database.db_session.query(models.User).filter_by(username=current_username).first()
    database.init_db()
    city_list = database.db_session.query(models.Cities).order_by(models.Cities.city_name).all()
    region_set = database.db_session.query(models.Cities.region).order_by(models.Cities.region).distinct().all()
    region_set = [region[0] for region in region_set]
    if request.method == 'GET':
        return render_template('travels.html', region_set=region_set, city_list=city_list, user=user)
    from_city = request.form.get('from_city')
    to_city = request.form.get('to_city')
    date = request.form.get('date')
    message = 0
    return redirect(url_for('all_find_travels', from_city=from_city, to_city=to_city, date=date, message=message))


@app.route('/all_find_travels', methods=['GET', 'POST'])
def all_find_travels():
    database.init_db()
    from_city_alias = aliased(models.Cities)
    to_city_alias = aliased(models.Cities)
    current_username = session.get('username')
    user = None
    if current_username:
        user = database.db_session.query(models.User).filter_by(username=current_username).first()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        trip_id = request.form.get('trip_id')
        trip_in_user_trip = database.db_session.query(models.UserTrips).filter_by(user_id=user_id,
                                                                                  trip_id=trip_id).first()
        if trip_in_user_trip is None:
            user_trip = models.UserTrips(user_id=user_id, trip_id=trip_id)
            database.db_session.add(user_trip)
            database.db_session.commit()
            travel = database.db_session.query(models.Travels).filter_by(id=trip_id).first()
            travel.current_number_of_seats += 1
            database.db_session.commit()
            return redirect(url_for('all_find_travels', message=2))
        else:
            return redirect(url_for('all_find_travels', message=3))
    travel_query = (database.db_session.query(models.Travels, from_city_alias, to_city_alias, models.User, models.Cars,
                                              models.Ratings)
                    .join(from_city_alias, from_city_alias.id == models.Travels.from_city)
                    .join(to_city_alias, to_city_alias.id == models.Travels.to_city)
                    .join(models.User, models.User.id == models.Travels.driver_id)
                    .join(models.Cars, models.Cars.id == models.Travels.car_id)
                    .join(models.Ratings, models.Ratings.user_id == models.Travels.driver_id))

    from_city = request.args.get('from_city')
    to_city = request.args.get('to_city')
    date = request.args.get('date')
    message = request.args.get('message')
    if message:
        message = int(message)
    if message == 1:
        message = 'Trip added successfully'
    if message == 2:
        message = 'You have successfully signed up for a trip'
    if message == 3:
        message = 'You have already signed up for this trip'
    if from_city:
        travel_query = travel_query.filter(models.Travels.from_city == from_city)
    if to_city:
        travel_query = travel_query.filter(models.Travels.to_city == to_city)
    if date:
        travel_query = travel_query.filter(models.Travels.date == date)
    trips = travel_query.all()

    travels_data = []
    for travel in trips:
        travel_time = round(travel[0].distance / travel[4].avg_speed, 2)
        travel_data = {'travel_time': travel_time, 'forbidden_of_trip': []}
        forbidden_of_trip = database.db_session.query(models.ForbiddenOfTravel.list_of_forbidden_id).filter_by(
            travel_id=travel[0].id).first()
        if forbidden_of_trip is not None:
            forbidden_of_trip = forbidden_of_trip[0].replace('{', '').replace('}', '').split(',')
            for forbidden_id in forbidden_of_trip:
                forbid = database.db_session.query(models.Forbidden).filter_by(id=forbidden_id).first()
                travel_data['forbidden_of_trip'].append(forbid.forbidden_name)
        for obj in travel:
            if hasattr(obj, 'to_dict'):
                obj_dict = obj.to_dict()
                for key, value in obj_dict.items():
                    if key in travel_data:
                        travel_data[f"{obj.__class__.__name__}_{key}"] = value
                    else:
                        travel_data[key] = value
        if travel[0].current_number_of_seats == travel[4].total_number_of_seats:
            travel_data = None
        else:
            travels_data.append(travel_data)

    return render_template('all_find_travels.html', travels=travels_data, message=message, user=user)


@app.route('/new_trip', methods=['GET', 'POST'])
def new_trip():
    current_username = session.get('username')
    user = database.db_session.query(models.User).filter_by(username=current_username).first()
    car = database.db_session.query(models.Cars).filter_by(user_id=user.id).first()
    database.init_db()
    from_cities = database.db_session.query(models.Cities).all()
    to_cities = database.db_session.query(models.Cities).all()
    random.shuffle(from_cities)
    random.shuffle(to_cities)
    list_of_forbidden = database.db_session.query(models.Forbidden).all()
    if request.method == 'GET':
        return render_template('new_trip.html', from_cities=from_cities, to_cities=to_cities,
                               list_of_forbidden=list_of_forbidden)
    if car is None:
        return render_template('new_trip.html', from_cities=from_cities, to_cities=to_cities,
                               message='Add the car first', list_of_forbidden=list_of_forbidden)
    from_city = request.form.get('from_city')
    to_city = request.form.get('to_city')
    date = request.form.get('date')
    distance = request.form.get('distance')
    price = request.form.get('price')
    description = request.form.get('description')
    forbidden = request.form.getlist('forbidden')
    driver_id = user.id
    car_id = car.id
    travel = models.Travels(from_city=from_city, to_city=to_city, date=date, price=price, driver_id=driver_id,
                            car_id=car_id, description=description, distance=distance, current_number_of_seats=0)
    database.db_session.add(travel)
    database.db_session.commit()
    message = 1
    forbidden_of_trip = models.ForbiddenOfTravel(travel_id=travel.id, list_of_forbidden_id=forbidden)
    database.db_session.add(forbidden_of_trip)
    database.db_session.commit()
    return redirect(url_for('all_find_travels', from_city=from_city, to_city=to_city, date=date, message=message))


@app.route('/user_trips', methods=['GET', 'POST'])
def user_trips():
    current_username = session.get('username')
    user = database.db_session.query(models.User).filter_by(username=current_username).first()
    message = request.args.get('message')
    if message:
        message = int(message)
        if message == 1:
            message = 'Trip delete successfully'
        if message == 2:
            message = 'You successfully canceled your trip'
        if message == 3:
            message = 'You have successfully rated the user'
        if message == 4:
            message = 'You have updated your rating'
    if user.status == 1:
        data_for_template = []
        trips = database.db_session.query(models.Travels).filter_by(driver_id=user.id).all()
        for i in range(len(trips)):
            from_city = database.db_session.query(models.Cities.city_name).filter_by(id=trips[i].from_city).first()[0]
            to_city = database.db_session.query(models.Cities.city_name).filter_by(id=trips[i].to_city).first()[0]
            travel = {'id': trips[i].id, 'from_city': from_city, 'to_city': to_city,
                      'date': trips[i].date, 'passengers': []}

            passengers = database.db_session.query(models.UserTrips, models.User, models.Ratings).join(
                models.User, models.UserTrips.user_id == models.User.id).join(
                models.Ratings, models.Ratings.user_id == models.User.id)
            passengers = passengers.filter(models.UserTrips.trip_id == trips[i].id).all()
            for j in range(len(passengers)):
                passenger = {'number': j + 1, 'user_id': passengers[j][1].id, 'name': passengers[j][1].name,
                             'surname': passengers[j][1].surname,
                             'phone_number': passengers[j][1].phone_number, 'rating': passengers[j][2].value}
                travel['passengers'].append(passenger)
            data_for_template.append(travel)
        return render_template('user_trips.html', data_for_template=data_for_template, user=user, message=message)
    else:
        data_for_template = []
        user_trips_obj = (database.db_session.query(models.UserTrips, models.Travels).join(
            models.Travels, models.UserTrips.trip_id == models.Travels.id))
        user_trips_obj = user_trips_obj.filter(models.UserTrips.user_id == user.id).all()
        for i in range(len(user_trips_obj)):
            from_city = database.db_session.query(models.Cities.city_name).filter_by(
                id=user_trips_obj[i][1].from_city).first()[0]
            to_city = database.db_session.query(models.Cities.city_name).filter_by(
                id=user_trips_obj[i][1].to_city).first()[0]
            driver = (database.db_session.query(models.User, models.Cars, models.Ratings).join(
                models.User, models.Cars.user_id == models.User.id).join(
                models.Ratings, models.Ratings.user_id == models.User.id))
            driver = driver.filter(models.User.id == user_trips_obj[i][1].driver_id).first()
            travel = {'id': user_trips_obj[i][1].id, 'from_city': from_city, 'to_city': to_city,
                      'date': user_trips_obj[i][1].date, 'driver_name': driver[0].name, 'driver_id': driver[0].id,
                      'driver_surname': driver[0].surname, 'driver_phone_number': driver[0].phone_number,
                      'driver_car_name': driver[1].car_name, 'driver_car_model': driver[1].car_model,
                      'driver_car_color': driver[1].car_color, 'rating': driver[2].value}
            data_for_template.append(travel)
        return render_template('user_trips.html', data_for_template=data_for_template, user=user, message=message)


@app.route('/delete_trip', methods=['GET', 'POST'])
def delete_trip():
    current_username = session.get('username')
    user = database.db_session.query(models.User).filter_by(username=current_username).first()
    if user.status == 1:
        trip_id = request.form.get('trip_id')
        trip = database.db_session.query(models.Travels).filter_by(id=trip_id).first()
        database.db_session.delete(trip)
        database.db_session.commit()
        message = 1
        return redirect(url_for('user_trips', message=message))
    else:
        trip_id = request.form.get('trip_id')
        user_trip = database.db_session.query(models.UserTrips).filter_by(trip_id=trip_id, user_id=user.id).first()
        database.db_session.delete(user_trip)
        travel = database.db_session.query(models.Travels).filter_by(id=trip_id).first()
        travel.current_number_of_seats -= 1
        database.db_session.commit()
        message = 2
        return redirect(url_for('user_trips', message=message))


@app.route('/rate/<user_id>', methods=['GET', 'POST'])
def rate(user_id):
    current_username = session.get('username')
    current_user = database.db_session.query(models.User).filter_by(username=current_username).first()
    rated_user = database.db_session.query(models.User).filter_by(id=user_id).first()
    if request.method == 'GET':
        return render_template('rate.html', rated_user=rated_user)
    if current_user.id == user_id:
        return render_template('rate.html', rated_user=rated_user, message='You cannot rate yourself')
    rating_obj = models.UsersRatings.query.filter_by(user_who_rated_id=current_user.id,
                                                     user_to_whom_rated_id=user_id).first()
    message = 3
    rating = request.form.get('rating')
    if rating_obj:
        rating_obj.rating = rating
        message = 4
    else:
        rating_obj = models.UsersRatings(user_who_rated_id=current_user.id, user_to_whom_rated_id=user_id,
                                         rating=rating)
        database.db_session.add(rating_obj)
    final_rating = database.db_session.query(models.UsersRatings.rating).filter_by(
        user_to_whom_rated_id=user_id).all()
    final_rating = round(sum(int(*i) for i in final_rating) / len(final_rating), 1)
    user_rating = models.Ratings.query.filter_by(user_id=user_id).first()
    user_rating.value = final_rating
    database.db_session.commit()

    return redirect(url_for('user_trips', message=message))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
