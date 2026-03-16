from dataclasses import dataclass
from typing import Optional
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db


@dataclass
class Operator:
    id: Optional[int] = None
    username: str = ''
    password_hash: str = ''
    full_name: str = ''
    role: str = 'operator'
    created_at: Optional[str] = None


def to_dict(operator: Operator) -> dict:
    return {
        'id': operator.id,
        'username': operator.username,
        'full_name': operator.full_name,
        'role': operator.role,
        'created_at': operator.created_at,
    }


def from_row(row: sqlite3.Row) -> Operator:
    return Operator(
        id=row['id'],
        username=row['username'],
        password_hash=row['password_hash'],
        full_name=row['full_name'],
        role=row['role'],
        created_at=row['created_at'],
    )


def create(username: str, password: str, full_name: str, role: str = 'operator') -> Operator:
    password_hash = generate_password_hash(password)
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO operators (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (username, password_hash, full_name, role),
        )
        op_id = cursor.lastrowid
        row = db.execute("SELECT * FROM operators WHERE id = ?", (op_id,)).fetchone()
        return from_row(row)


def get_by_username(username: str) -> Optional[Operator]:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM operators WHERE username = ?", (username,)
        ).fetchone()
        if row is None:
            return None
        return from_row(row)


def get_by_id(operator_id: int) -> Optional[Operator]:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM operators WHERE id = ?", (operator_id,)
        ).fetchone()
        if row is None:
            return None
        return from_row(row)


def verify_password(operator: Operator, password: str) -> bool:
    return check_password_hash(operator.password_hash, password)
