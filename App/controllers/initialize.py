from .user import create_user
from .application import create_application
from .position import open_position
from .company import create_company
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()
    # Create a company first
    company = create_company('Default Company', 'The default company for testing')
    create_user('bob', 'bobpass', "student")
    create_user('frank', 'frankpass', "employer", company_id=company.id)
    create_user('john', 'johnpass', "staff", company_id=company.id)
    open_position(user_id=2, title='Software Engineer', number_of_positions=6)
    open_position(user_id=2, title='Mechanical Engineer', number_of_positions=6)
    create_application(student_id=1, position_id=1, updated_by=3)
