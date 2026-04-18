from flask import Blueprint, abort, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
import os

from app import db, bcrypt
from app.models import (
    User, Doubt, Answer, Vote, Note, NoteComment,
    Quiz, Question, Submission, QuizAnswer
)
from app.forms import (
    RegisterForm, LoginForm, DoubtForm, AnswerForm,
    NoteForm, CommentForm, ProfileForm
)

main = Blueprint('main', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ─── HOME ────────────────────────────────────────────────────────
@main.route('/')
def home():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'newest')

    doubts_query = Doubt.query
    if query:
        doubts_query = doubts_query.filter(
            (Doubt.title.ilike(f'%{query}%')) |
            (Doubt.description.ilike(f'%{query}%'))
        )
    if category:
        doubts_query = doubts_query.filter_by(category=category)
    if status:
        doubts_query = doubts_query.filter_by(status=status)
    if sort == 'oldest':
        doubts_query = doubts_query.order_by(Doubt.created_at.asc())
    else:
        doubts_query = doubts_query.order_by(Doubt.created_at.desc())

    doubts = doubts_query.all()
    categories = ['Math', 'Physics', 'Computer Science', 'Chemistry', 'Biology', 'Other']
    return render_template('home.html', doubts=doubts, categories=categories,
                           current_query=query, current_category=category,
                           current_status=status, current_sort=sort)


# ─── AUTH ────────────────────────────────────────────────────────
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterForm()
    faculty_users = User.query.filter_by(role='faculty').all()
    form.faculty.choices = [(0, '-- Select Faculty --')] + [(f.id, f.username) for f in faculty_users]

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        faculty_id = None
        is_admin = False

        if form.role.data == 'student' and form.faculty.data and form.faculty.data != 0:
            faculty_id = form.faculty.data
        elif form.role.data == 'admin':
            # Check secret code
            if form.admin_code.data != 'admin123':
                flash('Invalid admin code!', 'danger')
                return render_template('register.html', form=form)
            is_admin = True
            
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw,
            role=form.role.data,
            faculty_id=faculty_id,
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


# ─── DASHBOARD ───────────────────────────────────────────────────
@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        my_doubts = Doubt.query.filter_by(user_id=current_user.id).order_by(Doubt.created_at.desc()).limit(5).all()
        my_submissions = Submission.query.filter_by(student_id=current_user.id).order_by(Submission.submitted_at.desc()).limit(5).all()
        recent_notes = Note.query.order_by(Note.created_at.desc()).limit(5).all()
        return render_template('dashboard.html', my_doubts=my_doubts,
                               my_submissions=my_submissions, recent_notes=recent_notes)
    else:
        my_students = User.query.filter_by(faculty_id=current_user.id).all()
        student_doubts = Doubt.query.join(User, Doubt.user_id == User.id).filter(
            User.faculty_id == current_user.id
        ).order_by(Doubt.created_at.desc()).limit(10).all()
        my_quizzes = Quiz.query.filter_by(faculty_id=current_user.id).order_by(Quiz.created_at.desc()).limit(5).all()
        my_notes = Note.query.filter_by(faculty_id=current_user.id).order_by(Note.created_at.desc()).limit(5).all()
        unanswered = Doubt.query.join(User, Doubt.user_id == User.id).filter(
            User.faculty_id == current_user.id, Doubt.status == 'open'
        ).count()
        return render_template('dashboard.html', my_students=my_students,
                               student_doubts=student_doubts, my_quizzes=my_quizzes,
                               my_notes=my_notes, unanswered=unanswered)


# ─── DOUBTS ──────────────────────────────────────────────────────
@main.route('/post_doubt', methods=['GET', 'POST'])
@login_required
def post_doubt():
    form = DoubtForm()
    if form.validate_on_submit():
        doubt = Doubt(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            user_id=current_user.id
        )
        db.session.add(doubt)
        current_user.points += 2
        db.session.commit()
        flash('Your doubt has been posted!', 'success')
        return redirect(url_for('main.home'))
    return render_template('post_doubt.html', form=form)


