#imports
import random
from flask import Flask, request, render_template, g, url_for
import flask
from flask_cors import CORS
import mysql.connector
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
error_logger = logging.getLogger('error')

# Configure the logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler for logging to a file
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(formatter)

# Add the file handler to the app's logger
app.logger.addHandler(file_handler)

CORS(app)

# Connect to the database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="g0thb01",
    database="personality_test"
)

# Home page route
@app.route("/")
def home():
    logging.info('User accessed home page')
    return render_template("index.html")

# User registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Insert user account into the database
        try:
            cursor = db.cursor()
            insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            values = (username, password)
            cursor.execute(insert_query, values)
            db.commit()

            logging.info('Registration successful for user: %s', username)
            return "Registration successful!"
        
        except mysql.connector.Error as err:
            error_logger.error('Error occurred during registration: %s', err)
            return "Error occurred during registration."

    else:
        return render_template("register.html")

# User login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the username and password match in the database
    try:    
        cursor = db.cursor()
        select_query = "SELECT * FROM users WHERE username = %s AND password = %s"
        values = (username, password)
        cursor.execute(select_query, values)
        result = cursor.fetchone()

        if result:
            logging.info('Login successful for user: %s', username)
            return "Login successful!"
        
        else:
            logging.warning('Invalid login attempt for user: %s', username)
            return "Invalid username or password."
        
    except mysql.connector.Error as err:
            error_logger.error('Error occurred during login: %s', err)
            return "Error occurred during login."
        
    else:
        return render_template("login.html")
    
if __name__ == "__main__":
    app.run()