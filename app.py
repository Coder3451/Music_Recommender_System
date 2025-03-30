import os
import psycopg2
from flask import Flask, jsonify, render_template, redirect, request, session, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Set up Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_url='http://localhost:10000/google_login/authorized'  # Explicitly set the correct redirect URL here
)

app.register_blueprint(google_bp, url_prefix="/google_login")

# Get PostgreSQL connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL") 

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@app.route('/google_login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))  # Triggers the OAuth flow
    
    # Handle the user after they log in with Google
    user_info = google.get('/plus/v1/people/me').json()
    session['google_user'] = user_info  # Store the user info in the session
    return redirect(url_for('dashboard'))

@app.route('/google_login/authorized')
def google_login_authorized():
    if not google.authorized:
        return redirect(url_for('login'))  # Redirect to login if not authorized
    
    # Get the user's information from Google
    user_info = google.get('/plus/v1/people/me').json()

    # Store the user data in session or database
    session['google_user'] = user_info

    # Redirect to the dashboard after successful login
    return redirect(url_for('dashboard'))

@app.route('/api/music', methods=['GET'])
def get_recommendations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, artist FROM Music LIMIT 5;")
    recommendations = [{"track": row[0], "artist": row[1]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(recommendations)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM music")  # Get all songs from the music table
    songs = cursor.fetchall()  # Fetch all rows from the query
    cursor.close()
    conn.close()

    # Pass the songs list to the template
    return render_template('dashboard/index.html', songs=songs)

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
            session['user_id'] = user[0]  # Store user in session
            return redirect(url_for('dashboard'))
        else:
            # Display a message and provide a link to Google signup
            error_message = "Invalid username or password. Please <a href='https://accounts.google.com/signup'>sign up with Google</a>."
            return render_template('login.html', error=error_message)

    return render_template('login.html')

@app.route('/play/<int:music_id>')
def play_song(music_id):
    # Fetch the song title from the PostgreSQL database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM music WHERE music_id = %s", (music_id,))
    song = cursor.fetchone()
    cursor.close()
    conn.close()

    if song:
        search_query = song[0]  # The title is stored as the first element in the tuple
    else:
        search_query = "Unknown Song"

    # Format the title correctly for YouTube search
    youtube_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
    
    # Print to console for debugging
    print(f"Playing song: {search_query}")
    print(f"Redirecting to YouTube URL: {youtube_url}")

    return redirect(youtube_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
