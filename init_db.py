import mysql.connector

def init_db():
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='atharv123'
    )
    cursor = db.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS movie_booking_db')
    cursor.close()
    db.close()

    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='atharv123',
        database='movie_booking_db'
    )
    cursor = db.cursor()

    cursor.execute('DROP TABLE IF EXISTS bookings')
    cursor.execute('DROP TABLE IF EXISTS movies')
    cursor.execute('DROP TABLE IF EXISTS users')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        phone VARCHAR(20),
        password VARCHAR(255) NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        genre VARCHAR(50),
        duration VARCHAR(20),
        price DECIMAL(10, 2),
        rating FLOAT,
        image_url VARCHAR(255)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        movie_id INT,
        show_time VARCHAR(50),
        show_date DATE,
        seats INT,
        total_amount DECIMAL(10, 2),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (movie_id) REFERENCES movies(id)
    )
    ''')

    movies = [
        ('Dhurandhar', 'Action, Thriller', '3h 30m', 250.00, 4.5, 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png'),
        ('Kantara', 'Action, Drama, Thriller', '2h 28m', 200.00, 4.9, 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/great-ball.png'),
        ('Project Hail Mary', 'Sci-Fi, Adventure', '2h 45m', 350.00, 4.8, 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/ultra-ball.png')
    ]
    sql = 'INSERT INTO movies (title, genre, duration, price, rating, image_url) VALUES (%s, %s, %s, %s, %s, %s)'
    cursor.executemany(sql, movies)
    db.commit()

    print('Database initialized successfully!')
    cursor.close()
    db.close()

if __name__ == '__main__':
    init_db()

