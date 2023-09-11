
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import *
from .views import *
import random, string
from flask_mail import Message
from . import mail



auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if 'username' in session:
        return redirect(url_for('views.user_home'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']



            if validate_login(username, password):
                session['username'] = username
                session['logged_in'] = True
                print(session['username'])
                return redirect(url_for('views.user_home'))
            else:
                flash('Invalid username or password', 'error')
                return redirect(url_for('auth.login'))
        else:
            return render_template('login.html')

@auth.route('/forgotpassword')
def forgotpassword():
    #get data and send email here
    return render_template("/forgotpassword.html")


@auth.route('/resetpassword/<code>', methods=['GET', 'POST'])
def resetpassword(code):
    if request.method == 'POST':
        # Handle password reset form submission
        result = get_code(code)

        if result:

            new_password = request.form['pass1']
            confirm_password = request.form['pass2']
        
            if new_password != confirm_password:
                flash('Passwords do not match.')
                return render_template('resetpassword.html', code=code)
            else:
                update_password_by_email(get_email_by_code(code), new_password)
                remove_code(code)

                return redirect(url_for('auth.login'))
        
        flash('Password reset successfully.')
        return redirect(url_for('auth.login'))
    
    # GET request
    return render_template('resetpassword.html', code=code)

@auth.route('/sendcode', methods=['POST'])
def sendcode():
    #api
    email = request.form['email']

    code = generate_code(8)

    cursor = db.cursor()
    sql = "INSERT INTO code (email, code) VALUES (%s, %s)"
    values = (email, code)
    cursor.execute(sql, values)
    db.commit()

    send_email(email, code)

    flash('A password reset code has been sent to your email.')
    return render_template('forgotpassword.html')


def generate_code(length):
    characters = string.digits
    code = ''.join(random.choice(characters) for _ in range(length))
    return code

def send_email(email, code):

    reset_link = url_for('auth.resetpassword', code=code, _external=True)
    msg = Message('Password Reset Code', sender='iophelperbot@gmail.com', recipients=[email])
    msg.body = f'Your password reset code is: {reset_link}'
    mail.send(msg)



@auth.route('/logout')
def logout():
    #to do logout/session
    session.pop('username', None)
    session['logged_in'] = False
    return render_template("/index.html")

@auth.route('/signup', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('views.user_home'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            password2 = request.form['passwordConfirm']
            email = request.form['email']

            # Check if the username already exists
            if user_exists(username):
                flash('Username already exists. Please choose a different username.', 'error')
                return redirect(url_for('auth.register'))
            elif len(password) <= 8:
                flash('Password is too short, please enter a new password')
                return redirect(url_for('auth.register'))
            elif password == password2:
                # Create a new user
                add_user(username, password, email)

                flash('Registration successful. Please log in.')
                return redirect(url_for('auth.login'))
        else:
            return render_template('signup.html')

def is_user_logged_in():
    return True if 'username' in session else False



