"""
Main application file for VibeTune Music App
Created by: Segni Woldemichael
Date: 04-03-2025
"""

import os
import psycopg
from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv
from urllib.parse import quote 
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Start our Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Session configurations to improve security
app.config.update(
    SESSION_COOKIE_NAME='vibetune_session',
    SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript from accessing cookies
    SESSION_COOKIE_SECURE=False,     # Set to True in production (requires HTTPS)
    SESSION_COOKIE_SAMESITE='Lax',   # Helps prevent CSRF attacks
    PERMANENT_SESSION_LIFETIME=3600  # Session lasts 1 hour
)

# Setting up Google login
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_url='http://localhost:10000/google_login/authorized',
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
)
app.register_blueprint(google_bp, url_prefix="/google_login")

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg.connect(DATABASE_URL, sslmode="require")

def log_history(user_id, music_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (user_id, music_id, played_at) VALUES (%s, %s, %s)",
            (user_id, music_id, datetime.now())
        )
        conn.commit()
    except Exception as e:
        print(f"Error logging history: {e}")
    finally:
        cursor.close()
        conn.close()

@app.route('/')
def home():
    return render_template("landing_page.html")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT music_id, title, artist, album, genre 
            FROM music 
            ORDER BY RANDOM() 
            LIMIT 10
        """)
        songs = cursor.fetchall()
        return render_template('home_page.html', songs=songs)
    except Exception as e:
        print(f"Dashboard error: {e}")
        flash("Error loading dashboard", "error")
        return render_template('home_page.html', songs=[])
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session.permanent = True  # Add this line
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            error_message = "Invalid username or password."
            return render_template('login_page.html', error=error_message)
    return render_template('login_page.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # First check if user exists
            cursor.execute("SELECT user_id FROM users WHERE user_name = %s", (email,))
            if cursor.fetchone():
                flash("This email is already registered. Please login instead.", "error")
                return redirect(url_for('login'))

            # Insert new user
            cursor.execute(
                "INSERT INTO users (user_name, password, preferred_genre) VALUES (%s, %s, %s) RETURNING user_id",
                (email, password, 'Unknown')
            )
            new_user_id = cursor.fetchone()[0]
            conn.commit()
            
            session['user_id'] = new_user_id
            return redirect(url_for('dashboard'))

        except Exception as e:
            if conn:
                conn.rollback()
            flash("Registration failed. Please try again.", "error")
            print(f"Signup error: {e}")
            return redirect(url_for('signup'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    return render_template('signup_page.html')

@app.route('/google_login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    return redirect(url_for('dashboard'))

@app.route('/google_login/authorized')
def google_login_authorized():
    if not google.authorized:
        flash("Google login failed", "error")
        return redirect(url_for('login'))
    
    try:
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info from Google", "error")
            return redirect(url_for('login'))
            
        user_info = resp.json()
        email = user_info['email']
        name = user_info.get('name', email.split('@')[0])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("""
            SELECT user_id FROM users 
            WHERE user_name = %s 
            LIMIT 1
        """, (email,))
        user = cursor.fetchone()
        
        if not user:
            # Create new user
            cursor.execute("""
                INSERT INTO users (user_name, password, preferred_genre) 
                VALUES (%s, 'google_auth', 'Pop') 
                RETURNING user_id
            """, (email,))
            user_id = cursor.fetchone()[0]
            conn.commit()

            session.permanent = True
            session['user_id'] = user_id
            session['user_name'] = name
        else:
            user_id = user[0]
            
        session['user_id'] = user_id
        session['user_name'] = name
        flash(f"Welcome, {name}!", "success")
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Google auth error: {e}")
        flash("Google login failed", "error")
        return redirect(url_for('login'))
    finally:
        cursor.close()
        conn.close()

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/play/<int:music_id>')
def play_song(music_id):
    if 'user_id' not in session:
        flash("Please login to play songs", "error")
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, artist, youtube_link 
            FROM music 
            WHERE music_id = %s
        """, (music_id,))
        song = cursor.fetchone()
        
        if not song:
            flash("Song not found", "error")
            return redirect(url_for('dashboard'))
        
        title, artist, youtube_link = song
        
        # Log to history
        cursor.execute("""
            INSERT INTO history (user_id, music_id, played_at)
            VALUES (%s, %s, NOW())
        """, (session['user_id'], music_id))
        conn.commit()
        
        if youtube_link:
            return redirect(youtube_link)
        
        search_query = f"{title} {artist} official audio"
        return redirect(f"https://www.youtube.com/results?search_query={quote(search_query)}")
        
    except Exception as e:
        print(f"Play error: {e}")
        flash("Error playing song", "error")
        return redirect(url_for('dashboard'))
    finally:
        if 'cursor' in locals(): 
            cursor.close()
        if 'conn' in locals(): 
            conn.close()

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.music_id, m.title, m.artist, h.played_at 
            FROM history h
            JOIN music m ON h.music_id = m.music_id
            WHERE h.user_id = %s
            ORDER BY h.played_at DESC
            LIMIT 20
        """, (session['user_id'],))
        columns = ['music_id', 'title', 'artist', 'played_at']
        history_items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return render_template('history_page.html', history=history_items)
    except Exception as e:
        print(f"History error: {e}")
        flash("Error loading history", "error")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT genre FROM music")
        available_genres = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT preferred_genre FROM users WHERE user_id = %s", (session['user_id'],))
        current_genre = cursor.fetchone()[0]

        if request.method == 'POST':
            genre = request.form.get('genre')
            cursor.execute("UPDATE users SET preferred_genre = %s WHERE user_id = %s", (genre, session['user_id']))
            cursor.execute("INSERT INTO preferences (user_id, preferred_genre) VALUES (%s, %s)", (session['user_id'], genre))
            conn.commit()
            flash("Preferences updated successfully!", "success")
            return redirect(url_for('preferences'))

        return render_template('preferences_page.html', available_genres=available_genres, current_genre=current_genre)

    except Exception as e:
        if conn:
            conn.rollback()
        flash("Error updating preferences", "error")
        print(f"Preferences error: {e}")
        return redirect(url_for('preferences'))
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/showcase')
def showcase():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT music_id, title, artist, album, youtube_link FROM music ORDER BY RANDOM() LIMIT 5")
    songs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('showcase_page.html', songs=songs)

@app.route('/about')
def about():
    return render_template('about_page.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
