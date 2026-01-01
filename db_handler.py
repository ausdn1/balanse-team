import sqlite3

def init_db():
    conn = sqlite3.connect('lol_balance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (room_id TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS players 
                 (room_id TEXT, name TEXT, score INTEGER, position TEXT)''')
    conn.commit()
    conn.close()

def create_room(room_id):
    try:
        conn = sqlite3.connect('lol_balance.db')
        c = conn.cursor()
        c.execute("INSERT INTO rooms VALUES (?)", (room_id,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def check_room_exists(room_id):
    conn = sqlite3.connect('lol_balance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rooms WHERE room_id=?", (room_id,))
    res = c.fetchone()
    conn.close()
    return res is not None

# 중복 유저 확인 함수
def is_player_in_room(room_id, name):
    conn = sqlite3.connect('lol_balance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE room_id=? AND name=?", (room_id, name))
    res = c.fetchone()
    conn.close()
    return res is not None

def add_player(room_id, name, score, position):
    conn = sqlite3.connect('lol_balance.db')
    c = conn.cursor()
    c.execute("INSERT INTO players VALUES (?, ?, ?, ?)", (room_id, name, int(score), position))
    conn.commit()
    conn.close()

def get_players(room_id):
    conn = sqlite3.connect('lol_balance.db')
    c = conn.cursor()
    c.execute("SELECT name, score, position FROM players WHERE room_id=?", (room_id,))
    rows = c.fetchall()
    conn.close()
    return [{'name': r[0], 'score': r[1], 'position': r[2]} for r in rows]
