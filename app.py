import os
import psycopg2
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Get PostgreSQL connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL") 

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, artist FROM Music")
    songs = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template("index.html", songs=songs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
