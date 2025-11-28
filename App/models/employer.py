from App.database import db
from App.models.user import User

class Employer(User):
    __tablename__ = 'employer'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    positions = db.relationship("Position", back_populates="employer")
    company = db.relationship("Company", back_populates="employers")

    __mapper_args__ = {
        'polymorphic_identity': 'employer'
    }

    def __init__(self, username, password, company_id):
        super().__init__(username, password, 'employer')
        self.company_id = company_id