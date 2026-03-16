from dataclasses import dataclass
from typing import Optional, List
import sqlite3
from app.database import get_db


@dataclass
class Case:
    id: Optional[int] = None
    wechat_user_id: str = ''
    case_type: Optional[str] = None
    status: str = 'collecting_info'
    customer_name: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    vehicle_info: Optional[str] = None
    damage_description: Optional[str] = None
    preferred_shop_id: Optional[str] = None
    assigned_operator_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


def to_dict(case: Case) -> dict:
    return {
        'id': case.id,
        'wechat_user_id': case.wechat_user_id,
        'case_type': case.case_type,
        'status': case.status,
        'customer_name': case.customer_name,
        'phone_number': case.phone_number,
        'location': case.location,
        'vehicle_info': case.vehicle_info,
        'damage_description': case.damage_description,
        'preferred_shop_id': case.preferred_shop_id,
        'assigned_operator_id': case.assigned_operator_id,
        'created_at': case.created_at,
        'updated_at': case.updated_at,
    }


def from_row(row: sqlite3.Row) -> Case:
    return Case(
        id=row['id'],
        wechat_user_id=row['wechat_user_id'],
        case_type=row['case_type'],
        status=row['status'],
        customer_name=row['customer_name'],
        phone_number=row['phone_number'],
        location=row['location'],
        vehicle_info=row['vehicle_info'],
        damage_description=row['damage_description'],
        preferred_shop_id=row['preferred_shop_id'],
        assigned_operator_id=row['assigned_operator_id'],
        created_at=row['created_at'],
        updated_at=row['updated_at'],
    )


def create(wechat_user_id: str, case_type: str) -> Case:
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO cases (wechat_user_id, case_type) VALUES (?, ?)",
            (wechat_user_id, case_type),
        )
        case_id = cursor.lastrowid
        row = db.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
        return from_row(row)


def get_by_id(case_id: int) -> Optional[Case]:
    with get_db() as db:
        row = db.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
        if row is None:
            return None
        return from_row(row)


def get_active_by_wechat_user(wechat_user_id: str) -> Optional[Case]:
    """Returns the most recent non-completed/cancelled case for a user."""
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM cases WHERE wechat_user_id = ? "
            "AND status NOT IN ('completed', 'cancelled') "
            "ORDER BY created_at DESC LIMIT 1",
            (wechat_user_id,),
        ).fetchone()
        if row is None:
            return None
        return from_row(row)


def update(case_id: int, **kwargs) -> Optional[Case]:
    if not kwargs:
        return get_by_id(case_id)

    # Build SET clause
    set_parts = []
    values = []
    for key, value in kwargs.items():
        set_parts.append(f"{key} = ?")
        values.append(value)
    set_parts.append("updated_at = CURRENT_TIMESTAMP")
    values.append(case_id)

    set_clause = ", ".join(set_parts)
    with get_db() as db:
        db.execute(
            f"UPDATE cases SET {set_clause} WHERE id = ?",
            values,
        )
        row = db.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
        if row is None:
            return None
        return from_row(row)


def list_all(status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Case]:
    with get_db() as db:
        if status:
            rows = db.execute(
                "SELECT * FROM cases WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (status, limit, offset),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM cases ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [from_row(row) for row in rows]
