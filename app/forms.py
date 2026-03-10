from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Optional
from wtforms import SelectField

class RegisterForm(FlaskForm):

    username = StringField("Username", validators=[DataRequired()])

    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired()])

    role = SelectField(
        "Register As",
        choices=[("student","Student"),("faculty","Faculty")],
        validators=[DataRequired()]
    )

    faculty = SelectField(
        "Select Faculty",
        coerce=int,
        validators=[Optional()]
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



from wtforms import TextAreaField, FileField
from wtforms.validators import DataRequired

class NoteForm(FlaskForm):

    title = StringField("Title", validators=[DataRequired()])

    content = TextAreaField("Content", validators=[DataRequired()])

    file = FileField("Upload File")

    submit = SubmitField("Upload Note")



class CommentForm(FlaskForm):

    content = TextAreaField("Comment", validators=[DataRequired()])

    submit = SubmitField("Post Comment")

    