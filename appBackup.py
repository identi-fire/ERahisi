#imports
import random
from flask import Flask, request, render_template, g, redirect, jsonify, url_for, flash, session
from flask_cors import CORS
import mysql.connector
import logging
import MySQLdb.cursors, re, hashlib
import secrets
import sys
import requests
from logger_setup import configure_logger

app = Flask(__name__, static_url_path='/static')
logger = configure_logger()

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
@app.route('/')
def homePage():
    print("homepage endpoint reached...")
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
    return render_template('about.html')

#route for contact details
@app.route('/contact')
def contact():
    return render_template('contact.html')

#route for Team Members
@app.route('/project')
def project():
    return render_template('project.html')

# Generate a secure secret key
secret_key = secrets.token_hex(8)

# Use the generated secret key in your Flask application
app.secret_key = secret_key

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
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8
"""
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
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
    
        # Create variables for easy access
        username = request.form.get('username', 'guest')
        password = request.form.get('password')

        if username == GUEST_USERNAME and password == GUEST_PASSWORD:
           # Default user login successful
           return "Login successful for Guest user!"
    
        # Retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()

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
            logger.error('Error occurred during login: %s', err)
            return "Error occurred during login."
    else: 
        return render_template("login.html")

# User registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form("email")

         # Retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()

         # Insert user account into the database
        try:
            cursor = db.cursor()
            insert_query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
            values = (username, password, email)
            cursor.execute(insert_query, values)
            db.commit()

            logging.info('Registration successful for user: %s', username)
            return "Registration successful!"
        
        except mysql.connector.Error as err:
            logger.error('Error occurred during registration: %s', err)
            return "Error occurred during registration."

    else:
        return render_template("register.html")
    
@app.route('/personality-test', methods=['GET', 'POST'])
def run_personality_test():
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
    total_score = 0

    if request.method == 'POST':
        for question in selected_questions:

            while True:

                answer = input(question + " (yes/no): ").lower()
    
                if answer == "yes":

                    while True:

                        score = input("Enter a value from 1-10 where 10 is the highest: ")

                        if score.isdigit():

                            score = int(score)

                            if 1 <= score <= 10:

                                total_score += score

                                break

                            else:

                                print("Invalid input! Please enter a number between 1 and 10.")

                        else:

                            print("Invalid input! Please enter a number between 1 and 10.")

                    break

                elif answer == "no":

                    total_score += 0

                    break

                else:

                    print("Invalid input! Please enter either 'yes' or 'no'.")

    if total_score < 50:

            result_message = "Based on your score, you may have an inclination towards an art career."
            return render_template('art.html', result=result_message)

    elif 50 <= total_score < 70:

            result_message = "Based on your score, you may have an inclination towards a philosophical career ."
            return render_template('humanities.html', result=result_message)
            
    elif total_score >= 70:
            
            result_message= "Based on your score, you may have an inclination towards a science course."
            return render_template('sciencepage.html', result=result_message)

    # Log the test result
    logger.info('Personality test result: %s', result_message)

        # Render the template with the test result
        #return render_template('personality_test_result.html', result=result_message)
    
     # Render the personality test form for GET requests
    #if request.method == 'GET':
     #return render_template('personality-test.html', questions=enumerate(selected_questions, start=1))            

@app.route('/dashboard')
def dashboard():
    # Render dashboard page
    return render_template('dashboard.html')        

if __name__ == "__main__":
    try:
        # Log a message indicating that the Flask app is starting
        logger.info('Flask app is starting...')
        app.run("localhost", 6969, debug=True)
    except Exception as e:
        # Log an error message if there's an exception during app startup
        logger.exception('Flask app failed to start: %s', str(e))
