from email.policy import default
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, BooleanField, DateTimeField, SelectField, PasswordField
from wtforms.validators import InputRequired, Email

class AddTravelerForm(FlaskForm):
    """Add Traveler form"""

    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])

class LoginTravelerForm(FlaskForm):
    """Login Traveler form"""

    email = StringField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class AddCityForm(FlaskForm):
    """Add City form"""

    # country_name = StringField("Country", validators=[InputRequired()])
    country_name = SelectField("Country", validators=[InputRequired()], default="United States of America")
    city_name = StringField("City Name", validators=[InputRequired()])