@main.route('/category/<string:category_name>')
def category_filter(category_name):
    return redirect(url_for('main.home', category=category_name))


@main.route('/doubt/<int:doubt_id>', methods=['GET', 'POST'])
@login_required
def doubt_detail(doubt_id):
    doubt = Doubt.query.get_or_404(doubt_id)
    doubt.views += 1
    db.session.commit()

    answers = Answer.query.filter_by(doubt_id=doubt.id).order_by(Answer.created_at.asc()).all()
    form = AnswerForm()

    user_vote = None
    if current_user.is_authenticated:
        vote = Vote.query.filter_by(user_id=current_user.id, doubt_id=doubt.id).first()
        if vote:
            user_vote = vote.vote_type

    if form.validate_on_submit():
        if current_user.role != 'faculty':
            abort(403)
        if doubt.author.faculty_id and doubt.author.faculty_id != current_user.id:
            flash('You can only answer doubts from your assigned students.', 'warning')
            return redirect(url_for('main.doubt_detail', doubt_id=doubt.id))

        answer = Answer(content=form.content.data, doubt_id=doubt.id, user_id=current_user.id)
        db.session.add(answer)
        current_user.points += 5
        db.session.commit()
        flash('Your answer has been posted!', 'success')
        return redirect(url_for('main.doubt_detail', doubt_id=doubt.id))

    return render_template('doubt_detail.html', doubt=doubt, answers=answers,
                           form=form, user_vote=user_vote)


@main.route('/doubt/<int:doubt_id>/vote', methods=['POST'])
@login_required
def vote_doubt(doubt_id):
    doubt = Doubt.query.get_or_404(doubt_id)
    vote_type = request.form.get('vote_type')
    if vote_type not in ('up', 'down'):
        abort(400)

    existing = Vote.query.filter_by(user_id=current_user.id, doubt_id=doubt_id).first()
    if existing:
        if existing.vote_type == vote_type:
            db.session.delete(existing)
            doubt.author.points -= (1 if vote_type == 'up' else -1)
        else:
            existing.vote_type = vote_type
            doubt.author.points += (2 if vote_type == 'up' else -2)
    else:
        vote = Vote(vote_type=vote_type, user_id=current_user.id, doubt_id=doubt_id)
        db.session.add(vote)
        doubt.author.points += (1 if vote_type == 'up' else -1)

    db.session.commit()
    return redirect(url_for('main.doubt_detail', doubt_id=doubt_id))


@main.route('/doubt/<int:doubt_id>/resolve', methods=['POST'])
@login_required
def resolve_doubt(doubt_id):
    doubt = Doubt.query.get_or_404(doubt_id)
    if doubt.user_id != current_user.id and current_user.role != 'faculty':
        abort(403)
    doubt.status = 'resolved' if doubt.status == 'open' else 'open'
    db.session.commit()
    flash(f'Doubt marked as {doubt.status}.', 'success')
    return redirect(url_for('main.doubt_detail', doubt_id=doubt_id))


# ─── NOTES ───────────────────────────────────────────────────────
@main.route('/upload_note', methods=['GET', 'POST'])
@login_required
def upload_note():
    if current_user.role != 'faculty':
        abort(403)
    form = NoteForm()
    if form.validate_on_submit():
        filename = None
        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        note = Note(title=form.title.data, content=form.content.data,
                    file=filename, faculty_id=current_user.id)
        db.session.add(note)
        current_user.points += 3
        db.session.commit()
        flash('Note uploaded successfully!', 'success')
        return redirect(url_for('main.notes'))
    return render_template('upload_note.html', form=form)


@main.route('/notes')
@login_required
def notes():
    all_notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=all_notes)


