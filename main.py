from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import os
from werkzeug.utils import secure_filename
from datetime import date

app = Flask(__name__)
app.secret_key = 'desangieee'

# MySQL configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="week"
)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['username'] = username
            return redirect(url_for('profile', username=username))  # Redirect to profile page
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome, {session['username']}! <a href='{url_for('logout')}'>Logout</a>"
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Add a register route for the register link
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        birthday = request.form['birthday']
        username = request.form['username']
        password = request.form['password']
        image_file = request.files['image']

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_file.save(image_path)
        else:
            flash('Invalid image file.', 'danger')
            return render_template('register.html')

        cursor = db.cursor()
        cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username already exists', 'danger')
        else:
            cursor.execute(
                "INSERT INTO user (name, address, image, birthday, username, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, address, filename, birthday, username, password)
            )
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            cursor.close()
            return redirect(url_for('login'))
        cursor.close()
    return render_template('register.html')

@app.route('/profile/<username>')
def profile(username):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, address, image, birthday FROM user WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('dashboard'))

    # Calculate age from birthday
    if user['birthday']:
        today = date.today()
        bday = user['birthday']
        age = today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))
    else:
        age = 'N/A'

    return render_template('profile.html', name=user['name'], address=user['address'], age=age, image=user['image'])

if __name__ == '__main__':
    app.run(debug=True)