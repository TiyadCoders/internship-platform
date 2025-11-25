from App.models import Shortlist, Position, Staff, Student
from App.models.position import PositionStatus
from App.models.shortlist import DecisionStatus
from App.database import db

def add_student_to_shortlist(student_id, position_id, staff_id):
    teacher = db.session.query(Staff).filter_by(user_id=staff_id).first()
    student = db.session.query(Student).filter_by(user_id=student_id).first()
    if student is None or teacher is None:
        return False
    existing = db.session.query(Shortlist).filter_by(student_id=student.id, position_id=position_id).first()
    position = db.session.query(Position).filter(
        Position.id == position_id,
        Position.number_of_positions > 0,
        Position.status == PositionStatus.open
    ).first()
    if teacher and not existing and position:
        shortlist = Shortlist(student_id=student.id, position_id=position.id, staff_id=teacher.id, title=position.title)
        db.session.add(shortlist)
        db.session.commit()
        return shortlist

    return False

def decide_shortlist(student_id, position_id, decision):
    student = db.session.query(Student).filter_by(user_id=student_id).first()
    if not student:
        return False
    shortlist = db.session.query(Shortlist).filter_by(
        student_id=student.id,
        position_id=position_id,
        status=DecisionStatus.pending
    ).first()
    position = db.session.query(Position).filter(
        Position.id == position_id,
        Position.number_of_positions > 0
    ).first()
    if shortlist and position:
        shortlist.status = DecisionStatus(decision) if isinstance(decision, str) else decision
        if shortlist.status == DecisionStatus.accepted:
            position.number_of_positions = position.number_of_positions - 1
        db.session.commit()
        return shortlist
    return False


def get_shortlist_by_student(student_id):
    student = db.session.query(Student).filter_by(user_id=student_id).first()
    if not student:
        return []
    return db.session.query(Shortlist).filter_by(student_id=student.id).all()

def get_shortlist_by_position(position_id):
    return db.session.query(Shortlist).filter_by(position_id=position_id).all()

def update_shortlist_status(shortlist_id, status):
    shortlist = db.session.get(Shortlist, shortlist_id)
    if not shortlist:
        return None
    shortlist.status = DecisionStatus(status) if isinstance(status, str) else status
    db.session.commit()
    return shortlist
