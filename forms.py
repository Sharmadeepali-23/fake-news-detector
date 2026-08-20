from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign In')

class NewsDetectionForm(FlaskForm):
    title = StringField('News Title / Headline (Optional)', validators=[Optional(), Length(max=255)])
    content = TextAreaField('News Article Content', validators=[
        DataRequired(message="Please paste or type news article content."),
        Length(min=20, message="Article content must be at least 20 characters long.")
    ])
    submit = SubmitField('Analyze Article')

class SearchHistoryForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    filter_by = SelectField('Filter Result', choices=[
        ('ALL', 'All Predictions'),
        ('REAL NEWS', 'Real News Only'),
        ('FAKE NEWS', 'Fake News Only')
    ], default='ALL')
    submit = SubmitField('Search')
