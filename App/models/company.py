from App.database import db

__all__ = ['Company']

class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    staff = db.relationship("Staff", back_populates="company")
    employers = db.relationship("Employer", back_populates="company")

    def __repr__(self):
        return f"<Company {self.name}>"

    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'staff': [s.get_json() for s in self.staff],
            'employers': [e.get_json() for e in self.employers]
        }
