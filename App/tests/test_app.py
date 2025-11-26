import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Employer, Position, Application, Staff, Student
from App.models.position import PositionStatus
from App.models.application_state import (
    ApplicationStatus, PendingState, AcceptedState, RejectedState, ShortlistedState
)
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user,
    open_position,
    get_positions_by_employer,
    add_student_to_shortlist,
    get_shortlist_by_student,
    accept_application,
)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob", "bobpass", "student")
        assert user.username == "bob"
        assert user.role == "student"

    def test_new_student(self):
        # Student model takes (username, user_id) - it's linked to User
        student = Student("john", user_id=1)
        assert student.username == "john"
        assert student.user_id == 1

    def test_new_staff(self):
        # Staff model takes (username, user_id) - it's linked to User
        staff = Staff("jim", user_id=1)
        assert staff.username == "jim"
        assert staff.user_id == 1

    def test_new_employer(self):
        # Employer model takes (username, user_id) - it's linked to User
        employer = Employer("alice", user_id=1)
        assert employer.username == "alice"
        assert employer.user_id == 1

    def test_new_position(self):
        position = Position("Software Developer", 10, 5)
        assert position.title == "Software Developer"
        assert position.employer_id == 10
        assert position.status == PositionStatus.open
        assert position.number_of_positions == 5

    def test_new_application(self):
        application = Application(student_id=1, position_id=2, staff_id=3)
        assert application.student_id == 1
        assert application.position_id == 2
        assert application.staff_id == 3
        assert application.status == ApplicationStatus.PENDING

    # pure function no side effects or integrations called
    def test_get_json(self):
        user = User("bob", "bobpass", "student")
        user_json = user.get_json()
        self.assertEqual(user_json["username"], "bob")
        self.assertTrue("id" in user.get_json())

    def test_hashed_password(self):
        password = "mypass"
        user = User("bob", password, "student")
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password, "student")
        assert user.check_password(password)


class ApplicationStateUnitTests(unittest.TestCase):
    """Unit tests for ApplicationState pattern"""

    # PendingState tests
    def test_pending_state_initial_status(self):
        state = PendingState()
        assert state.current_status == ApplicationStatus.PENDING

    def test_pending_to_shortlisted(self):
        state = PendingState()
        new_state = state.shortlist()
        assert isinstance(new_state, ShortlistedState)
        assert new_state.current_status == ApplicationStatus.SHORTLISTED

    def test_pending_to_accepted(self):
        state = PendingState()
        new_state = state.accept()
        assert isinstance(new_state, AcceptedState)
        assert new_state.current_status == ApplicationStatus.ACCEPTED

    def test_pending_to_rejected(self):
        state = PendingState()
        new_state = state.reject()
        assert isinstance(new_state, RejectedState)
        assert new_state.current_status == ApplicationStatus.REJECTED

    # ShortlistedState tests
    def test_shortlisted_state_initial_status(self):
        state = ShortlistedState()
        assert state.current_status == ApplicationStatus.SHORTLISTED

    def test_shortlisted_to_accepted(self):
        state = ShortlistedState()
        new_state = state.accept()
        assert isinstance(new_state, AcceptedState)
        assert new_state.current_status == ApplicationStatus.ACCEPTED

    def test_shortlisted_to_rejected(self):
        state = ShortlistedState()
        new_state = state.reject()
        assert isinstance(new_state, RejectedState)
        assert new_state.current_status == ApplicationStatus.REJECTED


    # AcceptedState tests
    def test_accepted_state_initial_status(self):
        state = AcceptedState()
        assert state.current_status == ApplicationStatus.ACCEPTED

    def test_accepted_accept_noop(self):
        state = AcceptedState()
        new_state = state.accept()
        assert new_state is state  # Returns self

    def test_accepted_shortlist_noop(self):
        state = AcceptedState()
        new_state = state.shortlist()
        assert new_state is state  # Returns self

    def test_accepted_to_rejected(self):
        state = AcceptedState()
        new_state = state.reject()
        assert isinstance(new_state, RejectedState)
        assert new_state.current_status == ApplicationStatus.REJECTED

    # RejectedState tests
    def test_rejected_state_initial_status(self):
        state = RejectedState()
        assert state.current_status == ApplicationStatus.REJECTED

    def test_rejected_reject_noop(self):
        state = RejectedState()
        new_state = state.reject()
        assert new_state is state  # Returns self

    def test_rejected_accept_noop(self):
        state = RejectedState()
        new_state = state.accept()
        assert new_state is state  # Returns self

    def test_rejected_to_shortlisted(self):
        state = RejectedState()
        new_state = state.shortlist()
        assert isinstance(new_state, ShortlistedState)
        assert new_state.current_status == ApplicationStatus.SHORTLISTED


