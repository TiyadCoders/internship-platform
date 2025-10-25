from App.database import db
from App.models.user import User

class Employer(db.Model):
    __tablename__ = 'employer'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    username =  db.Column(db.String(20), nullable=False, unique=True)
    positions = db.relationship("Position", back_populates="employer")

    def __init__(self, username, user_id):
        self.username = username
        self.user_id = user_id