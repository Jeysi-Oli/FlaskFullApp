# ---------------- IMPORTS ----------------
# These lines bring in the tools (modules) we need to build our app.
# Think of this like taking out ingredients before cooking.

from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RateForm, MovieForm
from models import db, User, Movie, Rating

# ---------------- APP SETUP ----------------
# Create the main app and tell Flask some important settings.

app = Flask(__name__)  # This creates our Flask web app
app.config['SECRET_KEY'] = 'secretkey123'  # Secret key helps keep sessions/forms safe
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'  # Where our data will be saved
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Turns off unnecessary tracking

# Connect the database (from models.py) to this Flask app
db.init_app(app)

# ---------------- DATABASE SETUP ----------------
# This creates the tables automatically when the app starts (Required for Railway/Production)
with app.app_context():
    db.create_all()
    
    # Check if admin exists, if not, create it
    if not User.query.filter_by(username='admin').first():
        print("Creating default admin account...")
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        viewer = User(username='viewer', password=generate_password_hash('viewer123'), role='viewer')
        db.session.add_all([admin, viewer])
        db.session.commit()
        print("Default accounts created.")

# ---------------- HOME PAGE ----------------
@app.route('/')
def index():
    # Get all movies from the database
    movies = Movie.query.all()
    # Show the 'index.html' page with the list of movies
    return render_template('index.html', title='Home', movies=movies)


# ---------------- LOGIN PAGE ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Create a login form object (from forms.py)
    
    # If the user clicks "Submit" and the form is valid...
    if form.validate_on_submit():
        # Look for a user in the database with the same username
        user = User.query.filter_by(username=form.username.data).first()
        
        # If the user exists AND the password is correct...
        if user and check_password_hash(user.password, form.password.data):
            # Save the user info in the session (like storing a note)
            session['user'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')  # Show a success message
            
            # Depending on their role, send them to different pages
            if session['role'] == 'viewer':
                return redirect(url_for('view'))  # Go to the viewer page
            elif session['role'] == 'admin':
                return redirect(url_for('manage_movies'))  # Go to the admin page
        else:
            # If login fails, show an error message
            flash('Invalid credentials', 'danger')
    
    # If the form wasn’t submitted yet, or had errors, show login page again
    return render_template('login.html', form=form, title='Login')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    # Remove user info from session (log them out)
    session.pop('user', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))  # Go back to home page


# ---------------- RATE A MOVIE ----------------
@app.route('/rate', methods=['GET', 'POST'])
def rate():
    form = RateForm()  # Create the rate form
    movies = Movie.query.all()  # Get all movies from the database

    # Fill the dropdown list in the form with movie titles
    form.movieList.choices = [(m.title, m.title) for m in movies]

    # If the user submits the form and it’s valid...
    if form.validate_on_submit():
        # Create a new rating object
        rating = Rating(
            name=form.name.data,
            movie=form.movieList.data,
            stars=form.stars.data,
            remarks=form.remarks.data
        )
        # Add the rating to the database and save it
        db.session.add(rating)
        db.session.commit()
        flash('Rating submitted successfully!', 'success')
        return redirect(url_for('rate'))  # Refresh the page

    # Show all ratings (latest first)
    ratings = Rating.query.order_by(Rating.created_at.desc()).all()
    return render_template('rate.html', form=form, ratings=ratings)


# ---------------- ADMIN ROUTES ----------------
# These pages are only for the admin role (movie management)

@app.route('/manage')
def manage_movies():
    # If user is NOT an admin, block access
    if session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    # Get all movies to show on admin page
    movies = Movie.query.all()
    return render_template('manage_movies.html', movies=movies)


# Add new movie
@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    form = MovieForm()
    if form.validate_on_submit():
        # Create a new movie record
        movie = Movie(title=form.title.data, description=form.description.data)
        db.session.add(movie)
        db.session.commit()
        flash('Movie added successfully!', 'success')
        return redirect(url_for('manage_movies'))
    return render_template('add_movie.html', form=form)


# Edit existing movie
@app.route('/edit_movie/<int:id>', methods=['GET', 'POST'])
def edit_movie(id):
    if session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Get the movie or show 404 if not found
    movie = Movie.query.get_or_404(id)
    # Load current movie details into the form
    form = MovieForm(obj=movie)
    
    if form.validate_on_submit():
        # Update movie info
        movie.title = form.title.data
        movie.description = form.description.data
        db.session.commit()
        flash('Movie updated!', 'success')
        return redirect(url_for('manage_movies'))
    
    return render_template('edit.html', form=form)


# Delete a movie
@app.route('/delete_movie/<int:id>')
def delete_movie(id):
    if session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Find the movie by ID, or show 404 if not found
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    flash('Movie deleted!', 'info')
    return redirect(url_for('manage_movies'))


# ---------------- VIEWER ROUTE ----------------
@app.route('/view')
def view():
    # Only allow viewers to access
    if session.get('role') != 'viewer':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Show all movie ratings
    ratings = Rating.query.all()
    return render_template('view.html', ratings=ratings)


# ---------------- MAIN PROGRAM ----------------
if __name__ == '__main__':
    # This makes sure the database exists before running the app
    with app.app_context():
        db.create_all()

        # If there’s no admin or viewer user yet, create them automatically
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
            viewer = User(username='viewer', password=generate_password_hash('viewer123'), role='viewer')
            db.session.add_all([admin, viewer])
            db.session.commit()
    
    # Start the web app in debug mode (so we can see errors easily)
    app.run(debug=True)
