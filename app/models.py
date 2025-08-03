from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

# Association table for many-to-many relationship between projects and users
project_users = db.Table('project_users',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), nullable=False),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('role', db.Enum('user', 'project_admin'), default='user'),  # User role within the project
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow),
    db.Column('is_active', db.Boolean, default=True)
)

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    primary_color = db.Column(db.String(20), default='emerald')  # emerald, purple, chocolate, blue, red, orange, teal, pink, custom
    secondary_color = db.Column(db.String(20), default='white')  # white, emerald, purple, chocolate, blue, red, orange, teal, pink, custom
    text_color = db.Column(db.String(20), default='primary')  # primary, secondary, light, white, dark, custom
    custom_primary_color = db.Column(db.String(7), default='#10b981')  # Hex color for custom primary
    custom_secondary_color = db.Column(db.String(7), default='#ffffff')  # Hex color for custom secondary
    custom_text_color = db.Column(db.String(7), default='#1f2937')  # Hex color for custom text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='preference', uselist=False)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.Enum('super_admin', 'company_admin', 'user'), default='user')
    hourly_rate = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    time_entries = db.relationship('TimeEntry', backref='user', lazy='dynamic')
    projects = db.relationship('Project', secondary=project_users, backref='users')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    def is_company_admin(self):
        return self.role == 'company_admin'
    
    def is_project_admin(self, project_id=None):
        """Check if user is project admin for specific project or any project"""
        if project_id:
            # Check specific project
            from sqlalchemy import text
            result = db.session.execute(text("""
                SELECT role FROM project_users 
                WHERE user_id = :user_id AND project_id = :project_id AND is_active = 1
            """), {'user_id': self.id, 'project_id': project_id})
            row = result.fetchone()
            return row and row[0] == 'project_admin'
        else:
            # Check if user is project admin for any project
            from sqlalchemy import text
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM project_users 
                WHERE user_id = :user_id AND role = 'project_admin' AND is_active = 1
            """), {'user_id': self.id})
            return result.fetchone()[0] > 0
    
    def can_manage_project(self, project_id):
        """Check if user can manage a specific project"""
        return (self.is_super_admin() or 
                self.is_company_admin() or 
                self.is_project_admin(project_id))
    
    def get_projects_as_admin(self):
        """Get all projects where user is project admin"""
        from sqlalchemy import text
        result = db.session.execute(text("""
            SELECT p.* FROM projects p
            JOIN project_users pu ON p.id = pu.project_id
            WHERE pu.user_id = :user_id AND pu.role = 'project_admin' AND pu.is_active = 1
        """), {'user_id': self.id})
        return result.fetchall()
    
    def get_color_preferences(self):
        """Get user's color preferences, create default if none exist"""
        # Always query directly to avoid relationship issues
        preferences = UserPreference.query.filter_by(user_id=self.id).first()
        if not preferences:
            # Create default preferences
            preferences = UserPreference(user_id=self.id)
            db.session.add(preferences)
            db.session.commit()
        return preferences

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    address = db.Column(db.Text)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    projects = db.relationship('Project', backref='company', lazy='dynamic')

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Numeric(15, 2))
    status = db.Column(db.Enum('active', 'completed', 'on_hold'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    time_entries = db.relationship('TimeEntry', backref='project', lazy='dynamic')

class TimeEntry(db.Model):
    __tablename__ = 'time_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Numeric(5, 2), nullable=False)  # Max 999.99 hours
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 