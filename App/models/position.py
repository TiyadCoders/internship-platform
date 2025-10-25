from App.database import db
from sqlalchemy import Enum
import enum

class PositionStatus(enum.Enum):
    open = "open"
    closed = "closed"

class Position(db.Model):
    __tablename__ = 'position'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    number_of_positions = db.Column(db.Integer, default=1)
    status = db.Column(Enum(PositionStatus, native_enum=False), nullable=False, default=PositionStatus.open)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=False)
    employer = db.relationship("Employer", back_populates="positions")

    def __init__(self, title, employer_id, number):
        self.title = title
        self.employer_id = employer_id
        self.status = "open"
        self.number_of_positions = number
        

    def update_status(self, status):
        self.status = status
        db.session.commit()
        return self.status

    def update_number_of_positions(self, number_of_positions):
        self.number_of_positions = number_of_positions
        db.session.commit()
        return self.number_of_positions

    def delete_position(self):
        db.session.delete(self)
        db.session.commit()
        return

    def list_positions(self):
        return db.session.query(Position).all()

    def toJSON(self):
        return {
            "id": self.id,
            "title": self.title,
            "number_of_positions": self.number_of_positions,
            "status": self.status.value,
            "employer_id": self.employer_id
        }