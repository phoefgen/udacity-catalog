# import form processors:
from flask.ext.wtf import Form

# import field types:
from wtforms import StringField, BooleanField, IntegerField, SelectField
from wtforms import FileField, TextAreaField, RadioField

# import field validators:
from wtforms.validators import DataRequired

class ReviewRun(Form):
    rating = SelectField('rating', choices=[('1','1 - awful!'),
                                            ('2','2'),
                                            ('3','3'),
                                            ('4','4'),
                                            ('5','5'),
                                            ('6','6'),
                                            ('7','7'),
                                            ('8','8'),
                                            ('9','9'),
                                            ('10','10 - perfect!')])
    top_hazard = BooleanField('top_hazard', default=False)
    mid_hazard = BooleanField('mid_hazard', default=False)
    bot_hazard = BooleanField('bot_hazard', default=False)
    comment = TextAreaField('comments')

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
