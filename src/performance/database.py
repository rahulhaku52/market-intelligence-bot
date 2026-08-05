import sqlite3
import os
from src.utils.logger import logger

DB_PATH = 'data/market_bot.db'

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Signals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        ticker TEXT NOT NULL,
        mode TEXT NOT NULL,
        price REAL NOT NULL,
        price_type TEXT NOT NULL,
        data_quality_score INTEGER NOT NULL,
        setup_score INTEGER NOT NULL,
        entry_zone TEXT NOT NULL,
        stoploss REAL NOT NULL,
        tp1 REAL NOT NULL,
        tp2 REAL NOT NULL,
        tp3 REAL NOT NULL,
        risk_reward REAL NOT NULL,
        status TEXT NOT NULL
    )
    ''')
    
    # Trades table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        signal_id INTEGER,
        ticker TEXT NOT NULL,
        entry_date TEXT NOT NULL,
        entry_price REAL NOT NULL,
        stoploss REAL NOT NULL,
        tp1 REAL NOT NULL,
        status TEXT NOT NULL,
        exit_date TEXT,
        exit_price REAL,
        pnl REAL,
        FOREIGN KEY (signal_id) REFERENCES signals (id)
    )
    ''')
    
    # Setup Features table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS setup_features (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        signal_id INTEGER,
        rvol REAL,
        rsi REAL,
        confluence_score INTEGER,
        sector_score INTEGER,
        FOREIGN KEY (signal_id) REFERENCES signals (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("💾 Local SQLite DB initialized successfully.")

def log_signal_to_db(signal_data: dict) -> int:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO signals (
            timestamp, ticker, mode, price, price_type, data_quality_score, setup_score,
            entry_zone, stoploss, tp1, tp2, tp3, risk_reward, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal_data.get('timestamp'),
            signal_data.get('ticker'),
            signal_data.get('mode', 'dynamic'),
            signal_data.get('price'),
            signal_data.get('price_type', 'LIVE'),
            signal_data.get('data_quality_score', 100),
            signal_data.get('setup_score', 0),
            signal_data.get('entry_zone', ''),
            signal_data.get('stoploss', 0.0),
            signal_data.get('tp1', 0.0),
            signal_data.get('tp2', 0.0),
            signal_data.get('tp3', 0.0),
            signal_data.get('risk_reward', 0.0),
            signal_data.get('status', 'VALID')
        ))
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return signal_id
    except Exception as e:
        logger.error(f"Failed to log signal to SQLite DB: {e}")
        return -1
