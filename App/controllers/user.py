from App.models import User, Student, Employer, Staff
from App.database import db

def create_user(username, password, user_type, company_id=None, student_data=None):
    """
    Create a new user. Returns tuple (user, error_message).
    On success: (user, None)
    On failure: (None, error_message)
    """
    if user_type == "student":
        newuser = Student(username=username, password=password)
        if student_data:
            newuser.email = student_data['email']
            newuser.dob = student_data['dob']
            newuser.gender = student_data['gender']
            newuser.degree = student_data['degree']
            newuser.phone = student_data['phone']
            newuser.gpa = student_data['gpa']
            newuser.resume = student_data['resume']
    elif user_type == "employer":
        if company_id is None:
            return None, "Company ID is required for employer"
        newuser = Employer(username=username, password=password, company_id=company_id)
    elif user_type == "staff":
        if company_id is None:
            return None, "Company ID is required for staff"
        newuser = Staff(username=username, password=password, company_id=company_id)
    else:
        return None, "Invalid user type"

    try:
        db.session.add(newuser)
        db.session.commit()
        return newuser, None
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        if "UNIQUE constraint failed" in error_msg or "duplicate key" in error_msg.lower():
            return None, "Username already taken"
        return None, f"Failed to create user: {error_msg}"


def get_user_by_username(username):
    result = db.session.execute(db.select(User).filter_by(username=username))
    return result.scalar_one_or_none()

def get_user(id):
    return db.session.get(User, id)

def get_all_users():
    return db.session.scalars(db.select(User)).all()

def get_all_users_json():
    users = get_all_users()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        # user is already in the session; no need to re-add
        db.session.commit()
        return True
    return None
