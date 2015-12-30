# import form processors:
from flask.ext.wtf import Form

# import field types:
from wtforms import StringField, BooleanField, IntegerField, SelectField
from wtforms import FileField, TextAreaField

# import field validators:
from wtforms.validators import DataRequired

class RunReview(Form):
    run_name = StringField('run_name', validators=[DataRequired()])
    resort_name = StringField('resort_name', validators=[DataRequired()])


class CreateResort(Form):
    name = StringField('name', validators=[DataRequired()])
    location = StringField('location', validators=[DataRequired()])
    image = FileField('image')
    summary = TextAreaField('summary', validators=[DataRequired()])

class CreateRun(Form):
    name = StringField('name', validators=[DataRequired()])
    summary = TextAreaField('summary', validators=[DataRequired()])
    # TODO: image = FileField('image')
    image = StringField('name')
