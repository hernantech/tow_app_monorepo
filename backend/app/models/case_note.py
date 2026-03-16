from dataclasses import dataclass
from typing import Optional, List
import sqlite3
from app.database import get_db


@dataclass
class CaseNote:
    id: Optional[int] = None
    case_id: Optional[int] = None
    operator_id: Optional[int] = None
    note: str = ''
    created_at: Optional[str] = None


def to_dict(case_note: CaseNote) -> dict:
    return {
        'id': case_note.id,
        'case_id': case_note.case_id,
        'operator_id': case_note.operator_id,
        'note': case_note.note,
        'created_at': case_note.created_at,
    }


def from_row(row: sqlite3.Row) -> CaseNote:
    return CaseNote(
        id=row['id'],
        case_id=row['case_id'],
        operator_id=row['operator_id'],
        note=row['note'],
        created_at=row['created_at'],
    )


def create(case_id: int, operator_id: int, note: str) -> CaseNote:
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO case_notes (case_id, operator_id, note) VALUES (?, ?, ?)",
            (case_id, operator_id, note),
        )
        note_id = cursor.lastrowid
        row = db.execute("SELECT * FROM case_notes WHERE id = ?", (note_id,)).fetchone()
        return from_row(row)


def get_by_case(case_id: int) -> List[CaseNote]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM case_notes WHERE case_id = ? ORDER BY created_at DESC, id DESC",
            (case_id,),
        ).fetchall()
        return [from_row(row) for row in rows]
