import os
import psycopg2
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

# Get PostgreSQL connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

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
def serve_frontend():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
