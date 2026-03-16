from dataclasses import dataclass
from typing import Optional, List
import sqlite3
from app.database import get_db


@dataclass
class Message:
    id: Optional[int] = None
    case_id: Optional[int] = None
    wechat_user_id: str = ''
    direction: str = 'inbound'
    content: str = ''
    message_type: str = 'text'
    created_at: Optional[str] = None


def to_dict(message: Message) -> dict:
    return {
        'id': message.id,
        'case_id': message.case_id,
        'wechat_user_id': message.wechat_user_id,
        'direction': message.direction,
        'content': message.content,
        'message_type': message.message_type,
        'created_at': message.created_at,
    }


def from_row(row: sqlite3.Row) -> Message:
    return Message(
        id=row['id'],
        case_id=row['case_id'],
        wechat_user_id=row['wechat_user_id'],
        direction=row['direction'],
        content=row['content'],
        message_type=row['message_type'],
        created_at=row['created_at'],
    )


def create(wechat_user_id: str, direction: str, content: str,
           case_id: Optional[int] = None, message_type: str = 'text') -> Message:
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO messages (case_id, wechat_user_id, direction, content, message_type) "
            "VALUES (?, ?, ?, ?, ?)",
            (case_id, wechat_user_id, direction, content, message_type),
        )
        msg_id = cursor.lastrowid
        row = db.execute("SELECT * FROM messages WHERE id = ?", (msg_id,)).fetchone()
        return from_row(row)


def get_by_case(case_id: int) -> List[Message]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM messages WHERE case_id = ? ORDER BY created_at ASC",
            (case_id,),
        ).fetchall()
        return [from_row(row) for row in rows]
