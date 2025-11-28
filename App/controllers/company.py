from App.models import Company
from App.database import db

def create_company(name, description):
    try:
        new_company = Company(name=name, description=description)
        db.session.add(new_company)
        db.session.commit()
        return new_company
    except Exception as e:
        db.session.rollback()
        return None

def get_company(id):
    return db.session.get(Company, id)

def get_all_companies():
    return db.session.scalars(db.select(Company)).all()

def get_all_companies_json():
    companies = get_all_companies()
    if not companies:
        return []
    return [company.get_json() for company in companies]

def update_company(id, name=None, description=None):
    company = get_company(id)
    if company:
        if name is not None:
            company.name = name
        if description is not None:
            company.description = description
        db.session.commit()
        return company
    return None

def delete_company(id):
    company = get_company(id)
    if company:
        db.session.delete(company)
        db.session.commit()
        return True
    return False
