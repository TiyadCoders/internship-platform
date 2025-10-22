import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Employer, Position, Shortlist, Staff, Student
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
    decide_shortlist
)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob", "bobpass")
        assert user.username == "bob"

    def test_new_student(self):
            student = Student("john", "johnpass")
            assert student.username == "john"
            assert student.role == "student"

    def test_new_staff(self):
        staff = Staff("jim", "jimpass")
        assert staff.username == "jim"
        assert staff.role == "staff"

    def test_new_employer(self):
        employer = Employer("alice", "alicepass")
        assert employer.username == "alice"
        assert employer.role == "employer"

    def test_new_position(self):
        position = Position("Software Developer", 10, 5) 
        assert position.title == "Software Developer"
        assert position.employer_id == 10
        assert position.status == "open"
        assert position.number_of_positions == 5

    def test_new_shortlist(self):
        shortlist = Shortlist(1,2,3)
        assert shortlist.student_id == 1
        assert shortlist.position_id == 2
        assert shortlist.staff_id == 3
        assert shortlist.status == "pending"

    # pure function no side effects or integrations called
    def test_get_json(self):
        user = User("bob", "bobpass")
        user_json = user.get_json()
        self.assertEqual(user_json["username"], "bob")
        self.assertTrue("id" in user.get_json())
    
    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password)
        user = User("bob", password)
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password)
        assert user.check_password(password)

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    
    with app.app_context():
        create_db()
        yield app.test_client()
        db.drop_all()


def test_authenticate():
    user = create_user("bob", "bobpass")
    assert login("bob", "bobpass") != None

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
        employer = create_user("sally", "sallypass", "employer")
        position = open_position("IT Support", employer.id, 2)
        positions = get_positions_by_employer(employer.id)
        assert [p.id == position.id for p in positions]

    def test_add_to_shortlist(self):

        staff = create_user("linda", "lindapass", "staff")
        student = create_user("hank", "hankpass", "student")
        employer =  create_user("ken", "kenpass", "employer")
        position = open_position("Database Manager", employer.id, 3)
        added_shortlist = add_student_to_shortlist(student.id, position.id ,staff.id)
        assert (added_shortlist)
        shortlists = get_shortlist_by_student(student.id)
        assert [s.id == added_shortlist for s in shortlists]

    def test_decide_shortlist(self):

        student = create_user("jack", "jackpass", "student")
        staff = create_user ("pat", "patpass", "staff")
        employer =  create_user("frank", "pass", "employer")
        position = open_position("Intern", employer.id, 4)
        add_student_to_shortlist(student.id, position.id ,staff.id)
        decide_shortlist(student.id, position.id, "accepted")
        shortlists = get_shortlist_by_student(student.id)
        assert [s.status == "approved" for s in shortlists]
        assert position.number_of_positions == 3

    def test_student_view_shortlist(self):

        student = create_user("john", "johnpass", "student")
        staff = create_user ("tim", "timpass", "staff")
        employer =  create_user("joe", "joepass", "employer")
        position = open_position("Software Intern", employer.id, 4)
        shortlist = add_student_to_shortlist(student.id, position.id ,staff.id)
        shortlists = get_shortlist_by_student(student.id)
        assert [shortlist.id == s.id for s in shortlists]

    # Tests data changes in the database
    #def test_update_user(self):
    #    update_user(1, "ronnie")
    #   user = get_user(1)
    #   assert user.username == "ronnie"

