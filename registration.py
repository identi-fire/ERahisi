#imports
import random
from flask import Flask, request, render_template, g, redirect, jsonify, url_for, flash, session
from flask_cors import CORS
import mysql.connector
import logging
import bcrypt
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import MySQLdb.cursors, re, hashlib
import secrets
import sys

app = Flask(__name__, static_url_path='/static')

# Generate a secure secret key
secret_key = secrets.token_hex(8)

# Use the generated secret key in your Flask application
app.secret_key = secret_key

# Connect to the database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="g0thb01",
    database="personality_test"
)

# Create a cursor to execute SQL queries
cursor = db.cursor()

# Switch to the `personality_test` database
use_database_query = "USE `personality_test`"
cursor.execute(use_database_query)

# Commit the changes to the database
db.commit()

# User registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        # Check if the provided email address is valid
        if not is_valid_email(email):
            logging.info('Registration failed. Invalid email address.')
            return "Registration failed. Invalid email address."
        
        # Check if the username or email already exists in the database
        cursor = db.cursor()
        check_query = "SELECT * FROM users WHERE username = %s OR email = %s"
        cursor.execute(check_query, (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            # A user with the same username or email already exists
            logging.info('Registration failed. Username or email already exists.')
            return "Registration failed. Username or email already exists."
        
        else:
            # User does not exist, proceed with registration
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
            return redirect(url_for('http://localhost:6969/login.html'))
        
        except mysql.connector.Error as err:
            logging.error('Error occurred during registration: %s', err)
            return "Error occurred during registration."

    else:
        return render_template("register.html")
    
# Function to validate email address using regular expression
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# Close the cursor and the database connection
cursor.close()

if __name__ == "__main__":
    app.run("localhost", 6969, debug=True)