@main.route('/note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def note_detail(note_id):
    note = Note.query.get_or_404(note_id)
    comments = NoteComment.query.filter_by(note_id=note.id).order_by(NoteComment.created_at.asc()).all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = NoteComment(content=form.content.data, note_id=note.id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted!', 'success')
        return redirect(url_for('main.note_detail', note_id=note.id))
    return render_template('note_detail.html', note=note, comments=comments, form=form)


# ─── QUIZZES ─────────────────────────────────────────────────────
@main.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if current_user.role != 'faculty':
        abort(403)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        questions_text = request.form.getlist('questions[]')
        question_types = request.form.getlist('question_types[]')
        options_a = request.form.getlist('options_a[]')
        options_b = request.form.getlist('options_b[]')
        options_c = request.form.getlist('options_c[]')
        options_d = request.form.getlist('options_d[]')
        correct_answers = request.form.getlist('correct_answers[]')

        quiz = Quiz(title=title, description=description, faculty_id=current_user.id)
        db.session.add(quiz)
        db.session.commit()

        for i, q_text in enumerate(questions_text):
            if q_text.strip():
                q_type = question_types[i] if i < len(question_types) else 'text'
                question = Question(
                    text=q_text, question_type=q_type, quiz_id=quiz.id,
                    option_a=options_a[i] if i < len(options_a) and q_type == 'mcq' else None,
                    option_b=options_b[i] if i < len(options_b) and q_type == 'mcq' else None,
                    option_c=options_c[i] if i < len(options_c) and q_type == 'mcq' else None,
                    option_d=options_d[i] if i < len(options_d) and q_type == 'mcq' else None,
                    correct_answer=correct_answers[i] if i < len(correct_answers) else None,
                )
                db.session.add(question)

        current_user.points += 5
        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('main.view_quizzes'))
    return render_template('create_quiz.html')


@main.route('/quizzes')
@login_required
def view_quizzes():
    if current_user.role == 'student':
        if current_user.faculty_id:
            quizzes = Quiz.query.filter_by(faculty_id=current_user.faculty_id).order_by(Quiz.created_at.desc()).all()
        else:
            quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    elif current_user.role == 'faculty':
        quizzes = Quiz.query.filter_by(faculty_id=current_user.id).order_by(Quiz.created_at.desc()).all()
    else:
        quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    return render_template('quizzes.html', quizzes=quizzes)


@main.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    existing = Submission.query.filter_by(student_id=current_user.id, quiz_id=quiz_id).first()

    if request.method == 'POST':
        if existing:
            flash('You have already submitted this quiz.', 'warning')
            return redirect(url_for('main.view_quizzes'))

        submission = Submission(student_id=current_user.id, quiz_id=quiz_id)
        db.session.add(submission)
        db.session.commit()

        auto_score = 0
        for q in questions:
            ans = request.form.get(f'question_{q.id}')
            if ans:
                quiz_answer = QuizAnswer(submission_id=submission.id, question_id=q.id, answer_text=ans)
                if q.question_type == 'mcq' and q.correct_answer:
                    if ans.strip().lower() == q.correct_answer.strip().lower():
                        quiz_answer.marks = 1
                        auto_score += 1
                db.session.add(quiz_answer)

        submission.score = auto_score
        current_user.points += 3
        db.session.commit()
        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('main.my_results'))

    return render_template('take_quiz.html', quiz=quiz, questions=questions, existing=existing)


