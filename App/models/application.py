from App.database import db
from App.models.application_state import (ApplicationState, ApplicationStatus, PendingState, ShortlistedState, AcceptedState, RejectedState)

from sqlalchemy import Enum

__all__ = ['Application']

class Application(db.Model):
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    status = db.Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    student = db.relationship('Student', backref=db.backref('applications', lazy=True))
    position = db.relationship('Position', backref=db.backref('applications', lazy=True))
    staff = db.relationship('Staff', backref=db.backref('applications', lazy=True))

    def __init__(self, student_id, position_id, staff_id):
        self.student_id = student_id
        self.position_id = position_id
        self.staff_id = staff_id
        self.status = ApplicationStatus.PENDING

    def _get_state(self) -> ApplicationState:
        state_map = {
            ApplicationStatus.PENDING: PendingState(),
            ApplicationStatus.SHORTLISTED: ShortlistedState(),
            ApplicationStatus.ACCEPTED: AcceptedState(),
            ApplicationStatus.REJECTED: RejectedState(),
        }
        return state_map[self.status]
    
    def set_state(self, new_state: ApplicationState):
        self.status = new_state.current_status

    def shortlist(self):
        new_state = self._get_state().shortlist()
        self.set_state(new_state)

    def accept(self):
        new_state = self._get_state().accept()
        self.set_state(new_state)

    def reject(self):
        new_state = self._get_state().reject()
        self.set_state(new_state)

    def toJSON(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'position_id': self.position_id,
            'staff_id': self.staff_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }