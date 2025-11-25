from App.models import Position, Employer
from App.models.position import PositionStatus
from App.database import db

def open_position(user_id, title, number_of_positions=1):
    employer = Employer.query.filter_by(user_id=user_id).first()
    if not employer:
        return None

    new_position = Position(title=title, number=number_of_positions, employer_id=employer.id)
    db.session.add(new_position)
    try:
        db.session.commit()
        return new_position
    except Exception as e:
        db.session.rollback()
        return None


def get_positions_by_employer(user_id):
    employer = Employer.query.filter_by(user_id=user_id).first()
    return db.session.query(Position).filter_by(employer_id=employer.id).all()

def get_all_positions():
    return Position.query.all()

def get_all_positions_json():
    positions = get_all_positions()
    if positions:
        return [position.toJSON() for position in positions]
    return []

def get_positions_by_employer_json(user_id):
    employer = Employer.query.filter_by(user_id=user_id).first()
    positions = db.session.query(Position).filter_by(employer_id=employer.id).all()
    if positions:
        return [position.toJSON() for position in positions]
    return []

def update_position_status(position_id, status):
    position = db.session.get(Position, position_id)
    if not position:
        return None
    try:
        position.status = PositionStatus(status) if isinstance(status, str) else status
        db.session.commit()
        return position
    except Exception:
        db.session.rollback()
        return None

def update_position_count(position_id, number_of_positions):
    position = db.session.get(Position, position_id)
    if not position:
        return None
    try:
        position.number_of_positions = number_of_positions
        db.session.commit()
        return position
    except Exception:
        db.session.rollback()
        return None

def delete_position(position_id):
    position = db.session.get(Position, position_id)
    if not position:
        return False
    try:
        db.session.delete(position)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False