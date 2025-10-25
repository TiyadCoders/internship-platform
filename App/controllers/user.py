from App.models import User, Student, Employer, Staff
from App.database import db

def create_user(username, password, user_type):
    try:
        newuser = User(username=username, password=password, role=user_type)
        db.session.add(newuser)
        db.session.flush() 
        
        if user_type == "student":
            student = Student(username=username, user_id=newuser.id)
            db.session.add(student)
        elif user_type == "employer":
            employer = Employer(username=username, user_id=newuser.id)
            db.session.add(employer)
        elif user_type == "staff":
            staff = Staff(username=username, user_id=newuser.id)
            db.session.add(staff)
        else:
            return False
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False


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
