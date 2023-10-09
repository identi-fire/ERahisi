from flask import Flask
import mysql.connector
from flask_login import LoginManager, UserMixin, login_user

login_manager = LoginManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Set your secret key for session management

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="g0thb01",
    database="personality_test"
)

# Create a cursor to execute MySQL queries
cursor = db.cursor()

# Assuming you have a User class representing your users
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Query the database to get user details based on user_id
    query = "SELECT id FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        return User(user_data[0])  # Create a User object using the fetched user_id
    else:
        return None  # Return None if user not found in the database
