#imports
import random
from flask import Flask, request, render_template, g, redirect
from flask_cors import CORS
import mysql.connector
import logging
import MySQLdb.cursors, re, hashlib
import secrets
import sys


app = Flask(__name__)

# Connect to the database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="g0thb01",
    database="personality_test"
)

# Set up logging
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('logs')
logger.setLevel(logging.DEBUG)

# Configure the logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler for all levels
file_handler = logging.FileHandler('server.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(file_handler)


CORS(app)

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
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8
"""
cursor.execute(create_table_query)

# Commit the changes to the database
db.commit()

# Close the cursor and the database connection
cursor.close()
#db.close()