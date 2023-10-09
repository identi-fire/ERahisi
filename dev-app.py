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
from flask_session import Session
from flask_login import current_user, login_required, LoginManager, UserMixin
from datetime import datetime
#from userModule import User

# Get the current timestamp
current_timestamp = datetime.now()

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key'
logger = configure_logger()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8
"""
cursor.execute(create_table_query)

# SQL query to create the `dashboard_results` table if it doesn't exist
create_table2_query = """
    CREATE TABLE IF NOT EXISTS dashboard_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    result_text TEXT,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""
cursor.execute(create_table2_query)

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

        # Get the current timestamp
        created_at = datetime.now()

         # Retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()

         # Insert user account into the database
        try:
            cursor = db.cursor()
            insert_query = "INSERT INTO users (username, password, email,created_at) VALUES (%s, %s, %s, %s)"
            values = (username, password, email, created_at)
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
    #total_score = 0

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

        if answered_questions < 5:  # Adjust the minimum number of answered questions
            return "Please answer at least 5 questions to complete the test."

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


#@app.route('/personality-test/save-to-dashboard', methods=['POST'])
#@login_required
#def save_to_dashboard():
 #   result = request.form.get('result')

    # Store the result in the user's dashboard (you need to implement this)

   # if current_user.is_authenticated:
    #   result_text = request.form.get('result')  # Assuming you are retrieving the result from a form
    
        # Get the current timestamp
    #   created_at = datetime.now()

        # MySQL query to insert the result into the dashboard_results table

     #  insert_query = "INSERT INTO dashboard_results (result_text, user_id, created_at) VALUES (%s, %s, %s)"
      # values = (result_text, current_user.id, created_at)
    
        # Execute the insert query
       #cursor.execute(insert_query, values)
    
       # Commit the changes to the database
       #db.commit()
    
        # Close the cursor and the database connection
       #cursor.close()
       #db.close()
    
   #    return "Result saved successfully!"
    #else:
        #return "User not authenticated!"  # Handle the case when the user is not authenticated
     #   return redirect(url_for('login'))

