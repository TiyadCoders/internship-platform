from App.models import User, Student, Employer, Staff
from App.database import db

def create_user(username, password, user_type, company_id=None):
    try:
        if user_type == "student":
            newuser = Student(username=username, password=password)
        elif user_type == "employer":
            if company_id is None:
                return None
            newuser = Employer(username=username, password=password, company_id=company_id)
        elif user_type == "staff":
            if company_id is None:
                return None
            newuser = Staff(username=username, password=password, company_id=company_id)
        else:
            return None

        db.session.add(newuser)
        db.session.commit()
        return newuser
    except Exception as e:
        db.session.rollback()
        return None


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
