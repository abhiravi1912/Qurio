from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )
    submit = SubmitField("Register")

from wtforms import TextAreaField

from wtforms import SelectField

class DoubtForm(FlaskForm):
    title = StringField("Doubt Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])

    category = SelectField(
        "Category",
        choices=[
            ("Math", "Math"),
            ("Physics", "Physics"),
            ("Computer Science", "Computer Science")
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField("Post Doubt")

class AnswerForm(FlaskForm):
    content = TextAreaField(
        "Your Answer",
        validators=[DataRequired()]
    )
    submit = SubmitField("Post Answer")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


