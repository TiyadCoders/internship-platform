import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Employer, Position, Application, Staff, Student, Company
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
    create_company,
    get_company,
    get_all_companies,
    update_company,
    delete_company,
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
        # Student now inherits from User and takes (username, password)
        student = Student("john", "johnpass")
        assert student.username == "john"
        assert student.role == "student"  # Should be set automatically
        assert isinstance(student, User)  # Should be instance of User
        assert isinstance(student, Student)  # Should be instance of Student

    def test_new_staff(self):
        # Staff now inherits from User and takes (username, password, company_id)
        staff = Staff("jim", "jimpass", company_id=1)
        assert staff.username == "jim"
        assert staff.role == "staff"  # Should be set automatically
        assert staff.company_id == 1
        assert isinstance(staff, User)  # Should be instance of User
        assert isinstance(staff, Staff)  # Should be instance of Staff

    def test_new_employer(self):
        # Employer now inherits from User and takes (username, password, company_id)
        employer = Employer("alice", "alicepass", company_id=1)
        assert employer.username == "alice"
        assert employer.role == "employer"  # Should be set automatically
        assert employer.company_id == 1
        assert isinstance(employer, User)  # Should be instance of User
        assert isinstance(employer, Employer)  # Should be instance of Employer

    def test_inheritance_chain(self):
        # Test that all subclasses properly inherit from User
        student = Student("student1", "pass1")
        staff = Staff("staff1", "pass2", company_id=1)
        employer = Employer("employer1", "pass3", company_id=1)

        # All should be instances of User
        assert isinstance(student, User)
        assert isinstance(staff, User)
        assert isinstance(employer, User)

        # All should have User methods
        assert hasattr(student, 'check_password')
        assert hasattr(staff, 'check_password')
        assert hasattr(employer, 'check_password')

        assert hasattr(student, 'get_json')
        assert hasattr(staff, 'get_json')
        assert hasattr(employer, 'get_json')

    def test_polymorphic_identity(self):
        # Test that role is set correctly via polymorphic identity
        student = Student("student1", "pass1")
        staff = Staff("staff1", "pass2", company_id=1)
        employer = Employer("employer1", "pass3", company_id=1)

        assert student.role == "student"
        assert staff.role == "staff"
        assert employer.role == "employer"

    def test_student_inherits_password_methods(self):
        # Test that Student inherits password methods from User
        password = "mypass"
        student = Student("john", password)
        assert student.password != password  # Should be hashed
        assert student.check_password(password)  # Should validate correctly
        assert not student.check_password("wrongpass")  # Should reject wrong password

    def test_staff_inherits_password_methods(self):
        # Test that Staff inherits password methods from User
        password = "staffpass"
        staff = Staff("jane", password, company_id=1)
        assert staff.password != password  # Should be hashed
        assert staff.check_password(password)  # Should validate correctly
        assert not staff.check_password("wrongpass")  # Should reject wrong password

    def test_employer_inherits_password_methods(self):
        # Test that Employer inherits password methods from User
        password = "emppass"
        employer = Employer("alice", password, company_id=1)
        assert employer.password != password  # Should be hashed
        assert employer.check_password(password)  # Should validate correctly
        assert not employer.check_password("wrongpass")  # Should reject wrong password

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

    def test_get_json_inherited(self):
        # Test that subclasses can use inherited get_json method
        student = Student("john", "johnpass")
        staff = Staff("jane", "janepass", company_id=1)
        employer = Employer("alice", "alicepass", company_id=1)

        student_json = student.get_json()
        staff_json = staff.get_json()
        employer_json = employer.get_json()

        assert student_json["username"] == "john"
        assert staff_json["username"] == "jane"
        assert employer_json["username"] == "alice"

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
    def test_position_with_and_without_description(self):
        employer = create_user("descemp", "descpass", "employer")
        assert employer is not None
        # With description
        pos_with_desc = open_position(user_id=employer.id, title="Described Position", number_of_positions=1, description="A position with a description")
        assert pos_with_desc is not None
        assert pos_with_desc.description == "A position with a description"
        # Without description
        pos_without_desc = open_position(user_id=employer.id, title="No Description Position", number_of_positions=1)
        assert pos_without_desc is not None
        assert pos_without_desc.description is None

    def test_create_user(self):
        # Create a company first for staff and employer
        company = create_company("Test Company", "A test company")
        assert company is not None

        # Test that create_user creates the correct subclass instances
        staff = create_user("rick", "bobpass", "staff", company_id=company.id)
        assert staff.username == "rick"

        employer = create_user("sam", "sampass", "employer", company_id=company.id)
        assert employer.username == "sam"
        assert employer.role == "employer"
        assert isinstance(employer, Employer)
        assert isinstance(employer, User)

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

        assert student.role == "student"
        assert isinstance(student, Student)
        assert isinstance(student, User)

    def test_polymorphic_query(self):
        # Create a company first for staff and employer
        company = create_company("Test Company", "A test company")

        # Test that querying User returns appropriate subclass instances
        staff = create_user("rick", "bobpass", "staff", company_id=company.id)
        employer = create_user("sam", "sampass", "employer", company_id=company.id)
        student = create_user("hannah", "hannahpass", "student")

        # Query by user ID should return the correct subclass
        queried_staff = db.session.get(User, staff.id)
        queried_employer = db.session.get(User, employer.id)
        queried_student = db.session.get(User, student.id)

        assert isinstance(queried_staff, Staff)
        assert isinstance(queried_employer, Employer)
        assert isinstance(queried_student, Student)

        # All should still be instances of User
        assert isinstance(queried_staff, User)
        assert isinstance(queried_employer, User)
        assert isinstance(queried_student, User)

    def test_query_by_subclass(self):
        # Create a company first for staff and employer
        company = create_company("Test Company", "A test company")

        # Test that querying by subclass only returns instances of that subclass
        create_user("rick", "bobpass", "staff", company_id=company.id)
        create_user("sam", "sampass", "employer", company_id=company.id)
        create_user("hannah", "hannahpass", "student")

        # Query specific subclasses
        all_staff = Staff.query.all()
        all_employers = Employer.query.all()
        all_students = Student.query.all()

        assert len(all_staff) == 1
        assert len(all_employers) == 1
        assert len(all_students) == 1

        # Verify they are the correct types
        assert all(isinstance(s, Staff) for s in all_staff)
        assert all(isinstance(e, Employer) for e in all_employers)
        assert all(isinstance(s, Student) for s in all_students)

    def test_user_relationships_after_inheritance(self):
        # Create a company first for employer
        company = create_company("Test Company", "A test company")

        # Test that relationships still work correctly after inheritance
        employer = create_user("sam", "sampass", "employer", company_id=company.id)
        assert employer is not None
        assert hasattr(employer, 'positions')
        assert isinstance(employer.positions, list)

    def test_new_position(self):
        employer = create_user("sally", "sallypass", "employer")
        assert employer is not None
        position = open_position(user_id=employer.id, title="IT Support", number_of_positions=2, description="Help with IT issues")
        assert position is not None
        assert position.title == "IT Support"
        assert position.number_of_positions == 2
        assert position.description == "Help with IT issues"

    def test_open_position(self):
        # Create a company first for employer
        company = create_company("Test Company", "A test company")

        position_count = 2
        employer = create_user("sally", "sallypass", "employer", company_id=company.id)
        assert employer is not None
        assert isinstance(employer, Employer)

        position = open_position(user_id=employer.id, title="IT Support", number_of_positions=position_count)
        positions = get_positions_by_employer(employer.id)
        assert position is not None
        assert position.number_of_positions == position_count
        assert len(positions) > 0
        assert any(p.id == position.id for p in positions)

        invalid_position = open_position(user_id=-1, title="Developer", number_of_positions=1)
        assert invalid_position is None


    def test_create_application(self):
        # Create a company first for staff and employer
        company = create_company("Test Company", "A test company")

        position_count = 3
        staff = create_user("linda", "lindapass", "staff", company_id=company.id)
        assert staff is not None
        assert isinstance(staff, Staff)

        student = create_user("hank", "hankpass", "student")
        assert student is not None
        assert isinstance(student, Student)

        employer = create_user("ken", "kenpass", "employer", company_id=company.id)
        assert employer is not None
        assert isinstance(employer, Employer)

        position = open_position(user_id=employer.id, title="Database Manager", number_of_positions=position_count)
        invalid_position = open_position(user_id=-1, title="Developer", number_of_positions=1)
        assert invalid_position is None
        assert position is not None
        added_application = add_student_to_shortlist(student.id, position.id, staff.id)
        assert added_application
        applications = get_shortlist_by_student(student.id)
        assert any(s.id == added_application.id for s in applications)


    def test_application_state_transitions(self):
        # Create a company first for staff and employer
        company = create_company("Test Company", "A test company")

        position_count = 3
        student = create_user("jack", "jackpass", "student")
        assert student is not None
        assert isinstance(student, Student)

        staff = create_user("pat", "patpass", "staff", company_id=company.id)
        assert staff is not None
        assert isinstance(staff, Staff)

        employer = create_user("frank", "pass", "employer", company_id=company.id)
        assert employer is not None
        assert isinstance(employer, Employer)

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
        # Create a company first for staff and employer
        company = create_company("Test Company", "A test company")

        student = create_user("john", "johnpass", "student")
        assert student is not None
        assert isinstance(student, Student)

        staff = create_user("tim", "timpass", "staff", company_id=company.id)
        assert staff is not None
        assert isinstance(staff, Staff)

        employer = create_user("joe", "joepass", "employer", company_id=company.id)
        assert employer is not None
        assert isinstance(employer, Employer)

        position = open_position(user_id=employer.id, title="Software Intern", number_of_positions=4)
        assert position is not None
        application = add_student_to_shortlist(student.id, position.id, staff.id)
        applications = get_shortlist_by_student(student.id)
        assert any(application.id == s.id for s in applications)
        assert len(applications) > 0

    def test_no_duplicate_usernames_across_subclasses(self):
        # Create a company first for staff
        company = create_company("Test Company", "A test company")

        # Test that username uniqueness is enforced across all User subclasses
        create_user("john", "pass1", "student")

        # Trying to create another user with same username should fail
        duplicate_staff = create_user("john", "pass2", "staff", company_id=company.id)
        assert duplicate_staff is None

    def test_login_works_with_inheritance(self):
        # Test that login still works correctly with inheritance
        student = create_user("john", "johnpass", "student")
        assert student is not None

        # Login should return a token
        token = login("john", "johnpass")
        assert token is not None

        # Login with wrong password should fail
        token = login("john", "wrongpass")
        assert token is None

    def test_get_user_returns_correct_subclass(self):
        # Create a company first for staff and employer
        company = create_company("Test Company", "A test company")

        # Test that get_user returns the correct subclass instance
        student = create_user("john", "johnpass", "student")
        staff = create_user("jane", "janepass", "staff", company_id=company.id)
        employer = create_user("joe", "joepass", "employer", company_id=company.id)

        retrieved_student = get_user(student.id)
        retrieved_staff = get_user(staff.id)
        retrieved_employer = get_user(employer.id)

        assert isinstance(retrieved_student, Student)
        assert isinstance(retrieved_staff, Staff)
        assert isinstance(retrieved_employer, Employer)

        # All should still be instances of User
        assert isinstance(retrieved_student, User)
        assert isinstance(retrieved_staff, User)
        assert isinstance(retrieved_employer, User)


