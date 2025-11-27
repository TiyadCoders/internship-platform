from App.database import db
from App.models.user import User
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date

from App.database import db
from App.models.user import User
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date

class Student(User):
    __tablename__ = 'student'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    email = db.Column(db.String(256))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(256))
    degree = db.Column(db.String(256))
    phone = db.Column(db.String(256))
    gpa = db.Column(db.Float)
    resume = db.Column(db.String(256))

    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }

    def __init__(self, username, password):
        super().__init__(username, password, 'student')

#    def update_DOB(self, date):
#        self.DOB = date
#        db.session.commit()
#        return self.DOB
#        
#   @hybrid_property
#   def age(self):
#       if self.DOB is None:
#           return None
#       today = date.today()
#       dob = self.DOB
#       return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))