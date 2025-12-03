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
    'get_applications',
    'withdraw_application',
    'staff_can_access_application',
]


def staff_can_access_application(staff_user, application):
    """Check if staff member can access this application (same company)."""
    return application.position.employer.company_id == staff_user.company_id

def create_application(student_id, position_id, updated_by=None):
    """Create a new application for a student to a position."""
    student = db.session.get(Student, student_id)
    position = db.session.get(Position, position_id)

    if not all([student, position]):
        return None

    if updated_by is not None:
        staff = db.session.get(Staff, updated_by)
        if not staff:
            return None

    # Check for existing application
    existing = db.session.query(Application).filter_by(
        student_id=student_id,
        position_id=position_id
    ).first()
    if existing:
        return None

    application = Application(student_id=student_id, position_id=position_id, updated_by=updated_by)
    db.session.add(application)
    db.session.commit()
    return application

def shortlist_application(application_id):
    """Shortlist an application."""
    application = db.session.get(Application, application_id)
    if not application:
        return None
    if 'shortlist' not in application.get_available_actions():
        return {'error': 'Cannot shortlist application in current state', 'application': application}
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
    if 'accept' not in application.get_available_actions():
        return {'error': 'Cannot accept application in current state', 'application': application}
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
    if 'reject' not in application.get_available_actions():
        return {'error': 'Cannot reject application in current state', 'application': application}
    application.reject()
    db.session.commit()
    return application

def get_applications(user):
    """Get all applications for a user."""
    if user.role == "student":
        return db.session.query(Application).filter_by(student_id=user.id).all()
    elif user.role == "staff":
        # Join through Position -> Employer to filter by company
        from App.models import Position, Employer
        return db.session.query(Application).join(Position).join(Employer).filter(
            Employer.company_id == user.company_id
        ).all()

def get_applications_by_student(student_id):
    """Get all applications for a student."""
    return db.session.query(Application).filter_by(student_id=student_id).all()

def get_applications_by_position(position_id):
    """Get all applications for a position."""
    return db.session.query(Application).filter_by(position_id=position_id).all()

def get_application(application_id):
    """Get a single application by ID."""
    return db.session.get(Application, application_id)

def withdraw_application(application_id):
    """Withdraw an application (changes status to withdrawn instead of deleting)."""
    application = db.session.get(Application, application_id)
    if not application:
        return None
    if 'withdraw' not in application.get_available_actions():
        return {'error': 'Cannot withdraw application in current state', 'application': application}
    application.withdraw()
    db.session.commit()
    return application


# Compatibility wrappers for legacy function names used in tests and other modules
def add_student_to_shortlist(student_id, position_id, updated_by=None):
    """Alias for create_application kept for backwards compatibility."""
    # With joined table inheritance, Student.id == User.id, so we can use the id directly
    return create_application(student_id, position_id, updated_by)


def get_shortlist_by_student(student_id):
    """Alias for get_applications_by_student kept for backwards compatibility."""
    # With joined table inheritance, Student.id == User.id, so we can use the id directly
    return get_applications_by_student(student_id)
