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
def hello_world():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')






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

        #Close connection
        cur.close()

        flash('Answer Posted', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_answer.html', form=form)

if __name__ == '__main__':
    app.run(host='localhost', port=4444, debug=True)
