from flask import Flask, redirect, session, request, render_template, url_for, flash
import pymysql
from db import create_db
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'hayst08'

# Upload folder for profile images
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


create_db()  # Ensure the database and table are created

# MySQL Configuration   
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'weekone_db'
cred = {
    'host': DB_HOST,
    'user': DB_USER,
    'pw': DB_PASSWORD,
    'db_name': DB_NAME
}

def connection():
    try:
        conn = pymysql.connect(
            host=cred['host'],
            user=cred['user'],
            password=cred['pw'],
            db=cred['db_name']
        )
        return conn
    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Allowed file extensions for images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'logged' in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connection()
        if conn is not None:
            with conn.cursor() as cur:
                # Check if the username exists in the database
                cur.execute("SELECT id, username FROM users WHERE username=%s", (username,))
                user = cur.fetchone()

                if not user:
                    flash('Username is not associated with any account. Please register.')
                    return render_template('login.html')
        else:
            flash("Database connection failed. Please try again later.")
            return render_template('login.html')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Match the names from your form
        name = request.form['name']
        bday = request.form['birthday']  # Changed from 'bday'
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
        image = request.files['image']  # Changed from 'image'

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            filename = f"{username}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(file_path)
            image_path = f'uploads/{filename}'
        else:
            flash('Invalid image file. Allowed types: PNG, JPG, JPEG, GIF')
            return redirect(url_for('signup'))

        conn = connection()
        if conn is None:
            flash("Database connection failed. Please try again later.", "error")
            return redirect(url_for("signup"))

        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", [username])
                account = cur.fetchone()
                if account:
                    flash("Username is already registered!")
                    return redirect(url_for("signup"))
                else:
                    cur.execute(
                        "INSERT INTO users (name, birthday, address, username, password) VALUES (%s, %s, %s, %s, %s)",
                        (name, bday, address, username, password)
                    )
                    conn.commit()
                    flash("Account created successfully!")
                    return redirect(url_for("login"))
        except pymysql.Error as e:
            flash(f"Database error: {e}")
            return redirect(url_for("signup"))
        finally:
            conn.close()
    return render_template('signup.html')


@app.route('/profile')
def profile():
    info = {
        'name': 'Daisy Lou Montante',
        'age': 21,
        'address': 'Kauswagan, Cabadbaran City',
    }
    return render_template('dashboard.html', information=info)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)