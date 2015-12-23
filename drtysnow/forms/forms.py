from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class RunReview(Form):
    run_name = StringField('run_name', validators=[DataRequired()])
    resort_name = StringField('resort_name', validators=[DataRequired()])

    
