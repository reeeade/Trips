import datetime

from flask import Flask, render_template, request, session, redirect

import database
import models

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


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
    return render_template('edit_user.html', user=user)


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
    current_username = session['username']
    user = database.db_session.query(models.User).filter_by(username=current_username).first()
    database.init_db()
    travel = (database.db_session.query(models.Travels, models.Cities, models.User, models).
              join(models.Cities, models.Cities.id == models.Travels.from_city).
              join(models.Cities, models.Cities.id == models.Travels.to_city).
              join(models.User, models.User.id == models.Travels.driver_id))
    city_list = database.db_session.query.order_by(models.Cities.city_name).all()
    from_city = request.form.get('from_city')
    to_city = request.form.get('to_city')
    if from_city:
        travel = travel.filter(models.Travels.from_city == from_city)
    if to_city:
        travel = travel.filter(models.Travels.to_city == to_city)
    travel = travel.all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
