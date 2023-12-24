from flask_wtf import FlaskForm
from wtforms import PasswordField,StringField,SubmitField
from wtforms.validators import DataRequired, URL

class Add(FlaskForm):
    title = StringField("Movie Title:", validators=[DataRequired()])
    add_button = SubmitField("Add")

class Add_Data(FlaskForm):
    Rating = StringField('rating for this movie:', validators=[DataRequired()])
    review = StringField("Review about this movie:", validators=[DataRequired()])
    add = SubmitField("Add")

class Update_Data(FlaskForm):
    Rating = StringField('rating for this movie:', validators=[DataRequired()])
    review = StringField("Review about this movie:", validators=[DataRequired()])
    add = SubmitField("Update")