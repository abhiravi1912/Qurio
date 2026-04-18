from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField,
    SelectField, FileField
)
from wtforms.validators import DataRequired, Email, Optional, Length, EqualTo


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Register As', choices=[('student', 'Student'), ('faculty', 'Faculty'), ('admin', 'Admin')], validators=[DataRequired()])
    faculty = SelectField('Select Faculty', coerce=int, validators=[Optional()])
    admin_code = StringField('Admin Secret Code', validators=[Optional()])
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class DoubtForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Math', 'Mathematics'),
        ('Physics', 'Physics'),
        ('Computer Science', 'Computer Science'),
        ('Chemistry', 'Chemistry'),
        ('Biology', 'Biology'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    submit = SubmitField('Post Doubt')


class AnswerForm(FlaskForm):
    content = TextAreaField('Your Answer', validators=[DataRequired()])
    submit = SubmitField('Post Answer')


class NoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    file = FileField('Upload File', validators=[FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'mp4', 'doc', 'docx', 'ppt', 'pptx'])])
    submit = SubmitField('Upload Note')


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')


class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Create Quiz')


class SubmissionForm(FlaskForm):
    answer = TextAreaField('Your Answer', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    avatar_color = StringField('Avatar Color', validators=[Optional()])
    submit = SubmitField('Save Changes')