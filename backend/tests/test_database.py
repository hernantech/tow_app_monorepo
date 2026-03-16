import pytest
from app.models import case as case_dao
from app.models import message as message_dao
from app.models import operator as operator_dao
from app.models import case_note as case_note_dao


def test_create_case(app):
    with app.app_context():
        case = case_dao.create('user123', 'tow_truck')
        assert case.id is not None
        assert case.wechat_user_id == 'user123'
        assert case.case_type == 'tow_truck'
        assert case.status == 'collecting_info'


def test_update_case(app):
    with app.app_context():
        case = case_dao.create('user123', 'tow_truck')
        updated = case_dao.update(case.id, customer_name='John Doe', phone_number='1234567890')
        assert updated.customer_name == 'John Doe'
        assert updated.phone_number == '1234567890'


def test_get_active_case(app):
    with app.app_context():
        case = case_dao.create('user123', 'tow_truck')
        active = case_dao.get_active_by_wechat_user('user123')
        assert active is not None
        assert active.id == case.id


def test_no_active_when_completed(app):
    with app.app_context():
        case = case_dao.create('user123', 'tow_truck')
        case_dao.update(case.id, status='completed')
        active = case_dao.get_active_by_wechat_user('user123')
        assert active is None


def test_list_filter_by_status(app):
    with app.app_context():
        case_dao.create('user1', 'tow_truck')
        case2 = case_dao.create('user2', 'body_shop')
        case_dao.update(case2.id, status='pending_review')

        collecting = case_dao.list_all(status='collecting_info')
        assert len(collecting) == 1
        pending = case_dao.list_all(status='pending_review')
        assert len(pending) == 1
        all_cases = case_dao.list_all()
        assert len(all_cases) == 2


def test_create_message(app):
    with app.app_context():
        case = case_dao.create('user123', 'tow_truck')
        msg = message_dao.create(
            wechat_user_id='user123',
            direction='inbound',
            content='I need a tow truck',
            case_id=case.id,
        )
        assert msg.id is not None
        assert msg.content == 'I need a tow truck'
        assert msg.direction == 'inbound'

        msgs = message_dao.get_by_case(case.id)
        assert len(msgs) == 1


def test_operator_password_verify(app):
    with app.app_context():
        op = operator_dao.create('testuser', 'password123', 'Test User')
        assert operator_dao.verify_password(op, 'password123') is True
        assert operator_dao.verify_password(op, 'wrongpassword') is False

        # to_dict should not include password_hash
        d = operator_dao.to_dict(op)
        assert 'password_hash' not in d
        assert d['username'] == 'testuser'


def test_case_notes_ordering(app):
    with app.app_context():
        case = case_dao.create('user123', 'tow_truck')
        op = operator_dao.create('operator1', 'pass', 'Operator One')

        note1 = case_note_dao.create(case.id, op.id, 'First note')
        note2 = case_note_dao.create(case.id, op.id, 'Second note')

        notes = case_note_dao.get_by_case(case.id)
        assert len(notes) == 2
        # Ordered DESC - newest first
        assert notes[0].id == note2.id
        assert notes[1].id == note1.id