'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="function")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})

    with app.app_context():
        create_db()
        yield app.test_client()
        db.drop_all()


class UserIntegrationTests(unittest.TestCase):

    def test_create_user(self):

        staff = create_user("rick", "bobpass", "staff")
        assert staff.username == "rick"

        employer = create_user("sam", "sampass", "employer")
        assert employer.username == "sam"

        student = create_user("hannah", "hannahpass", "student")
        assert student.username == "hannah"

   # def test_get_all_users_json(self):
     #   users_json = get_all_users_json()
      #  self.assertListEqual([{"id":1, "username":"bob"}, {"id":2, "username":"rick"}], users_json)

    # Tests data changes in the database
    #def test_update_user(self):
      #  update_user(1, "ronnie")
      #  user = get_user(1)
       # assert user.username == "ronnie"

    def test_open_position(self):
        position_count = 2
        employer = create_user("sally", "sallypass", "employer")
        assert employer is not None
        position = open_position(user_id=employer.id, title="IT Support", number_of_positions=position_count)
        positions = get_positions_by_employer(employer.id)
        assert position is not None
        assert position.number_of_positions == position_count
        assert len(positions) > 0
        assert any(p.id == position.id for p in positions)

        invalid_position = open_position(user_id=-1, title="Developer", number_of_positions=1)
        assert invalid_position is None


    def test_create_application(self):
        position_count = 3
        staff = create_user("linda", "lindapass", "staff")
        assert staff is not None
        student = create_user("hank", "hankpass", "student")
        assert student is not None
        employer = create_user("ken", "kenpass", "employer")
        assert employer is not None
        position = open_position(user_id=employer.id, title="Database Manager", number_of_positions=position_count)
        invalid_position = open_position(user_id=-1, title="Developer", number_of_positions=1)
        assert invalid_position is None
        assert position is not None
        added_application = add_student_to_shortlist(student.id, position.id, staff.id)
        assert added_application
        applications = get_shortlist_by_student(student.id)
        assert any(s.id == added_application.id for s in applications)


    def test_application_state_transitions(self):
        position_count = 3
        student = create_user("jack", "jackpass", "student")
        assert student is not None
        staff = create_user("pat", "patpass", "staff")
        assert staff is not None
        employer = create_user("frank", "pass", "employer")
        assert employer is not None
        position = open_position(user_id=employer.id, title="Intern", number_of_positions=position_count)
        assert position is not None
        stud_application = add_student_to_shortlist(student.id, position.id, staff.id)
        assert stud_application
        assert stud_application.status == ApplicationStatus.PENDING
        accepted = accept_application(stud_application.id)
        assert accepted is not None
        assert accepted.status == ApplicationStatus.ACCEPTED
        assert position.number_of_positions == (position_count - 1)
        applications = get_shortlist_by_student(student.id)
        assert any(s.status == ApplicationStatus.ACCEPTED for s in applications)
        assert len(applications) > 0

    def test_student_view_applications(self):
        student = create_user("john", "johnpass", "student")
        assert student is not None
        staff = create_user("tim", "timpass", "staff")
        assert staff is not None
        employer = create_user("joe", "joepass", "employer")
        assert employer is not None
        position = open_position(user_id=employer.id, title="Software Intern", number_of_positions=4)
        assert position is not None
        application = add_student_to_shortlist(student.id, position.id, staff.id)
        applications = get_shortlist_by_student(student.id)
        assert any(application.id == s.id for s in applications)
        assert len(applications) > 0

    # Tests data changes in the database
    #def test_update_user(self):
    #    update_user(1, "ronnie")
    #   user = get_user(1)
    #   assert user.username == "ronnie"

