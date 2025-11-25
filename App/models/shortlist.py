from App.database import db
from App.models.user import User
from sqlalchemy import Enum
import enum  

class DecisionStatus(enum.Enum):
    accepted = "accepted"
    rejected = "rejected"
    pending = "pending"

class Shortlist(db.Model):
    __tablename__ = 'shortlist'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    title = db.Column(db.String(512), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    status = db.Column(Enum(DecisionStatus, native_enum=False), nullable=False, default=DecisionStatus.pending)
    student = db.relationship('Student', backref=db.backref('shortlist', lazy=True))
    position = db.relationship('Position', backref=db.backref('shortlist', lazy=True))
    staff = db.relationship('Staff', backref=db.backref('shortlist', lazy=True))
    #Pending Commit

    def __init__(self, student_id, position_id, staff_id, title):
        self.student_id = student_id
        self.position_id = position_id
        self.status = DecisionStatus.pending
        self.staff_id = staff_id
        self.title = title

    def toJSON(self):
        return{
            "id": self.id,
            "title": self.title,
            "student_id": self.student_id,
            "position_id": self.position_id,
            "staff_id": self.staff_id,
            "status": self.status.value
        }
      