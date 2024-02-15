import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="database1"
)

cursor = db.cursor()

def create_users_table():
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        db.commit()
    except mysql.connector.Error as err:
        print("Error:", err)

create_users_table()

def create_images_table():
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                data LONGBLOB NOT NULL
            )
        """)
        db.commit()
    except mysql.connector.Error as err:
        print("Error:", err)

create_images_table()

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            return redirect(url_for('upload'))
        else:
            return render_template('login.html', message='Invalid username or password.')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return render_template('signup.html', message='Error: {}'.format(err))
    return render_template('signup.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' in session:
        if request.method == 'POST':
            # Check if the POST request has the file part
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an empty file without a filename
            if file.filename == '':
                return redirect(request.url)
            if file:
                # Save the uploaded file to MySQL
                filename = secure_filename(file.filename)
                file_data = file.read()
                cursor.execute("INSERT INTO images (filename, data) VALUES (%s, %s)", (filename, file_data))
                db.commit()
                return 'File uploaded successfully!'
        return render_template('upload.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)