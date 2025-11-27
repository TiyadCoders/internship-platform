from App.database import db
from App.models.user import User

class Employer(User):
    __tablename__ = 'employer'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    positions = db.relationship("Position", back_populates="employer")

    __mapper_args__ = {
        'polymorphic_identity': 'employer'
    }

    def __init__(self, username, password):
        super().__init__(username, password, 'employer')