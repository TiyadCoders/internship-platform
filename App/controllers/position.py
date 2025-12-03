from App.models import Position, Employer, Application
from App.models.position import PositionStatus
from App.database import db

def open_position(user_id, title, number_of_positions=1, description=None):
    employer = db.session.get(Employer, user_id)
    if not employer:
        return None

    new_position = Position(
        title=title,
        company_id=employer.company_id,
        created_by=employer.id,
        number=number_of_positions,
        description=description
    )
    db.session.add(new_position)
    try:
        db.session.commit()
        return new_position
    except Exception as e:
        db.session.rollback()
        return None


def get_positions_by_employer(user_id):
    employer = Employer.query.filter_by(id=user_id).first()
    if not employer:
        return []
    return db.session.query(Position).filter_by(created_by=employer.id).all()

def get_all_positions():
    return Position.query.all()

def get_all_positions_json():
    positions = get_all_positions()
    if positions:
        return [position.get_json() for position in positions]
    return []

def get_positions_by_employer_json(user_id):
    employer = Employer.query.filter_by(id=user_id).first()
    if not employer:
        return []
    positions = db.session.query(Position).filter_by(created_by=employer.id).all()
    if positions:
        return [position.get_json() for position in positions]
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

def get_open_positions():
    return Position.query.filter_by(status=PositionStatus.OPEN).all()


def get_open_positions_json():
    positions = get_open_positions()
    if positions:
        return [position.get_json() for position in positions]
    return []

def get_position(position_id):
    return db.session.get(Position, position_id)


def get_position_json(position_id):
    position = get_position(position_id)
    if position:
        return position.get_json()
    return None

def update_position(position_id, title=None, number_of_positions=None, description=None):
    position = db.session.get(Position, position_id)
    if not position:
        return None

    if title is not None:
        position.title = title
    if number_of_positions is not None:
        position.number_of_positions = number_of_positions
    if description is not None:
        position.description = description

    try:
        db.session.commit()
        return position
    except Exception:
        db.session.rollback()
        return None
    
def apply_for_position(student_id, position_id):
    position = db.session.get(Position, position_id)
    if not position:
        return {"error": "Position not found"}

    if position.status != PositionStatus.OPEN:
        return {"error": "Position is not open"}

    existing = Application.query.filter_by(
        student_id=student_id,
        position_id=position_id
    ).first()
    if existing:
        return {"error": "Application already exists"}

    application = Application(
        student_id=student_id,
        position_id=position_id,
        updated_by=student_id  
    )

    try:
        db.session.add(application)
        db.session.commit()
        return application
    except Exception:
        db.session.rollback()
        return None

def get_positions_by_company(company_id):
    return Position.query.filter_by(company_id=company_id).all()


def get_positions_by_company_json(company_id):
    positions = get_positions_by_company(company_id)
    if positions:
        return [p.get_json() for p in positions]
    return []
