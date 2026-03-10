from app import db
from datetime import datetime
from flask_login import UserMixin
from app import login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="student")

    # Student → Faculty mapping
    faculty_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    students = db.relationship(
        "User",
        backref=db.backref("faculty", remote_side=[id]),
        lazy=True
    )

    doubts = db.relationship("Doubt", backref="author", lazy=True)
    answers = db.relationship("Answer", backref="user", lazy=True)




    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

from datetime import datetime

class Doubt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)   
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doubt_id = db.Column(
        db.Integer,
        db.ForeignKey("doubt.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


    # 👇 NEW: link answer to user
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Note(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    content = db.Column(db.Text, nullable=False)

    file = db.Column(db.String(200))

    created_at = db.Column(db.DateTime)

    faculty_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )



class NoteComment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime)

    note_id = db.Column(
        db.Integer,
        db.ForeignKey("note.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )