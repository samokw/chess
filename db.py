# db.py
import sqlite3

DB_FILE = 'hostage_chess.db'

def connect_db():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    return conn

def create_tables():
    """Create the tables if they don't exist."""
    conn = connect_db()
    cursor = conn.cursor()

    # Create games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
        GAME_NO INTEGER PRIMARY KEY AUTOINCREMENT,
        WHITE_HANDLE TEXT,
        BLACK_HANDLE TEXT NULL,
        RESULT TEXT(256)
    )
    ''')

    # Create moves table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS moves (
        GAME_NO INTEGER,
        TURN_NO INTEGER,
        TURN TEXT(1),
        BOARD TEXT,
        REAL_TIME INTEGER,
        WHITE_TIME INTEGER,
        BLACK_TIME INTEGER,
        FOREIGN KEY (GAME_NO) REFERENCES games(GAME_NO)
    )
    ''')

    conn.commit()
    conn.close()


def find_game_waiting_for_opponent():
    """Find a game where BLACK_HANDLE is NULL or empty."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM games WHERE BLACK_HANDLE IS NULL OR BLACK_HANDLE = '' LIMIT 1
    ''')
    game = cursor.fetchone()
    conn.close()
    return game

def update_black_handle(game_no, black_handle):
    """Update the BLACK_HANDLE for a given game."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE games SET BLACK_HANDLE = ? WHERE GAME_NO = ?
    ''', (black_handle, game_no))
    conn.commit()
    conn.close()

def get_game_by_no(game_no):
    """Retrieve a game by GAME_NO."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM games WHERE GAME_NO = ?
    ''', (game_no,))
    game = cursor.fetchone()
    conn.close()
    return game

def add_move(game_no, turn_no, turn, board_state, real_time, white_time, black_time):
    """Insert a move into the moves table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO moves (GAME_NO, TURN_NO, TURN, BOARD, REAL_TIME, WHITE_TIME, BLACK_TIME)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (game_no, turn_no, turn, board_state, real_time, white_time, black_time))
    conn.commit()
    conn.close()

def get_latest_move(game_no):
    """Fetch the latest move for a game."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM moves WHERE GAME_NO = ? ORDER BY TURN_NO DESC LIMIT 1
    ''', (game_no,))
    move = cursor.fetchone()
    conn.close()
    return move

def get_next_turn_no(game_no):
    """Get the next turn number for a game."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT MAX(TURN_NO) FROM moves WHERE GAME_NO = ?
    ''', (game_no,))
    result = cursor.fetchone()
    conn.close()
    return (result[0] or 0) + 1

def update_game_result(game_no, result):
    """Update the result of a game."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE games SET RESULT = ? WHERE GAME_NO = ?
    ''', (result, game_no))
    conn.commit()
    conn.close()

def get_all_games():
    """Retrieve all games from the games table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games')
    games = cursor.fetchall()
    conn.close()
    return games

def get_moves_by_game_no(game_no):
    """Retrieve all moves for a given game number."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM moves WHERE GAME_NO = ? ORDER BY TURN_NO
    ''', (game_no,))
    moves = cursor.fetchall()
    conn.close()
    return moves

# db.py

def add_game(white_handle):
    """Insert a new game into the games table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO games (WHITE_HANDLE, BLACK_HANDLE)
        VALUES (?, NULL)
    ''', (white_handle,))
    conn.commit()

    game_no = cursor.lastrowid  # Get the GAME_NO of the newly inserted game
    conn.close()
    return game_no

def find_game_waiting_for_opponent():
    """Find a game where BLACK_HANDLE is NULL."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM games WHERE BLACK_HANDLE IS NULL LIMIT 1
    ''')
    game = cursor.fetchone()
    conn.close()
    return game
