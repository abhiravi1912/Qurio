# Qurio - Educational Collaboration Platform

A comprehensive web-based learning management system that connects students, faculty, and administrators in a collaborative educational environment. Qurio enables students to ask doubts, get answers from peers and faculty, access study materials, and take quizzes—all in one unified platform.

## Features

### 🎓 Core Features
- **Doubt Management**: Post and resolve academic doubts with community answers
- **Q&A Forum**: Structured doubt-and-answer system with voting and acceptance
- **Study Materials**: Faculty can upload and share notes, documents, and multimedia
- **Quiz System**: Faculty-created quizzes for assessment and learning
- **User Roles**: Support for students, faculty, and admin with role-based access

### 👥 User Management
- **Registration & Authentication**: Secure user registration with different roles
- **User Profiles**: Customizable profiles with bio and avatar colors
- **Points System**: Gamification through reputation points
- **Faculty-Student Relationships**: Students can be assigned to specific faculty members

### 🗳️ Engagement Features
- **Voting System**: Upvote/downvote on doubts for community curation
- **Answer Acceptance**: Mark best answers as accepted
- **Comments**: Discuss and clarify on study notes
- **View Tracking**: Track how many times a doubt has been viewed

### 📚 Study Resources
- **Notes Management**: Faculty can upload study notes with file attachments
- **File Uploads**: Support for PDF, images, videos, and document formats
- **Quiz Submissions**: Student quiz attempt tracking with scoring

## Tech Stack

### Backend
- **Framework**: Flask 3.1.2
- **Database**: SQLAlchemy 2.0.46 with SQLite (default)
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Forms**: Flask-WTF with WTForms

### Frontend
- **Bootstrap 5.3.3**: Responsive UI framework
- **Bootstrap Icons**: Icon library
- **Inter Font**: Modern typography

### Security
- **CSRF Protection**: Flask-WTF CSRF protection
- **Password Hashing**: Bcrypt for secure password storage
- **File Upload Validation**: File type and size restrictions

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/abhiravi1912/Qurio.git
   cd Qurio
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download frontend assets** (optional, if not already present)
   ```bash
   python download_assets.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

   The application will start at `http://localhost:5000`

## Configuration

### Environment Variables
Configure the following environment variables in your system or create a `.env` file:

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///site.db
```

### Configuration File (`config.py`)
- **SECRET_KEY**: Flask secret key (defaults to 'qurio-dev-secret-change-in-production')
- **SQLALCHEMY_DATABASE_URI**: Database connection string (defaults to SQLite)
- **UPLOAD_FOLDER**: Directory for file uploads (default: `static/uploads`)
- **MAX_CONTENT_LENGTH**: Maximum upload file size (default: 16MB)

## Project Structure

```
qurio/
├── app/
│   ├── __init__.py          # Flask app factory and initialization
│   ├── models.py            # SQLAlchemy database models
│   ├── forms.py             # WTForms form definitions
│   └── routes.py            # Application routes and views
├── static/
│   ├── vendor/              # Third-party libraries (Bootstrap, Icons, Fonts)
│   ├── css/                 # Custom stylesheets
│   ├── js/                  # JavaScript files
│   └── uploads/             # User uploaded files
├── templates/               # HTML templates
├── instance/                # Instance-specific files (database, etc.)
├── app.py                   # Application entry point
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
└── download_assets.py       # Script to download frontend assets
```

## Database Models

### User
- User authentication and profile management
- Roles: student, faculty, admin
- Points-based reputation system
- Faculty-student relationships

### Doubt
- Academic question posts
- Categories: Math, Physics, Computer Science, Chemistry, Biology, Other
- Status tracking: open/closed
- Voting and view counting

### Answer
- Responses to doubts
- Answer acceptance tracking
- User attribution

### Vote
- Upvote/downvote system for doubts
- Unique constraint per user-doubt pair

### Note
- Study materials shared by faculty
- File attachment support
- Comment threads

### Quiz & Questions
- Quiz creation and management by faculty
- Multiple question types
- Student submissions with scoring

## Security Considerations

- **CSRF Protection**: All forms are protected with CSRF tokens
- **Password Security**: Passwords are hashed using bcrypt
- **File Upload Safety**: Restricted file types and 16MB size limit
- **Database**: SQL injection protection through SQLAlchemy ORM
- **Authentication**: Session-based authentication with Flask-Login

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, please open an issue on the GitHub repository.

---

**GitHub**: [abhiravi1912/Qurio](https://github.com/abhiravi1912/Qurio)
