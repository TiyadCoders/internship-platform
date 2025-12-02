from App.database import db
from App.models.user import User

class Student(User):
    __tablename__ = 'student'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    email = db.Column(db.String(256))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20))
    degree = db.Column(db.String(256))
    phone = db.Column(db.String(256))
    gpa = db.Column(db.Float)
    resume = db.Column(db.String(256))

    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }

    def __init__(self, username, password):
        super().__init__(username, password, 'student')

    def __repr__(self):
        return f"<Student {self.username}>"

    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'email': self.email,
            'dob': self.dob.isoformat() if self.dob else None,
            'gender': self.gender,
            'degree': self.degree,
            'phone': self.phone,
            'gpa': self.gpa,
            'resume': self.resume
        }
