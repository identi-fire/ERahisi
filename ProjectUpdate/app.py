#imports
import random
from flask import Flask, request, render_template, g, redirect, jsonify, url_for, flash, session
from flask_cors import CORS
import mysql.connector
from flask_mysql_connector import MySQL
import logging
import MySQLdb.cursors, re, hashlib
import secrets
import sys
import requests
from logger_setup import configure_logger
from flask_session import Session
from datetime import datetime, timedelta
from redis import Redis
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__, static_url_path='/static')
secret_key = secrets.token_hex(16)
print("Generated Secret Key:", secret_key)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:g0thb01@localhost/personality_test'  # Update with your database connection details
db = SQLAlchemy(app)


app.secret_key = secret_key
logger = configure_logger()
logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG

#mysql
app.config['SESSION_SQLALCHEMY'] = MySQL(app)  # Check if the MySQL connection is properly initialized


# Configure Flask-Session to use Redis as the session storage
app.config['SESSION_TYPE'] = 'redis'  # Use Redis session type
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'myapp_'

# Configure Redis connection
app.config['SESSION_REDIS'] = Redis(host='localhost', port=6379, db=0)

#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
Session(app)

app.config['SESSION_TYPE'] = 'sqlalchemy'  # Use SQLAlchemy for session storage
app.config['SESSION_SQLALCHEMY'] = db  # db is the SQLAlchemy database object
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Set session lifetime to 30 minutes


# Connect to the database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="g0thb01",
    database="personality_test"
)

# Set up logging
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#logger = logging.getLogger('logs')
#logger.setLevel(logging.DEBUG)

# Configure the logging format
#formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler for all levels
#file_handler = logging.FileHandler('server.log')
#file_handler.setLevel(logging.DEBUG)
#file_handler.setFormatter(formatter)
#console_handler = logging.StreamHandler(sys.stdout)
#logger.addHandler(file_handler)
#logger.info('This is an info message')

CORS(app)

#Define the route for the home page:


GUEST_USERNAME = "guest"
GUEST_PASSWORD = "guest"

@app.route('/', methods=["GET", "POST"])
def homePage():
    user_id = session.get('guest')
    if user_id is None:
        return redirect('/login')  #
    logger.info('Session Data after login: %s', session)
    logger.info('Guest user login successful.')
    print("homepage endpoint reached...")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == GUEST_USERNAME and password == GUEST_PASSWORD:
            # Guest user login successful, redirect to the personality test page
            return render_template('personality-test.html')
    
        # For registered users, you can add logic to check the database here

        # If username/password is incorrect, render the index.html template with an error message
        error_message = "Invalid username or password. Please try again."
        return render_template('index.html', error_message=error_message)
    
    # If it's a GET request, just render the index.html template
    return render_template('index.html')

#Define the route for the personality test
@app.route('/personality_test', methods=['GET', 'POST'])
def personality_test():
    if request.method == 'POST':
        data = request.json
        return jsonify({'message': 'Personality test submitted'})  # JSON response for POST
    return render_template('personality-test.html')

#route for aboutUs
@app.route('/about')
def about():
    user_id = session.get('user_id', 'guest')
    if user_id is None:
        return redirect('/login')  #
    return render_template('about.html')

#route for contact details
@app.route('/contact')
def contact():
    return render_template('contact.html')

#route for Team Members
@app.route('/project')
def project():
    user_id = session.get('user_id', 'guest')
    if user_id is None:
        return redirect('/login')  #
    return render_template('project.html')

#route for Career
@app.route('/career')
def career():
    user_id = session.get('user_id', 'guest')
    if user_id is None:
        return redirect('/login')  #
    return render_template('career.html')
# Generate a secure secret key
#secret_key = secrets.token_hex(16)

# Use the generated secret key in your Flask application
#app.secret_key = secret_key

# Create a cursor to execute SQL queries
cursor = db.cursor()

# Create the database if it doesn't exist
create_database_query = "CREATE DATABASE IF NOT EXISTS personality_test DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci"
cursor.execute(create_database_query)

# Switch to the `personality_test` database
use_database_query = "USE `personality_test`"
cursor.execute(use_database_query)

# SQL query to create the `users` table if it doesn't exist
create_table_query = """
    CREATE TABLE IF NOT EXISTS `users` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `username` varchar(50) NOT NULL,
        `password` varchar(255) NOT NULL,
        `email` varchar(100) NOT NULL,
        `date_created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8
"""
create_table_sessions = """
CREATE TABLE IF NOT EXISTS `sessions` (
    session_id CHAR(64) PRIMARY KEY,
    session_data TEXT,
    expiry TIMESTAMP
);
"""
cursor.execute(create_table_sessions)
cursor.execute(create_table_query)

# Commit the changes to the database
db.commit()

# Close the cursor and the database connection
cursor.close()
#db.close()

GUEST_USERNAME = "guest"
GUEST_PASSWORD = "guest"

# Check if "username" and "password" POST requests exist (user submitted form)

@app.route("/login", methods=["GET", "POST"])
def login():
    
    error = None
    if request.method == 'POST': 
        username = request.form.get('username', 'guest')
        password = request.form.get('password')

        # Check if it's the guest user
        if username == GUEST_USERNAME and password == GUEST_PASSWORD:
            # Default user login successful, redirect to personality test
            session['user_id'] = 'guest'
            logger.info('Session Data after login: %s', session)
            logger.info('Guest user login successful.')
            return redirect('/personality-test')
                   
        # Retrieve the hashed password
        hash = hashlib.sha1((password + app.secret_key).encode()).hexdigest()

        try:
            cursor = db.cursor()
            select_query = "SELECT id FROM users WHERE username = %s AND password = %s"
            values = (username, hash)
            cursor.execute(select_query, values)
            result = cursor.fetchone()

            if result:
               user_id = result[0]  # Assuming 'id' is the column name for the user's ID in the database
               session['user_id'] = user_id # Store user ID in the session
               logger.info('Session Data after login: %s', session)
               logger.info('Login successful for user: %s', username)
               return redirect('/personality-test')
            else:
                # Authentication failed, redirect back to the login page with an error message
                error = 'Invalid username or password'
                logger.info('Session Data after login: %s', session)

        except mysql.connector.Error as err:
            logger.error('Error occurred during login: %s', err)
            # Log the specific database error
            return f"Error occurred during login: {err}"

    # Handle GET request, render the login form
    
    return render_template('index.html', error=error)

#logout route
@app.route("/logout", methods=["GET"])
def logout():
    session.pop('user_id', None)  # Clear user session data
    return redirect('/login')  # Redirect to your home page or login page


# User registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    successfulReg = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        email = request.form.get("email")

        # Validate that both password and email are provided
        if not (username and password and confirm_password and email):
            error = "All fields are required."
            return render_template("register.html", error=error)

        # Validate password confirmation
        if password != confirm_password:
            error = "Passwords do not match."
            return render_template("register.html", error=error)
        
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error = "Invalid email address format."
            return render_template("register.html", error=error)

        # Retrieve the hashed password
        hash = hashlib.sha1((password + app.secret_key).encode()).hexdigest()

        # Get current timestamp
        timestamp = datetime.now()

        # Insert user account into the database
        try:
            cursor = db.cursor()
            insert_query = "INSERT INTO users (username, password, email, date_created) VALUES (%s, %s, %s, %s)"
            values = (username, hash, email, timestamp)  # Use hashed password here
            cursor.execute(insert_query, values)
            db.commit()

            logging.info('Registration successful for user: %s', username)
            # Redirect to the successful registration page after successful registration
            session['user_id'] = cursor.lastrowid  # Assuming lastrowid is the ID of the newly inserted user
            logging.info('Registration successful for user: %s', username)
            successfulReg ="Registration Successful!"
            return render_template('successful-reg.html', successfulReg=successfulReg)
        
        except mysql.connector.Error as err:
            logger.error('Error occurred during registration: %s', err)
            return "Error occurred during registration."

    else:
        return render_template("register.html")

    
