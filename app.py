import datetime
import random

from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import select
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
    message = None
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
    current_username = session['username']
    database.init_db()
    user = database.db_session.query(models.User).filter_by(username=current_username).first()
    if request.method == 'GET':
        return render_template('edit_user.html', user=user)
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
    return render_template('edit_user.html', user=user, message=message)


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
    total_seats = request.form.get('total_seats')
    car.car_name = car_name
    car.car_model = car_model
    car.car_year = car_year
    car.car_color = car_color
    car.avg_speed = avg_speed
    car.number_of_seats = total_seats
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
    return redirect(url_for('all_find_travels', from_city=from_city, to_city=to_city, date=date))


@app.route('/all_find_travels', methods=['GET', 'POST'])
def all_find_travels():
    database.init_db()
    from_city_alias = aliased(models.Cities)
    to_city_alias = aliased(models.Cities)

    travel_query = (database.db_session.query(models.Travels, from_city_alias, to_city_alias, models.User, models.Cars)
                    .join(from_city_alias, from_city_alias.id == models.Travels.from_city)
                    .join(to_city_alias, to_city_alias.id == models.Travels.to_city)
                    .join(models.User, models.User.id == models.Travels.driver_id)
                    .join(models.Cars, models.Cars.id == models.Travels.car_id))

    from_city = request.args.get('from_city')
    to_city = request.args.get('to_city')
    date = request.args.get('date')
    message = int(request.args.get('message'))

    if message == 1:
        message = 'Trip added successfully'
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
        travel_data = {'travel_time': travel_time}
        for obj in travel:
            if hasattr(obj, 'to_dict'):
                obj_dict = obj.to_dict()
                for key, value in obj_dict.items():
                    if key in travel_data:
                        travel_data[f"{obj.__class__.__name__}_{key}"] = value
                    else:
                        travel_data[key] = value
        travels_data.append(travel_data)

    return render_template('all_find_travels.html', travels=travels_data, message=message)


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
    if request.method == 'GET':
        return render_template('new_trip.html', from_cities=from_cities, to_cities=to_cities)
    from_city = request.form.get('from_city')
    to_city = request.form.get('to_city')
    date = request.form.get('date')
    distance = request.form.get('distance')
    price = request.form.get('price')
    description = request.form.get('description')
    driver_id = user.id
    car_id = car.id
    travel = models.Travels(from_city=from_city, to_city=to_city, date=date, price=price, driver_id=driver_id,
                            car_id=car_id, description=description, distance=distance)
    database.db_session.add(travel)
    database.db_session.commit()
    message = 1
    return redirect(url_for('all_find_travels', from_city=from_city, to_city=to_city, date=date, message=message))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
