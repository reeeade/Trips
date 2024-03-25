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
        if 'login' not in session:
            return redirect('/login')
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
        return redirect('/')
    else:
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
