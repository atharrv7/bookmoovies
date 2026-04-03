from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'super_secret_glassmorphism_key'

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='atharv123',
        database='movie_booking_db'
    )

@app.route('/')
def home():
    fallback_movies = [
        {
            'id': 1,
            'title': 'Dhurandhar',
            'genre': 'Action',
            'duration': '2h 25m',
            'price': 250,
            'rating': 4.5,
            'image_url': 'https://via.placeholder.com/300x400'
        },
        {
            'id': 2,
            'title': 'Kantara',
            'genre': 'Thriller',
            'duration': '2h 30m',
            'price': 300,
            'rating': 4.9,
            'image_url': 'https://via.placeholder.com/300x400'
        },
        {
            'id': 3,
            'title': 'Project Hail Mary',
            'genre': 'Sci-Fi',
            'duration': '2h 10m',
            'price': 350,
            'rating': 4.8,
            'image_url': 'https://via.placeholder.com/300x400'
        }
    ]

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM movies')
        movies = cursor.fetchall()
        cursor.close()
        db.close()
    except Exception as e:
        movies = fallback_movies
        print('Database error:', e)

    if not movies:
        movies = fallback_movies

    return render_template('index.html', movies=movies)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))

        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO users (full_name, email, phone, password) VALUES (%s, %s, %s, %s)',
                (full_name, email, phone, password)
            )
            db.commit()
            cursor.close()
            db.close()
            flash('Signup successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error: Email already exists or invalid data.')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/book/<int:movie_id>', methods=['GET', 'POST'])
def book(movie_id):
    if 'user_id' not in session:
        flash('Please login to book tickets.')
        return redirect(url_for('login'))
    allowed_show_times = {'10:00 AM', '01:30 PM', '05:00 PM', '09:00 PM'}

    if request.method == 'POST':
        show_time = request.form.get('show_time', '').strip()
        show_date = request.form.get('show_date', '').strip()

        if show_time not in allowed_show_times:
            flash('Please select a valid show time.')
            return redirect(url_for('book', movie_id=movie_id))

        try:
            booking_date = datetime.strptime(show_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Please select a valid date.')
            return redirect(url_for('book', movie_id=movie_id))

        try:
            seats = int(request.form.get('seats', '1'))
        except ValueError:
            flash('Please enter a valid number of seats.')
            return redirect(url_for('book', movie_id=movie_id))

        if seats < 1 or seats > 10:
            flash('Seats must be between 1 and 10.')
            return redirect(url_for('book', movie_id=movie_id))

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute('SELECT price FROM movies WHERE id = %s', (movie_id,))
            movie = cursor.fetchone()

            if not movie:
                flash('Movie not found.')
                return redirect(url_for('home'))

            total_amount = float(movie['price']) * seats

            cursor.execute(
                'INSERT INTO bookings (user_id, movie_id, show_time, show_date, seats, total_amount) VALUES (%s, %s, %s, %s, %s, %s)',
                (session['user_id'], movie_id, show_time, booking_date, seats, total_amount)
            )
            booking_id = cursor.lastrowid
            db.commit()
            flash('Your ticket is booked!')
            return redirect(url_for('ticket', booking_id=booking_id))
        except Exception:
            db.rollback()
            flash('Booking failed. Please try again.')
            return redirect(url_for('book', movie_id=movie_id))
        finally:
            cursor.close()
            db.close()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM movies WHERE id = %s', (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    db.close()

    if not movie:
        flash('Movie not found.')
        return redirect(url_for('home'))

    return render_template('book.html', movie=movie)

@app.route('/ticket/<int:booking_id>')
def ticket(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Fetch booking along with movie details
    cursor.execute('''
        SELECT b.*, m.title, m.image_url, m.genre
        FROM bookings b
        JOIN movies m ON b.movie_id = m.id
        WHERE b.id = %s AND b.user_id = %s
    ''', (booking_id, session['user_id']))
    
    booking = cursor.fetchone()
    cursor.close()
    db.close()

    if not booking:
        flash('Booking not found.')
        return redirect(url_for('home'))

    return render_template('ticket.html', booking=booking)

if __name__ == '__main__':
    app.run(debug=True)
