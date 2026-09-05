import sqlite3
import random
import requests;
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)
DB_FILE = "database.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failed_logins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_id TEXT,
                username TEXT,
                source_ip TEXT,
                sub_status TEXT,
                country TEXT,
                latitude REAL,
                longitude REAL
            )
        ''')
        conn.commit()

def generate_mock_log():
    usernames = ['Administrator', 'root', 'jdoe', 'db_admin', 'service_account', 'backup_user']
    sub_statuses = ['0xC000006A', '0xC0000064', '0xC0000234']
    sample_ips = [
        '185.190.140.1', '45.227.254.1', '103.212.230.1',
        '82.102.23.1', '216.58.213.14', '195.154.122.1'
    ]
    
    ip = random.choice(sample_ips)
    user = random.choice(usernames)
    status = random.choice(sub_statuses)
    
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        country = response.get('country', 'Unknown')
        lat = response.get('lat', 0.0)
        lon = response.get('lon', 0.0)
    except Exception:
        country, lat, lon = "Unknown", 0.0, 0.0

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO failed_logins (timestamp, event_id, username, source_ip, sub_status, country, latitude, longitude)
            VALUES (?, '4625', ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user, ip, status, country, lat, lon))
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    generate_mock_log()
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM failed_logins ORDER BY timestamp DESC LIMIT 100")
        logs = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT COUNT(*) as total FROM failed_logins")
        total_count = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(DISTINCT source_ip) as unique_ips FROM failed_logins")
        unique_ips = cursor.fetchone()['unique_ips']
        
    return jsonify({
        "logs": logs,
        "metrics": {
            "total_failed": total_count,
            "unique_ips": unique_ips
        }
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)