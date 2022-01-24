from flask import Flask, render_template, flash, redirect, session, request, jsonify, g
from models import db, connect_db, Traveler, City, Country, TravelerCity
from forms import AddTravelerForm, LoginTravelerForm, AddCityForm
from sqlalchemy.exc import IntegrityError
import requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///traveler_tracker"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config['SECRET_KEY'] = "abcdef"

TRAVELER_KEY = "current_traveler"

connect_db(app)
# db.create_all()

@app.before_request
def add_traveler_to_g():
    """ If logged in, add current traveler to Flask global. """

    if TRAVELER_KEY in session:
        g.traveler = Traveler.query.get(session[TRAVELER_KEY])

    else:
        g.traveler = None

@app.route("/")
def home():
    """ Home page. """

    if g.traveler:
        cities = g.traveler.cities
        

        return render_template("index.html", cities = cities)
    else:
        return redirect("/signup")



############################################################
# Traveler methods

def login(traveler):
    """ Login traveler. """

    session[TRAVELER_KEY] = traveler.id

def logout():
    """ Logout traveler. """

    if TRAVELER_KEY in session:
        del session[TRAVELER_KEY]

############################################################
# Traveler routes

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """ Sign up form for new travelers. """

    form = AddTravelerForm()

    if form.validate_on_submit():
        try:
            traveler = Traveler.signup(
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                password = form.password.data,
                email = form.email.data
            )

        except IntegrityError:
            flash("Email already taken", 'danger')
            return render_template('signup.html', form = form)

        login(traveler)

        return redirect("/")

    return render_template('signup.html', form = form)

@app.route("/login", methods=["GET", "POST"])
def login_traveler():
    """ Login form for existing travelers. """

    form = LoginTravelerForm()

    if form.validate_on_submit():
        traveler = Traveler.authenticate(
            email = form.email.data,
            password = form.password.data
        )

        if traveler:
            login(traveler)
            return redirect("/")

        flash("Invalid email/password")

    return render_template('login.html', form = form)

@app.route("/logout")
def logout_traveler():
    """ Logout current traveler """

    logout()

    flash("Successfully logged out.")
    return redirect("/login")

############################################################
# City/country methods

def find_currency_code(JSONresponse, country_name):
    for country in JSONresponse:
        if country["name"] == country_name:
            return country["currencies"][0]["code"]

############################################################
# City/country routes

@app.route("/city/add", methods=["GET", "POST"])
def add_city():
    """ Add city to current traveler. Add country with currency code from API @ 
        https://restcountries.com/#api-endpoints-v2-name
    """

    form = AddCityForm()

    response = requests.get("https://restcountries.com/v2/all?fields=name,currencies")

    form.country_name.choices = [(c["name"], c["name"]) for c in response.json()]

    if form.validate_on_submit():

        currency_code = find_currency_code(response.json(), form.country_name.data)
        
        country = Country.new_country(form.country_name.data, currency_code)
        city = City.new_city(form.city_name.data, country.id)
        g.traveler.assign_city(city)

        return redirect("/")

    return render_template("add_city.html", form = form)

@app.route("/city/<int:city_id>/remove", methods=["POST"])
def remove_city(city_id):
    """ Remove city from current traveler's home """

    city = City.query.get_or_404(city_id)

    travelercity = TravelerCity.query.filter(TravelerCity.traveler_id == g.traveler.id, 
                                            TravelerCity.city_id == city_id
                                            ).first()

    db.session.delete(travelercity)
    db.session.commit()

    City.delete_city(city) # Only delete city if not associated with any traveler

    return redirect("/")
        