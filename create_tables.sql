-- Create Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    preferred_genre VARCHAR(100) NOT NULL
);

-- Create Music table
CREATE TABLE music (
    music_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    album VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    release_year INT NOT NULL
);

-- Create History table
CREATE TABLE history (
    history_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    music_id INT NOT NULL,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (music_id) REFERENCES music(music_id)
);

-- Create Preferences table
CREATE TABLE preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    preferred_genre VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Insert test data into Users
INSERT INTO users (user_name, password, preferred_genre) VALUES
('testuser', 'testpassword', 'Rock');

-- Insert test data into Music
INSERT INTO music (title, artist, album, genre, release_year) VALUES
('Song A', 'Artist A', 'Album A', 'Rock', 2020),
('Song B', 'Artist B', 'Album B', 'Pop', 2019),
('Song C', 'Artist C', 'Album C', 'Jazz', 2018);

