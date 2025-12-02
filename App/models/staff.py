from App.database import db
from App.models.user import User

class Staff(User):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    company = db.relationship("Company", back_populates="staff")

    __mapper_args__ = {
        'polymorphic_identity': 'staff'
    }

    def __init__(self, username, password, company_id):
        super().__init__(username, password, 'staff')
        self.company_id = company_id

    def __repr__(self):
        return f"<Staff {self.username}>"

    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'company_id': self.company_id
        }
