# ---------------- IMPORTS ----------------
# These tools help us define tables for our database and track time
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the database object
db = SQLAlchemy()


# ---------------- USER TABLE ----------------
# This table stores all users (admin and viewers)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each user
    username = db.Column(db.String(50), unique=True, nullable=False)  
    # username must be unique and cannot be empty
    password = db.Column(db.String(200), nullable=False)  
    # store hashed passwords, cannot be empty
    role = db.Column(db.String(10), nullable=False)  
    # user role: 'admin' or 'viewer'


# ---------------- MOVIE TABLE ----------------
# This table stores movies that admin adds
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each movie
    title = db.Column(db.String(100), nullable=False)  # Movie title, cannot be empty
    description = db.Column(db.Text)  # Optional description of the movie


# ---------------- RATING TABLE ----------------
# This table stores ratings given by viewers
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each rating
    name = db.Column(db.String(50), nullable=False)  # Name of the person rating
    movie = db.Column(db.String(100), nullable=False)  # Movie title being rated
    stars = db.Column(db.Integer, nullable=False)  # Rating from 1 to 5
    remarks = db.Column(db.Text)  # Optional comment about the movie
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    # Automatically store the time when the rating was created
