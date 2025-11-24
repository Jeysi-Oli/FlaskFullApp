# ---------------- IMPORTS ----------------
# These are the tools we need to make forms that users can fill out.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange


# ---------------- LOGIN FORM ----------------
# This form is for users to log in (type username and password)
class LoginForm(FlaskForm):
    username = StringField(
        "Username",  # Label that shows up next to the box
        validators=[DataRequired()]  # Makes sure the user doesn’t leave it empty
    )
    password = PasswordField(
        "Password",  # Label for password box
        validators=[DataRequired()]  # Cannot be empty
    )
    submit = SubmitField("Login")  # The button that says "Login"


# ---------------- RATE FORM ----------------
# This form is for users to rate movies
class RateForm(FlaskForm):
    name = StringField(
        "Enter Name",  # User types their name
        validators=[DataRequired()]  # Cannot leave blank
    )
    
    movieList = SelectField(
        "Movie",  # Dropdown label
        choices=[],  # This will be filled dynamically with movie titles in app.py
        validators=[DataRequired()]  # Must select a movie
    )
    
    stars = SelectField(
        "Rating (1–5 Stars)",  # Label for rating
        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],  # 5 options
        coerce=int,  # Make sure the selected value is stored as a number
        validators=[DataRequired(), NumberRange(min=1, max=5)]  # Must be between 1 and 5
    )
    
    remarks = TextAreaField(
        "Remarks",  # Label for comments
        render_kw={"rows": 3, "placeholder": "Write your comments..."}  # Show 3 lines and placeholder text
    )
    
    submit = SubmitField("Submit")  # Button that says "Submit"


# ---------------- MOVIE FORM ----------------
# This form is for admin to add or edit movies
class MovieForm(FlaskForm):
    title = StringField(
        "Movie Title",  # Label for movie title
        validators=[DataRequired()]  # Cannot be empty
    )
    description = TextAreaField(
        "Description"  # Text area to write a description of the movie
    )
    submit = SubmitField("Save")  # Button that says "Save"
