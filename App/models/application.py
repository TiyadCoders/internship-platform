from App.database import db
from App.models.application_state import (ApplicationState, ApplicationStatus, PendingState, ShortlistedState, AcceptedState, RejectedState, WithdrawnState)

from sqlalchemy import Enum, UniqueConstraint

__all__ = ['Application']

class Application(db.Model):
    __tablename__ = 'application'
    __table_args__ = (
        UniqueConstraint('student_id', 'position_id', name='uq_student_position'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id', ondelete='CASCADE'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    student = db.relationship('Student', backref=db.backref('applications', lazy=True, passive_deletes=True))
    position = db.relationship('Position', backref=db.backref('applications', lazy=True, passive_deletes=True))
    staff = db.relationship('Staff', backref=db.backref('applications', lazy=True), foreign_keys=[updated_by])

    def __init__(self, student_id, position_id, updated_by=None):
        self.student_id = student_id
        self.position_id = position_id
        self.updated_by = updated_by
        self.status = ApplicationStatus.PENDING

    def _get_state(self) -> ApplicationState:
        state_map = {
            ApplicationStatus.PENDING: PendingState(),
            ApplicationStatus.SHORTLISTED: ShortlistedState(),
            ApplicationStatus.ACCEPTED: AcceptedState(),
            ApplicationStatus.REJECTED: RejectedState(),
            ApplicationStatus.WITHDRAWN: WithdrawnState(),
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

    def withdraw(self):
        new_state = self._get_state().withdraw()
        self.set_state(new_state)

    def get_available_actions(self) -> list[str]:
        return self._get_state().get_available_actions()

    def toJSON(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'position_id': self.position_id,
            'updated_by': self.updated_by,
            'status': self.status.value,
            'available_actions': self.get_available_actions(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }