"""Idempotent seed script to create initial admin user."""
from app.database import init_db
from app.models import operator as operator_dao
from config import Config


def seed():
    init_db(Config.DATABASE_URL)
    existing = operator_dao.get_by_username('admin')
    if existing is None:
        operator_dao.create(
            username='admin',
            password='admin123',
            full_name='System Admin',
            role='admin',
        )
        print("Created admin user.")
    else:
        print("Admin user already exists.")


if __name__ == '__main__':
    seed()