class CompanyIntegrationTests(unittest.TestCase):

    def test_create_company(self):
        company = create_company("Acme Corp", "A test company")
        assert company is not None
        assert company.name == "Acme Corp"
        assert company.description == "A test company"
        assert company.id is not None

    def test_get_company(self):
        company = create_company("Test Corp", "Description")
        retrieved = get_company(company.id)
        assert retrieved is not None
        assert retrieved.id == company.id
        assert retrieved.name == "Test Corp"

    def test_get_company_not_found(self):
        result = get_company(9999)
        assert result is None

    def test_get_all_companies(self):
        create_company("Company A", "First company")
        create_company("Company B", "Second company")
        companies = get_all_companies()
        assert len(companies) >= 2

    def test_update_company(self):
        company = create_company("Old Name", "Old description")
        updated = update_company(company.id, name="New Name", description="New description")
        assert updated is not None
        assert updated.name == "New Name"
        assert updated.description == "New description"

    def test_update_company_partial(self):
        company = create_company("Original", "Original description")
        updated = update_company(company.id, name="Updated Name")
        assert updated.name == "Updated Name"
        assert updated.description == "Original description"

    def test_update_company_not_found(self):
        result = update_company(9999, name="Test")
        assert result is None

    def test_delete_company(self):
        company = create_company("To Delete", "Will be deleted")
        company_id = company.id
        result = delete_company(company_id)
        assert result is True
        assert get_company(company_id) is None

    def test_delete_company_not_found(self):
        result = delete_company(9999)
        assert result is False

    def test_delete_company_cascades_staff_and_employers(self):
        # Create a company with staff and employers
        company = create_company("Cascade Test", "Testing cascade delete")
        staff = create_user("cascade_staff", "pass", "staff", company_id=company.id)
        employer = create_user("cascade_employer", "pass", "employer", company_id=company.id)

        staff_id = staff.id
        employer_id = employer.id
        company_id = company.id

        # Delete the company
        result = delete_company(company_id)
        assert result is True

        # Verify staff and employer were also deleted
        assert get_user(staff_id) is None
        assert get_user(employer_id) is None

    def test_company_get_json(self):
        company = create_company("JSON Test", "Testing JSON output")
        staff = create_user("json_staff", "pass", "staff", company_id=company.id)
        employer = create_user("json_employer", "pass", "employer", company_id=company.id)

        json_data = company.get_json()
        assert json_data['id'] == company.id
        assert json_data['name'] == "JSON Test"
        assert json_data['description'] == "Testing JSON output"
        assert len(json_data['staff']) == 1
        assert len(json_data['employers']) == 1
        assert json_data['staff'][0]['username'] == "json_staff"
        assert json_data['employers'][0]['username'] == "json_employer"
