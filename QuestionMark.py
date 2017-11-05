from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'questionmark'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


# Register Form Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=100)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO UserProfile(Email, Uname, Upass) VALUES(%s, %s, %s)", (email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM UserProfile WHERE Uname = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']
            pro_id = data['ProID']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['pro_id'] = pro_id

                flash('You are now logged in', 'success')
                return redirect(url_for('profile'))
            else:
                error = 'Invalid login'
                return render_template('auth/login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('auth/login.html', error=error)

    return render_template('auth/login.html')


# Answer Form Class
class AnswerForm(Form):
    body = TextAreaField('AnsBody', [validators.Length(min=30)])


# Add Answer
@app.route('/add_answer', methods=['GET', 'POST'])
def add_answer():
    form = AnswerForm(request.form)
    if request.method == 'POST' and form.validate():
        ansbody = form.body.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO Answers(Ans) VALUES(%s)",(ansbody))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Answer Posted', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_answer.html', form=form)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='localhost', port=4444, debug=True)
