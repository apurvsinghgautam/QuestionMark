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
    return render_template('members.html')


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=50)])
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
        name = form.name.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO UserProfile(Email, Uname, Upass) VALUES(%s, %s, %s)", (email, name, password))

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
        email = request.form['email']
        password_candidate = request.form['password']
        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM UserProfile WHERE Email = %s", [email])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['Upass']
            pro_id = data['ProID']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['pro_id'] = pro_id
                session['email'] = email

                flash('You are now logged in', 'success')
                return redirect(url_for('profile'))
            else:
                error = 'Invalid login'
                return render_template('auth/login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'User not found'
            return render_template('auth/login.html', error=error)

    return render_template('auth/login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/profile')
@is_logged_in
def profile():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Uname FROM userprofile WHERE Email=%s", [session['email']])
    names = cur.fetchone()
    return render_template('profile.html', names=names)


# Question Form Class
class QuestionForm(Form):
    quesbody = TextAreaField('QuesBody', [validators.Length(min=10)])


# Add Question
@app.route('/add_question', methods=['GET', 'POST'])
@is_logged_in
def add_question():
    form = QuestionForm(request.form)
    if request.method == 'POST' and form.validate():
        quesbody = form.quesbody.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO Questions(Ques) VALUES(%s)", (quesbody))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Question Posted', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_question.html', form=form)


# Answer Form Class
class AnswerForm(Form):
    body = TextAreaField('AnsBody', [validators.Length(min=30)])


# Add Answer
@app.route('/add_answer', methods=['GET', 'POST'])
@is_logged_in
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


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Ques FROM questions")
    questions = cur.fetchall()
    cur.execute("SELECT Uname,Ans,AID FROM answers,userprofile WHERE answers.ProID=userprofile.ProID")
    ansname = cur.fetchall()
    # cur.execute("SELECT Ans FROM answers,userprofile WHERE answers.ProID=userprofile.ProID")
    # answers = cur.fetchall()
    cur.execute("SELECT COUNT(*) as cnt FROM upvotes GROUP BY AID",request['answerID'])
    upvote = cur.fetchone()
    # cur.execute("INSERT INTO (AID) VALUES %s", aid)
    print(upvote['cnt'])
    cur.execute("INSERT INTO upvotes VALUES %s",request['answerID'])

    return render_template('dashboard.html', upvote=upvote, questions=questions, ansname=ansname)


@app.route('/setsession/<name>')
def setsession(name):
    session['name'] = name
    return redirect('getsession')


app.route('/getsession')
def getsession():
    name = session['name']
    return str(name)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='localhost', port=4444, debug=True)