@app.route('/personality-test', methods=['GET', 'POST'])
def run_personality_test():
    user_id = session.get('user_id', 'guest')
       
    questions = [

        "Was science your favorite area?",

        "Did you hate any of the science subjects?",

        "did you used to attend science classes in school?",

        "did you like your teachers?",

        "Are you naturally curious about the world around you?",

        "Do you enjoy solving puzzles or brain teasers?",

        "Are you comfortable with abstract or theoretical concepts?",

        "Are you detail-oriented and meticulous in your work?",

        "are you comfortable with public speaking or presenting information to others?",

        "Are you a natural leader and enjoy taking charge of projects or teams?",

        "do you adapt to new situations or changes?",

        "Do you enjoy working independently or as part of a team?",

        "Are you patient and persistent when faced with challenges?",

        "Do you handle stress and pressure effectively?",

        "do you enjoy expressing yourself through creative outlets?",

        "Are you naturally drawn to visual aesthetics and design?",

        "Are you comfortable with experimenting and trying out new artistic techniques?",

        "Do you enjoy visiting art galleries and exhibitions?",

        "Do you engage in artistic activities during your free time?",

        "Are you passionate about storytelling and conveying emotions through art?",

        "Do you often find yourself thinking outside the box and embracing unconventional ideas?",

        "Do you enjoy working with different mediums such as paints, clay, or digital tools?",

        "Do you handle constructive criticism and feedback on your artistic work well?",

        "Are you motivated by the process of creating art rather than the end result?",

        "Do you enjoy contemplating deep philosophical questions?",

        "Are you interested in exploring the nature of knowledge and reality?",

        "Are you comfortable with abstract and complex philosophical concepts?",

        "Do you enjoy engaging in debates and discussions about moral and ethical dilemmas?",

        "Are you fascinated by the study of human existence and the meaning of life?",

        "do you critically analyze and evaluate arguments and ideas well?",

        "Do you enjoy reading philosophical texts and exploring different philosophical traditions?"
    ]
    selected_questions = []
    if request.method == 'GET':
        random.shuffle(questions)  # Shuffle the questions randomly
        #random.shuffle(questions)  # Shuffle the questions randomly
        selected_questions = random.sample(questions, 10)  # Select 10 random questions
        
        
        # Log that the personality test page is accessed
        logger.info('Accessed the personality test page.')

        # Render the personality test form
        return render_template('personality-test.html', questions=enumerate(selected_questions, start=1))
    
    print("Please answer each question with 'yes' or 'no'.")
    print("If your answer is 'no', the score for that question will be 0.")
    #total_score = 0

    error = None  # Initialize error variable to None initially
    if request.method == 'POST':
        total_score = 0
        answered_questions = 0  # Track the number of questions with answers

        for i, question in enumerate(questions, start=1):
            score = request.form.get(f'score_{i}')  # Get the score from the form

            print(f"Question {i}: Score={score}")  # Debug print

            if score is not None and score.isdigit():
                score = int(score)
                if 1 <= score <= 5:  # Ensure the score is within the valid range
                    total_score += score
                    answered_questions += 1  # Increment the count of answered questions
                else:
                    return "Invalid input! Please select a score between 1 (Strongly Disagree) and 5 (Strongly Agree)."

        print(f"Total Score: {total_score}")  # Debug print

        result_message = ""

        #if answered_questions < 5:  # Adjust the minimum number of answered questions
        #    return "Please answer at least 5 questions to complete the test."
        
        if answered_questions < 5:
            error = "Please answer at least 5 questions to complete the test."
            return render_template('error-page.html', selected_questions=selected_questions, error=error)


        if total_score < 18:  # Adjust the threshold based on the new range
            result_message = "Based on your score, you may have an inclination towards an art career."
            return render_template('art.html', result=result_message)

        elif 18 <= total_score < 25:  # Adjust the thresholds based on the new range
            result_message = "Based on your score, you may have an inclination towards a philosophical career."
            return render_template('humanities.html', result=result_message)

        elif total_score >= 25:  # Adjust the threshold based on the new range
            result_message = "Based on your score, you may have an inclination towards a science course."
            return render_template('sciencepage.html', result=result_message)



     # Handle saving and sharing options
        save_option = request.form.get('save_option')
        if save_option == 'save':
            # Save results to the database or other storage
            # You can add this logic here
            flash('Results saved.')
        elif save_option == 'share':
            # Implement sharing logic (e.g., share on social media)
            # You can add this logic here
            flash('Results shared on social media.')

    # Log the test result
    logger.info('Personality test result: %s', result_message)

        # Render the template with the test result
        #return render_template('personality_test_result.html', result=result_message)
    
     # Render the personality test form for GET requests
    #if request.method == 'GET':
     #return render_template('personality-test.html', questions=enumerate(selected_questions, start=1))            

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id', 'guest')
    if user_id is None:
        return redirect('/login')  #
    # Render dashboard page
    return render_template('dashboard.html')        

if __name__ == "__main__":
    try:
        # Log a message indicating that the Flask app is starting
        logger.info('Flask app is starting...')
        # Start the Flask development server on port 8080
        app.run(host='0.0.0.0', port=8082, debug=True)
    except Exception as e:
        # Log an error message if there's an exception during app startup
        logger.exception('Flask app failed to start: %s', str(e))


