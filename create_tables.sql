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
    youtube_link VARCHAR(255) NOT NULL;
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

CREATE INDEX idx_history_user ON history(user_id);
CREATE INDEX idx_music_genre ON music(genre);

-- Insert test user
INSERT INTO users (user_name, password, preferred_genre) VALUES
('testuser', 'testpassword', 'Rock');

-- Insert 50 songs (fixed formatting)
INSERT INTO music (title, artist, album, genre, release_year) VALUES
('Bohemian Rhapsody', 'Queen', 'A Night at the Opera', 'Rock', 1975),
('Sweet Child O''Mine', 'Guns N'' Roses', 'Appetite for Destruction', 'Rock', 1987),
('Hotel California', 'Eagles', 'Hotel California', 'Rock', 1976),
('Smells Like Teen Spirit', 'Nirvana', 'Nevermind', 'Rock', 1991),
('Stairway to Heaven', 'Led Zeppelin', 'Led Zeppelin IV', 'Rock', 1971),
('Blinding Lights', 'The Weeknd', 'After Hours', 'Pop', 2019),  -- Fixed artist name typo
('Shape of You', 'Ed Sheeran', '÷', 'Pop', 2017),
('Uptown Funk', 'Mark Ronson ft. Bruno Mars', 'Uptown Special', 'Pop', 2014),
('Rolling in the Deep', 'Adele', '21', 'Pop', 2010),
('Bad Guy', 'Billie Eilish', 'When We All Fall Asleep, Where Do We Go?', 'Pop', 2019),
-- ... (rest of your 50 songs) ...
('Walk', 'Pantera', 'Vulgar Display of Power', 'Metal', 1992);  -- Last entry