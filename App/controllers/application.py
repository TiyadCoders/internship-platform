from App.models import Application, Position, Staff, Student
from App.database import db

__all__ = [
    'create_application',
    'shortlist_application',
    'get_application_by_id',
    'accept_application',
    'reject_application',
    'get_applications_by_student',
    'get_applications_by_position',
    'get_application',
    'add_student_to_shortlist',
    'get_shortlist_by_student',
]

def create_application(student_id, position_id, staff_id):
    """Create a new application for a student to a position."""
    student = db.session.get(Student, student_id)
    position = db.session.get(Position, position_id)
    staff = db.session.get(Staff, staff_id)

    if not all([student, position, staff]):
        return None

    # Check for existing application
    existing = db.session.query(Application).filter_by(
        student_id=student_id,
        position_id=position_id
    ).first()
    if existing:
        return None

    application = Application(student_id=student_id, position_id=position_id, staff_id=staff_id)
    db.session.add(application)
    db.session.commit()
    return application

def shortlist_application(application_id):
    """Shortlist an application."""
    application = db.session.get(Application, application_id)
    if not application:
        return None
    application.shortlist()
    db.session.commit()
    return application

def get_application_by_id(application_id):
    return db.session.get(Application, application_id)

def accept_application(application_id):
    """Accept an application."""
    application = db.session.get(Application, application_id)
    if not application:
        return None
    application.accept()
    position = db.session.get(Position, application.position_id)
    if position and position.number_of_positions > 0:
        position.number_of_positions -= 1
    db.session.commit()
    return application

def reject_application(application_id):
    """Reject an application."""
    application = db.session.get(Application, application_id)
    if not application:
        return None
    application.reject()
    db.session.commit()
    return application

def get_applications_by_student(student_id):
    """Get all applications for a student."""
    return db.session.query(Application).filter_by(student_id=student_id).all()

def get_applications_by_position(position_id):
    """Get all applications for a position."""
    return db.session.query(Application).filter_by(position_id=position_id).all()

def get_application(application_id):
    """Get a single application by ID."""
    return db.session.get(Application, application_id)


# Compatibility wrappers for legacy function names used in tests and other modules
def add_student_to_shortlist(student_id, position_id, staff_id):
    """Alias for create_application kept for backwards compatibility."""
    # With joined table inheritance, Student.id == User.id, so we can use the id directly
    return create_application(student_id, position_id, staff_id)


def get_shortlist_by_student(student_id):
    """Alias for get_applications_by_student kept for backwards compatibility."""
    # With joined table inheritance, Student.id == User.id, so we can use the id directly
    return get_applications_by_student(student_id)
