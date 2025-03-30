from flask import Flask, jsonify, request, send_from_directory
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="music_recommender"
    )
    return conn

@app.route('/api/music', methods=['GET'])
def get_recommendations():
    recommendations = [
            {"track": "Song A", "artist": "Artist A"},
            {"track": "Song B", "artist": "Artist B"},
            {"track": "Song C", "artist": "Artist C"}
    ]
    return jsonify(recommendations)

@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
