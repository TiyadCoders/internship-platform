from App.database import db
from sqlalchemy import Enum
import enum

class PositionStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"

class Position(db.Model):
    __tablename__ = 'position'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    number_of_positions = db.Column(db.Integer, default=1)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(Enum(PositionStatus, native_enum=False), nullable=False, default=PositionStatus.OPEN)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=False)
    employer = db.relationship("Employer", back_populates="positions")

    def __init__(self, title, employer_id, number, description=None):
        self.title = title
        self.employer_id = employer_id
        self.status = PositionStatus.OPEN
        self.number_of_positions = number
        self.description = description
        self.description = description

    def toJSON(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "description": self.description,
            "number_of_positions": self.number_of_positions,
            "status": self.status.value,
            "employer_id": self.employer_id
        }
