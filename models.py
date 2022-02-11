from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """ Connect to database. """

    db.app = app
    db.init_app(app)

# def find_currency_code(country_name):
#     """ Return currency code from 'country_name' from API @ 
#         https://restcountries.com/#api-endpoints-v2-name
#     """

#     response = requests.get(f"https://restcountries.com/v2/name/{country_name}?fields=name,currencies")


#     for city in response.json():
#         if city["name"].lower() in country_name.lower():
#             return city["currencies"][0]["code"]

class Traveler(db.Model):
    """ Users aka 'Travelers' class """

    __tablename__ = "traveler"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    first_name = db.Column(
        db.Text,
        nullable=False
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    home_country = db.Column(
        db.Integer,
        db.ForeignKey('country.id')
    )

    country = db.relationship("Country")

    cities = db.relationship("City", 
        secondary = "traveler_city",
        backref = "travelers")

    def __repr__(self):
        return f"<Traveler #{self.id}: {self.first_name} {self.last_name}, {self.email}>"

    def assign_city(self, city):
        """ Assign City to traveler.
            Return False if Traveler-City relationship exists, otherwise return True.
        """

        if TravelerCity.query.filter(TravelerCity.city_id == city.id, TravelerCity.traveler_id == self.id).first():
            return False

        travelercity = TravelerCity(city_id = city.id, traveler_id = self.id)

        db.session.add(travelercity)
        db.session.commit()

        return True

    def updateInfo(self, first_name, last_name, email, home_country):
        """ Update personal info """
        
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.home_country = home_country.id

        db.session.commit()

    @classmethod
    def signup(cls, first_name, last_name, email, password, home_country):
        """ Sign up traveler. Hashes password and adds traveler to system. """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        country = Country.new_country(home_country)

        traveler = Traveler(
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = hashed_pwd,
            home_country = country.id
        )

        db.session.add(traveler)
        db.session.commit()
        return traveler

    @classmethod
    def authenticate(cls, email, password):
        """ Find user with `email` and `password`.
            If can't find matching user (or if password is wrong), returns False.
        """

        traveler = cls.query.filter_by(email=email).first()

        if traveler:
            is_auth = bcrypt.check_password_hash(traveler.password, password)
            if is_auth:
                return traveler

        return False

class City(db.Model):
    """ City class """

    __tablename__ = "city"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.Text,
        nullable=False
    )

    country_id = db.Column(
        db.Integer,
        db.ForeignKey('country.id')
    )

    country = db.relationship('Country')

    def __repr__(self):
        return f"<City #{self.id}: {self.name}>"

    @classmethod
    def new_city(cls, city_name, country_id):
        """ Adds new city and country to system if none exists. """

        city = City.query.filter(City.name == city_name).one_or_none()

        if not city:
            city = City(name = city_name, country_id = country_id)

            db.session.add(city)
            db.session.commit()

        return city

    @classmethod
    def delete_city(cls, city):
        """ Delete city only if no traveler is associated to it """

        if not TravelerCity.query.filter(TravelerCity.city_id == city.id).all():
            db.session.delete(city)
            db.session.commit()

class Country(db.Model):
    """ Country class """

    __tablename__ = "country"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.Text,
        unique=True,
        nullable=False
    )

    currency_code = db.Column(
        db.Text
    )

    cities = db.relationship("City", cascade="all, delete")

    def __repr__(self):
        return f"<Country #{self.id}: {self.name}>"

    @classmethod
    def new_country(cls, country_name):
        """ Adds new country to system if none exists. """

        country = Country.query.filter(Country.name == country_name).one_or_none()

        if not country:
            currency_code = Country.find_currency_code(country_name)

            country = Country(name = country_name, currency_code = currency_code)

            db.session.add(country)
            db.session.commit()

        return country
    
    @classmethod
    def find_currency_code(cls, country_name):
        """ Find currency code from API. Returns currency code. """
        response = requests.get("https://restcountries.com/v2/all?fields=name,currencies")

        for country in response.json():
            if country["name"] == country_name:
                return country["currencies"][0]["code"]

class TravelerCity(db.Model):
    """ Traveler - City relationship class """

    __tablename__ = "traveler_city"

    traveler_id = db.Column(
        db.Integer,
        db.ForeignKey('traveler.id', ondelete="cascade"),
        primary_key=True
    )

    city_id = db.Column(
        db.Integer,
        db.ForeignKey('city.id', ondelete="cascade"),
        primary_key=True
    )