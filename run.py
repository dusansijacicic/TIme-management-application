from app import create_app, db, migrate
from app.models import User, Company, Project, TimeEntry

app = create_app()
# git clone https://github.com/dusansijacicic/TIme-management-application.git
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Company': Company,
        'Project': Project,
        'TimeEntry': TimeEntry
    }

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database tables created.')

@app.cli.command()
def create_super_admin():
    """Create a super admin user."""
    username = input('Enter super admin username: ')
    email = input('Enter super admin email: ')
    password = input('Enter super admin password: ')
    first_name = input('Enter first name: ')
    last_name = input('Enter last name: ')
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        print('User already exists!')
        return
    
    # Create super admin
    super_admin = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role='super_admin'
    )
    super_admin.set_password(password)
    
    db.session.add(super_admin)
    db.session.commit()
    print('Super admin created successfully!')

@app.cli.command()
def migrate_db():
    """Run database migrations."""
    from flask_migrate import upgrade
    upgrade()
    print('Database migrations completed successfully!')

@app.cli.command()
def create_migration():
    """Create a new migration."""
    from flask_migrate import revision
    revision()
    print('New migration created!')

if __name__ == '__main__':
    app.run(debug=True) 