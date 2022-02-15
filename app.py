from flask import Flask, render_template, flash, redirect, session, request, g
from models import db, connect_db, Traveler, City, Country, TravelerCity
from forms import TravelerForm, LoginTravelerForm, AddCityForm, UpdateTravelerForm
from sqlalchemy.exc import IntegrityError
import requests
import os
from API_Keys import WEATHER_API_KEY

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///traveler_tracker')
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL.replace("postgres://","postgresql://")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'abcdef')

TRAVELER_KEY = "current_traveler"

connect_db(app)

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

@app.route("/help")
def help():
    """ Help instructions. """
    return render_template("help.html")

@app.route("/secret")
def secret():
    """ THIS IS A SECRET! SHHH! """
    return render_template("secret.html")

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

    form = TravelerForm()

    response = requests.get("https://restcountries.com/v2/all?fields=name,currencies")
    form.current_country.choices = [(c["name"], c["name"]) for c in response.json()]

    if form.validate_on_submit():
        try:
            traveler = Traveler.signup(
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                password = form.password.data,
                email = form.email.data,
                home_country = form.current_country.data
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

@app.route("/current_traveler", methods=["GET", "POST"])
def update_user():
    """ Update current traveler info """

    form = UpdateTravelerForm(obj=g.traveler)

    response = requests.get("https://restcountries.com/v2/all?fields=name,currencies")

    form.current_country.choices = [(c["name"], c["name"]) for c in response.json()]

    if form.validate_on_submit():
        home_country = Country.new_country(form.current_country.data)

        try:
            g.traveler.updateInfo(form.first_name.data, form.last_name.data, form.email.data, home_country)

            flash("Updated info!")
            return redirect ("/")

        except IntegrityError:
            db.session.rollback()
            flash("Email already taken", 'danger')
        
    form.current_country.data = g.traveler.country.name

    return render_template("update_traveler.html", form = form)

@app.route("/logout")
def logout_traveler():
    """ Logout current traveler """

    logout()

    flash("Successfully logged out.")
    return redirect("/login")

############################################################
# City/country methods

def verify_city_country(city, country):
    response = requests.get("http://api.weatherapi.com/v1/search.json", params={"key": WEATHER_API_KEY, "q": city})

    for c in response.json():
        if (city in c["name"] or c["name"] in city) and (country in c["country"] or c["country"] in country):
            return c["name"]
    
    return False


############################################################
# City/country routes

@app.route("/city/add", methods=["GET", "POST"])
def add_city_form():
    """ Add city to current traveler. Add country with currency code from API @ 
        https://restcountries.com/#api-endpoints-v2-name
    """

    form = AddCityForm()

    response = requests.get("https://restcountries.com/v2/all?fields=name,currencies")

    form.country_name.choices = [(c["name"], c["name"]) for c in response.json()]

    if form.validate_on_submit():

        city_name = verify_city_country(form.city_name.data, form.country_name.data)

        if city_name:
            return render_template("verify_city.html", city_name=city_name, 
                                                        country_name=form.country_name.data)
                                                    
        flash(f"Could not find {form.city_name.data} in {form.country_name.data}. Please re-enter the city or choose another country.")

    return render_template("add_city.html", form = form)

@app.route("/verified", methods=["POST"])
def add_city():

    # city_name = request.args.get("city_name")
    # country_name = request.args.get("country_name")
    city_name = request.form["city_name"]
    country_name = request.form["country_name"]
        
    country = Country.new_country(country_name)
    city = City.new_city(city_name, country.id)
    g.traveler.assign_city(city)

    flash("New city added!")
    return redirect("/")

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


############################################################
# Testing routes

@app.route("/test", methods=["GET", "POST"])
def tester():
    """ This is for testing features only. To be used by developers only! """

    # form = AddCityForm()

    # response = requests.get("https://restcountries.com/v2/all?fields=name,currencies")

    # form.country_name.choices = [(c["name"], c["name"]) for c in response.json()]

    # if form.validate_on_submit():

    #     if verify_city_country(form.city_name.data, form.country_name.data):
    #         flash("Test successful!")

    #     else:
    #         flash("No match.")

    # return render_template("test.html", form = form)