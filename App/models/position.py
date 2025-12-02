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
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=False)

    company = db.relationship("Company", back_populates="positions")
    employer = db.relationship("Employer", back_populates="positions")

    def __init__(self, title, company_id, created_by, number, description=None):
        self.title = title
        self.company_id = company_id
        self.created_by = created_by
        self.status = PositionStatus.OPEN
        self.number_of_positions = number
        self.description = description

    def __repr__(self):
        return f"<Position {self.title}>"

    def get_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "number_of_positions": self.number_of_positions,
            "status": self.status.value,
            "company_id": self.company_id,
            "created_by": self.created_by
        }
