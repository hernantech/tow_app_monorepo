import sqlite3
from contextlib import contextmanager

_db_path = None


def init_db(database_url):
    """Parse sqlite URL, store path, and create tables."""
    global _db_path
    if database_url == 'sqlite:///:memory:':
        _db_path = ':memory:'
    elif database_url.startswith('sqlite:///'):
        _db_path = database_url.replace('sqlite:///', '', 1)
    else:
        _db_path = database_url
    _create_tables()


# For in-memory databases we need to keep a single persistent connection
_memory_conn = None


def _get_connection():
    global _memory_conn
    if _db_path == ':memory:':
        if _memory_conn is None:
            _memory_conn = sqlite3.connect(':memory:')
            _memory_conn.row_factory = sqlite3.Row
            _memory_conn.execute("PRAGMA foreign_keys = ON")
        return _memory_conn
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    """Context manager yielding sqlite3.Connection with Row factory and foreign keys."""
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        # Only close file-based connections, not in-memory
        if _db_path != ':memory:':
            conn.close()


def _create_tables():
    """Create all database tables and indexes."""
    conn = _get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS operators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'operator',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wechat_user_id TEXT NOT NULL,
                case_type TEXT CHECK(case_type IN ('tow_truck', 'body_shop')),
                status TEXT CHECK(status IN ('collecting_info', 'pending_review', 'assigned', 'in_progress', 'completed', 'cancelled')) DEFAULT 'collecting_info',
                customer_name TEXT,
                phone_number TEXT,
                location TEXT,
                vehicle_info TEXT,
                damage_description TEXT,
                preferred_shop_id TEXT,
                assigned_operator_id INTEGER REFERENCES operators(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER REFERENCES cases(id),
                wechat_user_id TEXT NOT NULL,
                direction TEXT CHECK(direction IN ('inbound', 'outbound')) NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS case_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER REFERENCES cases(id) NOT NULL,
                operator_id INTEGER REFERENCES operators(id) NOT NULL,
                note TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS device_usage (
                device_id TEXT PRIMARY KEY,
                message_count INTEGER DEFAULT 0,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_cases_wechat_user_id ON cases(wechat_user_id);
            CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
            CREATE INDEX IF NOT EXISTS idx_messages_case_id ON messages(case_id);
        """)
        conn.commit()
    finally:
        if _db_path != ':memory:':
            conn.close()


def reset_memory_db():
    """Reset in-memory database (for testing)."""
    global _memory_conn
    if _memory_conn is not None:
        _memory_conn.close()
        _memory_conn = None
