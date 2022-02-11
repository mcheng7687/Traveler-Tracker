from app import app, login
from unittest import TestCase
from models import db, connect_db, Traveler, City, Country

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///traveler_tracker_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

class TravelerTrackerTestCase(TestCase):
    """ Test all functions in Traveler Tracker app.py """

    def setUp(self):
        """ Clean up any Travelers in database and adds new Traveler """
        db.drop_all()
        db.create_all()

        traveler = Traveler.signup(first_name = "Mickey", 
                                    last_name = "Mouse", 
                                    email = "MickeyMouse@gmail.com", 
                                    password = "HouseOfMouse", 
                                    home_country = "United States of America")
        country = Country.new_country("United States of America")
        city = City.new_city("San Francisco", country.id)

        traveler.assign_city(city)

    def tearDown(self):
        """ Clean up any database transactions """
        db.session.rollback()

    def test_homepage(self):
        """ Test home page """
        with app.test_client() as client:
            client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                                 "password":"HouseOfMouse"}, 
                                                 follow_redirects = True)

            res = client.get("/")
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2 class="page-header"> Here are your cities: </h2>',html)
            self.assertIn('<div id="SanFrancisco">', html)

    def test_signup_form(self):
        """ Test sign up page for a new Traveler. """
        with app.test_client() as client:
            res = client.get("/signup")
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2 class="page-header">Sign Up</h2>', html)

    def test_signup_success(self):
        """ Test successful signup of new Traveler. """
        with app.test_client() as client:
            res = client.post("/signup", data = {'first_name':'Goofy',
                                                 'last_name':"Goof",
                                                 "email":"GoofyGoof@gmail.com",
                                                 "password":"GoofyisGoofy",
                                                 "current_country":"Japan"}, 
                                                 follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Hello Goofy!', html)

    def test_signup_failure(self):
        """ Test failed signup of new Traveler. This can only be caused by 
        attempting signup using same email of another Traveler. """
        with app.test_client() as client:
            res = client.post("/signup", data = {'first_name':'Goofy',
                                                 'last_name':"Goof",
                                                 "email":"MickeyMouse@gmail.com",
                                                 "password":"GoofyisGoofy",
                                                 "current_country":"Japan"}, 
                                                 follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Email already taken', html)

    def test_login_form(self):
        """ Test login form for a Traveler. """
        with app.test_client() as client:
            res = client.get("/login")
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2 class="page-header">Login</h2>', html)

    def test_login_successful(self):
        """ Test successful login of an existing Traveler. """
        with app.test_client() as client:
            res = client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                                 "password":"HouseOfMouse"}, 
                                                 follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Hello Mickey!', html)

    def test_login_failure(self):
        """ Test failed login attempt of an existing Traveler. This can be 
        caused by the incorrect combination of email & password. """
        with app.test_client() as client:
            res = client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                                 "password":"GoofyisGoofy"}, 
                                                 follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Invalid email/password', html)

    def test_logout(self):
        """ Test logout. """
        with app.test_client() as client:
            client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                                 "password":"HouseOfMouse"}, 
                                                 follow_redirects = True)

            res = client.get("/logout", follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Successfully logged out.',html)

    def test_update_info(self):
        """ Update current traveler info form. """
        with app.test_client() as client:
            client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                          "password":"HouseOfMouse"}, 
                                          follow_redirects = True)

            res = client.get("/current_traveler")
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2 class="page-header">Update My Info</h2>', html)
            self.assertIn('value="Mickey"', html)
            self.assertIn('value="MickeyMouse@gmail.com"', html)

    def test_update_info_successful(self):
        """ Successful update of current traveler info.  """
        with app.test_client() as client:
            client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                                 "password":"HouseOfMouse"}, 
                                                 follow_redirects = True)

            res = client.post("/current_traveler", data = {"first_name":"Minnie",
                                                            "last_name":"Mouse",
                                                            "email":"MinnieMouse@gmail.com",
                                                            "current_country":"Japan"}, 
                                                            follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Updated info!', html)
            self.assertIn('Hello Minnie!', html)

    def test_update_info_failure(self):
        """ Test failed update info of current traveler. This can only be caused by 
        attempting update using same email of another Traveler. """
        with app.test_client() as client:
            Traveler.signup(first_name = "Goofy",
                            last_name = "Goof", 
                            email = "GoofyGoof@gmail.com", 
                            password = "GoofyisGoofy", 
                            home_country = "United States of America")                                  

            client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                                 "password":"HouseOfMouse"}, 
                                                 follow_redirects = True)

            res = client.post("/current_traveler", data = {"first_name":"Mickey",
                                                            "last_name":"Mouse",
                                                            "email":"GoofyGoof@gmail.com",
                                                            "current_country":"Japan"}, 
                                                            follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Email already taken', html)

    def test_add_city_form(self):
        """ Test add city form. """
        with app.test_client() as client:
            client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                          "password":"HouseOfMouse"}, 
                                          follow_redirects = True)

            res = client.get("/city/add")
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2 class="page-header">Add City</h2>', html)

    def test_found_city_API(self):
        """ Test whether weather API can find specified city. """
        with app.test_client() as client:
            client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                          "password":"HouseOfMouse"})

            res = client.post("/city/add", data = {"country_name":"Japan",
                                                    "city_name":"Tokyo"})
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2 class="page-header">Verify Your New City</h2>', html)
            self.assertIn('<h6>Found Tokyo in Japan. Are you sure you want to add this city?</h6>', html)

    def test_add_city(self):
        """ Test successful add of another city. """
        with app.test_client() as client:
            client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                          "password":"HouseOfMouse"})

            res = client.post("/verified", data = {"country_name":"Japan",
                                                    "city_name":"Tokyo"}, 
                                                    follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('New city added!', html)
            self.assertIn('<div id="Tokyo">', html)

    def test_cannot_find_city_API(self):
        """ Test whether API can't find specified city. """
        with app.test_client() as client:
            client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                          "password":"HouseOfMouse"})

            res = client.post("/city/add", data = {"country_name":"Japan",
                                                    "city_name":"abcdefgh"})
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Could not find abcdefgh in Japan. Please re-enter the city or choose another country.', html)

    def test_remove_city(self):
        """ Test removing a city. """
        with app.test_client() as client:
            client.post("/login", data = {"email":"MickeyMouse@gmail.com",
                                                 "password":"HouseOfMouse"}, 
                                                 follow_redirects = True)

            res = client.post("/city/1/remove", follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2 class="page-header"> Here are your cities: </h2>',html)
            self.assertNotIn('<div id="SanFrancisco">', html)