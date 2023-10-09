#imports
import random
from flask import Flask, request, render_template, g, url_for, session
from flask_cors import CORS
import mysql.connector
import logging
import bcrypt
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import MySQLdb.cursors, re, hashlib
import secrets

app = Flask(__name__)

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

        cursor = db.cursor()
        select_query = "SELECT * FROM users WHERE username = %s AND password = %s"
        values = (username, password)
        cursor.execute(select_query, values)
        result = cursor.fetchone()

        if result:
            #logging.info('Login successful for user: %s', username)
            return "Login successful!"
        
        else:
            logging.warning('Invalid login attempt for user: %s', username)
            return "Invalid username or password."

    else: 
        return render_template("login.html")


if __name__ == "__main__":
    app.run("localhost", 6969, debug=True)