@main.route('/quiz/<int:quiz_id>/detail')
@login_required
def quiz_detail(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('quiz_detail.html', quiz=quiz, questions=questions)


@main.route('/quiz/<int:quiz_id>/submissions', methods=['GET', 'POST'])
@login_required
def view_submissions(quiz_id):
    if current_user.role != 'faculty':
        abort(403)
    quiz = Quiz.query.get_or_404(quiz_id)
    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('marks_'):
                answer_id = key.split('_')[1]
                answer = QuizAnswer.query.get(answer_id)
                if answer:
                    answer.marks = int(value) if value else 0
        for sub in submissions:
            sub.score = sum(a.marks for a in sub.answers)
        db.session.commit()
        flash('Marks saved successfully!', 'success')
    return render_template('submissions.html', quiz=quiz, submissions=submissions)


@main.route('/my_results')
@login_required
def my_results():
    if current_user.role != 'student':
        abort(403)
    submissions = Submission.query.filter_by(
        student_id=current_user.id
    ).order_by(Submission.submitted_at.desc()).all()
    return render_template('results.html', submissions=submissions)


# ─── PROFILE ─────────────────────────────────────────────────────
@main.route('/profile/<string:username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_doubts = Doubt.query.filter_by(user_id=user.id).order_by(Doubt.created_at.desc()).all()
    user_answers = Answer.query.filter_by(user_id=user.id).all()

    stats = {
        'doubts_posted': len(user_doubts),
        'answers_given': len(user_answers),
        'doubts_resolved': Doubt.query.filter_by(user_id=user.id, status='resolved').count(),
        'points': user.points,
        'rank': User.query.filter(User.points > user.points).count() + 1
    }

    badges = []
    if stats['doubts_posted'] >= 10:
        badges.append({'name': 'Curious Mind', 'icon': 'bi-lightbulb-fill', 'color': '#f59e0b'})
    if stats['doubts_posted'] >= 1:
        badges.append({'name': 'First Question', 'icon': 'bi-chat-dots-fill', 'color': '#06b6d4'})
    if stats['answers_given'] >= 10:
        badges.append({'name': 'Mentor', 'icon': 'bi-mortarboard-fill', 'color': '#10b981'})
    if stats['answers_given'] >= 1:
        badges.append({'name': 'Helper', 'icon': 'bi-hand-thumbs-up-fill', 'color': '#8b5cf6'})
    if stats['points'] >= 100:
        badges.append({'name': 'Century Club', 'icon': 'bi-trophy-fill', 'color': '#ef4444'})
    if stats['points'] >= 50:
        badges.append({'name': 'Rising Star', 'icon': 'bi-star-fill', 'color': '#eab308'})

    return render_template('profile.html', user=user, doubts=user_doubts,
                           stats=stats, badges=badges)


@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(username=form.username.data).first()
        if existing and existing.id != current_user.id:
            flash('Username already taken.', 'danger')
            return redirect(url_for('main.edit_profile'))
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        if form.avatar_color.data:
            current_user.avatar_color = form.avatar_color.data
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('main.profile', username=current_user.username))

    form.username.data = current_user.username
    form.bio.data = current_user.bio
    form.avatar_color.data = current_user.avatar_color
    return render_template('edit_profile.html', form=form)


# ─── LEADERBOARD ─────────────────────────────────────────────────
@main.route('/leaderboard')
def leaderboard():
    users = User.query.filter_by(role='student').order_by(User.points.desc()).limit(50).all()
    return render_template('leaderboard.html', users=users)


# ─── ADMIN ───────────────────────────────────────────────────────
@main.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.order_by(User.created_at.desc()).all()
    stats = {
        'total_users': User.query.count(),
        'total_students': User.query.filter_by(role='student').count(),
        'total_faculty': User.query.filter_by(role='faculty').count(),
        'total_doubts': Doubt.query.count(),
        'open_doubts': Doubt.query.filter_by(status='open').count(),
        'total_quizzes': Quiz.query.count(),
        'total_notes': Note.query.count()
    }
    return render_template('admin.html', users=users, stats=stats)


@main.route('/admin/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def change_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role in ('student', 'faculty'):
        user.role = new_role
        db.session.commit()
        flash(f'{user.username} is now a {new_role}.', 'success')
    return redirect(url_for('main.admin_panel'))


@main.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Admin status toggled for {user.username}.', 'success')
    return redirect(url_for('main.admin_panel'))


@main.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't delete yourself!", 'danger')
        return redirect(url_for('main.admin_panel'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted.', 'success')
    return redirect(url_for('main.admin_panel'))