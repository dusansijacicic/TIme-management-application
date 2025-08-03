from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.admin import admin
from app.admin.forms import CompanyForm, ProjectForm, UserForm, ProjectUserForm
from app.models import User, Company, Project, TimeEntry, UserPreference
from app import db
from sqlalchemy import func, text
from datetime import datetime, timedelta
from functools import wraps
from app import csrf
import random

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def admin_decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super_admin():
            flash('Nemate dozvolu za pristup ovoj stranici', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return admin_decorated_function

def company_admin_required(f):
    """Decorator to check if user is company admin or super admin"""
    @wraps(f)
    def company_admin_decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_super_admin() or current_user.is_company_admin()):
            flash('Nemate dozvolu za pristup ovoj stranici', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return company_admin_decorated_function

def project_admin_required(f):
    """Decorator to check if user is project admin"""
    @wraps(f)
    def project_decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Nemate dozvolu za pristup ovoj stranici', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Super admin and company admin can access everything
        if current_user.is_super_admin() or current_user.is_company_admin():
            return f(*args, **kwargs)
        
        # For project-specific routes, check if user is project admin
        project_id = kwargs.get('project_id')
        if project_id and current_user.can_manage_project(project_id):
            return f(*args, **kwargs)
        
        flash('Nemate dozvolu za pristup ovoj stranici', 'danger')
        return redirect(url_for('main.dashboard'))
    return project_decorated_function

@admin.route('/')
@login_required
@admin_required
def index():
    stats = {
        'total_users': User.query.count(),
        'total_companies': Company.query.count(),
        'total_projects': Project.query.count(),
        'total_hours': db.session.query(func.sum(TimeEntry.hours)).scalar() or 0
    }
    return render_template('admin/index.html', stats=stats)

@admin.route('/companies')
@login_required
@admin_required
def companies():
    companies = Company.query.all()
    return render_template('admin/companies.html', companies=companies)

@admin.route('/companies/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_company():
    form = CompanyForm()
    if form.validate_on_submit():
        company = Company(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            website=form.website.data,
            address=form.address.data,
            description=form.description.data
        )
        db.session.add(company)
        db.session.commit()
        flash('Kompanija je uspešno kreirana', 'success')
        return redirect(url_for('admin.companies'))
    
    return render_template('admin/company_form.html', form=form, title='Nova kompanija')

@admin.route('/companies/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_company(company_id):
    company = Company.query.get_or_404(company_id)
    form = CompanyForm(obj=company)
    
    if form.validate_on_submit():
        company.name = form.name.data
        company.email = form.email.data
        company.phone = form.phone.data
        company.website = form.website.data
        company.address = form.address.data
        company.description = form.description.data
        db.session.commit()
        flash('Kompanija je uspešno ažurirana', 'success')
        return redirect(url_for('admin.companies'))
    
    return render_template('admin/company_form.html', form=form, title='Izmeni kompaniju')

@admin.route('/projects')
@login_required
@admin_required
def projects():
    projects = Project.query.all()
    return render_template('admin/projects.html', projects=projects)

@admin.route('/projects/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_project():
    form = ProjectForm()
    form.company_id.choices = [(c.id, c.name) for c in Company.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            company_id=form.company_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            status=form.status.data
        )
        db.session.add(project)
        db.session.commit()
        flash('Projekat je uspešno kreiran', 'success')
        return redirect(url_for('admin.projects'))
    
    return render_template('admin/project_form.html', form=form, title='Novi projekat')

@admin.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    form.company_id.choices = [(c.id, c.name) for c in Company.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        project.company_id = form.company_id.data
        project.start_date = form.start_date.data
        project.end_date = form.end_date.data
        project.budget = form.budget.data
        project.status = form.status.data
        db.session.commit()
        flash('Projekat je uspešno ažuriran', 'success')
        return redirect(url_for('admin.projects'))
    
    return render_template('admin/project_form.html', form=form, title='Izmeni projekat')

@admin.route('/projects/<int:project_id>/users')
@login_required
@project_admin_required
def project_users(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Get users assigned to this project
    result = db.session.execute(text("""
        SELECT u.*, pu.role as project_role, pu.assigned_at
        FROM users u
        JOIN project_users pu ON u.id = pu.user_id
        WHERE pu.project_id = :project_id AND pu.is_active = 1
        ORDER BY u.first_name, u.last_name
    """), {'project_id': project_id})
    
    project_users = result.fetchall()
    
    # Get all users for assignment form
    all_users = User.query.filter_by(is_active=True).all()
    
    form = ProjectUserForm()
    form.user_id.choices = [(u.id, f"{u.first_name} {u.last_name} ({u.username})") for u in all_users]
    
    return render_template('admin/project_users.html', 
                         project=project, 
                         project_users=project_users, 
                         form=form)

@admin.route('/projects/<int:project_id>/users/assign', methods=['POST'])
@login_required
@project_admin_required
def assign_user_to_project_form(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectUserForm()
    form.user_id.choices = [(u.id, f"{u.first_name} {u.last_name}") for u in User.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        user_id = form.user_id.data
        role = form.role.data
        
        # Check if user is already assigned to this project
        existing = db.session.execute(text("""
            SELECT id FROM project_users 
            WHERE user_id = :user_id AND project_id = :project_id AND is_active = 1
        """), {'user_id': user_id, 'project_id': project_id}).fetchone()
        
        if existing:
            flash('Korisnik je već dodeljen ovom projektu', 'warning')
        else:
            # Assign user to project
            db.session.execute(text("""
                INSERT INTO project_users (project_id, user_id, role, assigned_at, is_active)
                VALUES (:project_id, :user_id, :role, NOW(), 1)
            """), {
                'project_id': project_id,
                'user_id': user_id,
                'role': role
            })
            db.session.commit()
            flash('Korisnik je uspešno dodeljen projektu', 'success')
    
    return redirect(url_for('admin.project_users', project_id=project_id))

@admin.route('/projects/<int:project_id>/users/<int:user_id>/remove', methods=['POST'])
@login_required
@project_admin_required
def remove_user_from_project(project_id, user_id):
    # Soft delete - mark as inactive
    db.session.execute(text("""
        UPDATE project_users 
        SET is_active = 0 
        WHERE project_id = :project_id AND user_id = :user_id
    """), {'project_id': project_id, 'user_id': user_id})
    db.session.commit()
    
    flash('Korisnik je uklonjen sa projekta', 'success')
    return redirect(url_for('admin.project_users', project_id=project_id))

@admin.route('/users')
@login_required
@company_admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/users/new', methods=['GET', 'POST'])
@login_required
@company_admin_required
def new_user():
    form = UserForm()
    
    # Populate projects choices
    form.projects.choices = [(p.id, f"{p.name} ({p.company.name})") for p in Project.query.filter_by(is_active=True).all()]
    
    # Limit role choices for non-super admins
    if not current_user.is_super_admin():
        form.role.choices = [
            ('user', 'Korisnik'),
            ('company_admin', 'Admin kompanije')
        ]
    
    if form.validate_on_submit():
        # Only super admin can create super admin users
        role = form.role.data
        if not current_user.is_super_admin() and role == 'super_admin':
            flash('Nemate dozvolu za kreiranje super admin korisnika', 'danger')
            return redirect(url_for('admin.users'))
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=role,
            hourly_rate=form.hourly_rate.data
        )
        password = form.password.data if form.password.data else 'password123'
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Assign projects to user
        selected_projects = request.form.getlist('projects')
        for project_id in selected_projects:
            try:
                project_id = int(project_id)
                db.session.execute(text("""
                    INSERT INTO project_users (project_id, user_id, role, assigned_at, is_active)
                    VALUES (:project_id, :user_id, 'user', NOW(), 1)
                """), {
                    'project_id': project_id,
                    'user_id': user.id
                })
            except ValueError:
                # Skip invalid project IDs
                continue
        db.session.commit()
        
        flash('Korisnik je uspešno kreiran', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, current_project_ids=[], title='Novi korisnik')

@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@company_admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    # Populate projects choices
    form.projects.choices = [(p.id, f"{p.name} ({p.company.name})") for p in Project.query.filter_by(is_active=True).all()]
    
    # Limit role choices for non-super admins
    if not current_user.is_super_admin():
        form.role.choices = [
            ('user', 'Korisnik'),
            ('company_admin', 'Admin kompanije')
        ]
    
    # Get current user projects
    current_projects = db.session.execute(text("""
        SELECT project_id FROM project_users 
        WHERE user_id = :user_id AND is_active = 1
    """), {'user_id': user_id}).fetchall()
    current_project_ids = [row[0] for row in current_projects] if current_projects else []
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        
        # Only super admin can change roles
        if current_user.is_super_admin():
            user.role = form.role.data
        else:
            # Company admin can only change to user or company_admin, not super_admin
            if form.role.data == 'super_admin':
                flash('Nemate dozvolu za dodeljivanje super admin uloge', 'danger')
                return redirect(url_for('admin.users'))
            user.role = form.role.data
        
        # Only super admin and company admin can change hourly rate
        if current_user.is_super_admin() or current_user.is_company_admin():
            user.hourly_rate = form.hourly_rate.data
        
        # Update password if provided
        if form.password.data:
            user.set_password(form.password.data)
        
        # Update project assignments
        # First, deactivate all current assignments
        db.session.execute(text("""
            UPDATE project_users SET is_active = 0 
            WHERE user_id = :user_id
        """), {'user_id': user_id})
        
        # Get selected projects from form data (checkbox values)
        selected_projects = request.form.getlist('projects')
        for project_id in selected_projects:
            try:
                project_id = int(project_id)
                # Check if assignment already exists
                existing = db.session.execute(text("""
                    SELECT id FROM project_users 
                    WHERE user_id = :user_id AND project_id = :project_id
                """), {'user_id': user_id, 'project_id': project_id}).fetchone()
                
                if existing:
                    # Reactivate existing assignment
                    db.session.execute(text("""
                        UPDATE project_users SET is_active = 1 
                        WHERE user_id = :user_id AND project_id = :project_id
                    """), {'user_id': user_id, 'project_id': project_id})
                else:
                    # Create new assignment
                    db.session.execute(text("""
                        INSERT INTO project_users (project_id, user_id, role, assigned_at, is_active)
                        VALUES (:project_id, :user_id, 'user', NOW(), 1)
                    """), {
                        'project_id': project_id,
                        'user_id': user_id
                    })
            except ValueError:
                # Skip invalid project IDs
                continue
        
        db.session.commit()
        flash('Korisnik je uspešno ažuriran', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, user=user, current_project_ids=current_project_ids, title='Izmeni korisnika')

@admin.route('/api/assign-user-to-project', methods=['POST'])
@login_required
@company_admin_required
@csrf.exempt
def assign_user_to_project_api():
    data = request.get_json()
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    role = data.get('role', 'user')
    
    user = User.query.get(user_id)
    project = Project.query.get(project_id)
    
    if user and project:
        # Check if already assigned
        existing = db.session.execute(text("""
            SELECT id FROM project_users 
            WHERE user_id = :user_id AND project_id = :project_id AND is_active = 1
        """), {'user_id': user_id, 'project_id': project_id}).fetchone()
        
        if existing:
            return jsonify({'success': False, 'message': 'Korisnik je već dodeljen ovom projektu'})
        
        # Assign user to project
        db.session.execute(text("""
            INSERT INTO project_users (project_id, user_id, role, assigned_at, is_active)
            VALUES (:project_id, :user_id, :role, NOW(), 1)
        """), {
            'project_id': project_id,
            'user_id': user_id,
            'role': role
        })
        db.session.commit()
        return jsonify({'success': True, 'message': 'Korisnik je dodeljen projektu'})
    
    return jsonify({'success': False, 'message': 'Greška pri dodeljivanju'})

@admin.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@company_admin_required
@csrf.exempt
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    is_active = data.get('is_active', False)
    
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Ne možete da deaktivirate svoj nalog'})
    
    user.is_active = is_active
    db.session.commit()
    
    action = 'aktiviran' if is_active else 'deaktiviran'
    return jsonify({'success': True, 'message': f'Korisnik je {action}'})

@admin.route('/companies/<int:company_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def toggle_company_status(company_id):
    company = Company.query.get_or_404(company_id)
    data = request.get_json()
    is_active = data.get('is_active', False)
    
    company.is_active = is_active
    db.session.commit()
    
    action = 'aktiviran' if is_active else 'deaktiviran'
    return jsonify({'success': True, 'message': f'Kompanija je {action}'}) 

@admin.route('/clear-database', methods=['GET', 'POST'])
@login_required
@admin_required
def clear_database():
    """Clear all data from database except super admin users"""
    
    if request.method == 'POST':
        # Get confirmation from form
        confirm = request.form.get('confirm')
        
        if confirm == 'DELETE_ALL_DATA':
            try:
                # Get count of super admin users to preserve
                super_admin_count = User.query.filter_by(role='super_admin').count()
                
                # Delete all time entries
                time_entries_deleted = TimeEntry.query.delete()
                
                # Delete all project-user associations
                project_users_deleted = db.session.execute(text("DELETE FROM project_users")).rowcount
                
                # Delete all projects
                projects_deleted = Project.query.delete()
                
                # Delete all companies
                companies_deleted = Company.query.delete()
                
                # Delete user preferences for non-super-admin users only
                non_super_admin_user_ids = [user.id for user in User.query.filter(User.role != 'super_admin').all()]
                user_preferences_deleted = UserPreference.query.filter(UserPreference.user_id.in_(non_super_admin_user_ids)).delete(synchronize_session=False)
                
                # Delete all non-super-admin users
                regular_users_deleted = User.query.filter(User.role != 'super_admin').delete()
                
                # Commit all changes
                db.session.commit()
                
                flash(f'Baza podataka je uspešno očišćena! Obrisano: {time_entries_deleted} time entries, {project_users_deleted} project associations, {projects_deleted} projects, {companies_deleted} companies, {user_preferences_deleted} user preferences (za obične korisnike), {regular_users_deleted} regular users. Zadržano: {super_admin_count} super admin korisnika sa njihovim preferencijama.', 'success')
                
                return redirect(url_for('admin.index'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Greška pri brisanju podataka: {str(e)}', 'danger')
                return redirect(url_for('admin.clear_database'))
        else:
            flash('Potvrda nije ispravna. Molimo unesite "DELETE_ALL_DATA" za potvrdu.', 'danger')
    
    # GET request - show confirmation page
    stats = {
        'total_users': User.query.count(),
        'super_admin_users': User.query.filter_by(role='super_admin').count(),
        'regular_users': User.query.filter(User.role != 'super_admin').count(),
        'total_companies': Company.query.count(),
        'total_projects': Project.query.count(),
        'total_time_entries': TimeEntry.query.count(),
        'total_project_users': db.session.execute(text("SELECT COUNT(*) FROM project_users")).scalar(),
        'total_user_preferences': UserPreference.query.count(),
        'super_admin_preferences': UserPreference.query.join(User).filter(User.role == 'super_admin').count(),
        'regular_user_preferences': UserPreference.query.join(User).filter(User.role != 'super_admin').count()
    }
    
    return render_template('admin/clear_database.html', stats=stats) 

@admin.route('/generate-mockup-data', methods=['GET', 'POST'])
@login_required
@admin_required
def generate_mockup_data():
    """Generate mockup data for a specific user"""
    
    if request.method == 'POST':
        user_id = request.form.get('user_id', type=int)
        
        if not user_id:
            flash('Molimo odaberite korisnika', 'danger')
            return redirect(url_for('admin.generate_mockup_data'))
        
        user = User.query.get(user_id)
        if not user:
            flash('Korisnik nije pronađen', 'danger')
            return redirect(url_for('admin.generate_mockup_data'))
        
        try:
            # Create mockup companies
            companies = []
            company_names = ['Tech Solutions Inc.', 'Digital Innovations Ltd.', 'Creative Agency Pro', 'Software House Plus']
            
            for i, name in enumerate(company_names):
                company = Company(
                    name=name,
                    email=f'info@{name.lower().replace(" ", "").replace(".", "").replace(",", "")}.com',
                    phone=f'+381 11 123 45{6+i}',
                    website=f'www.{name.lower().replace(" ", "").replace(".", "").replace(",", "")}.com',
                    address=f'Adresa {i+1}, Beograd, Srbija',
                    description=f'Opis kompanije {name}'
                )
                db.session.add(company)
                companies.append(company)
            
            db.session.commit()
            
            # Create mockup projects
            projects = []
            project_data = [
                ('Web Development', 'Razvoj web aplikacije', 5000, 'active'),
                ('Mobile App', 'Razvoj mobilne aplikacije', 8000, 'active'),
                ('UI/UX Design', 'Dizajn korisničkog interfejsa', 3000, 'completed'),
                ('Database Design', 'Dizajn baze podataka', 2500, 'active'),
                ('API Development', 'Razvoj API-ja', 4000, 'on_hold'),
                ('Testing', 'Testiranje aplikacije', 2000, 'active'),
                ('Maintenance', 'Održavanje sistema', 1500, 'active'),
                ('Consulting', 'Konsultantske usluge', 6000, 'completed')
            ]
            
            for i, (name, desc, budget, status) in enumerate(project_data):
                company = companies[i % len(companies)]
                project = Project(
                    name=name,
                    description=desc,
                    company_id=company.id,
                    start_date=datetime.now().date() - timedelta(days=30 + i*5),
                    end_date=datetime.now().date() + timedelta(days=60 + i*10),
                    budget=budget,
                    status=status
                )
                db.session.add(project)
                projects.append(project)
            
            db.session.commit()
            
            # Assign user to projects
            for i, project in enumerate(projects):
                role = 'project_admin' if i % 3 == 0 else 'user'
                db.session.execute(text("""
                    INSERT INTO project_users (project_id, user_id, role, assigned_at, is_active)
                    VALUES (:project_id, :user_id, :role, NOW(), 1)
                """), {
                    'project_id': project.id,
                    'user_id': user_id,
                    'role': role
                })
            
            # Create mockup time entries for the last 30 days
            time_entries = []
            for i in range(30):
                date = datetime.now().date() - timedelta(days=29-i)
                
                # Skip weekends (Saturday=5, Sunday=6)
                if date.weekday() >= 5:
                    continue
                
                # Create 1-3 time entries per day
                num_entries = min(3, len(projects))
                for j in range(num_entries):
                    project = projects[j % len(projects)]
                    hours = round(random.uniform(2.0, 8.0), 2)
                    
                    time_entry = TimeEntry(
                        user_id=user_id,
                        project_id=project.id,
                        date=date,
                        hours=hours,
                        description=f'Mockup rad na projektu {project.name} - {["Analiza", "Razvoj", "Testiranje", "Dokumentacija"][j % 4]}'
                    )
                    db.session.add(time_entry)
                    time_entries.append(time_entry)
            
            db.session.commit()
            
            flash(f'Uspešno generisani mockup podaci za korisnika {user.get_full_name()}: {len(companies)} kompanija, {len(projects)} projekata, {len(time_entries)} time entries', 'success')
            return redirect(url_for('admin.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Greška pri generisanju mockup podataka: {str(e)}', 'danger')
            return redirect(url_for('admin.generate_mockup_data'))
    
    # GET request - show form
    users = User.query.filter(User.role != 'super_admin').all()
    return render_template('admin/generate_mockup_data.html', users=users) 

@admin.route('/generate-mockup-data-user-21')
@login_required
@admin_required
def generate_mockup_data_user_21():
    """Generate mockup data specifically for user ID 21"""
    
    user_id = 21
    user = User.query.get(user_id)
    
    if not user:
        flash('Korisnik sa ID 21 nije pronađen', 'danger')
        return redirect(url_for('admin.index'))
    
    try:
        # Create mockup companies
        companies = []
        company_names = ['Tech Solutions Inc.', 'Digital Innovations Ltd.', 'Creative Agency Pro', 'Software House Plus']
        
        for i, name in enumerate(company_names):
            company = Company(
                name=name,
                email=f'info@{name.lower().replace(" ", "").replace(".", "").replace(",", "")}.com',
                phone=f'+381 11 123 45{6+i}',
                website=f'www.{name.lower().replace(" ", "").replace(".", "").replace(",", "")}.com',
                address=f'Adresa {i+1}, Beograd, Srbija',
                description=f'Opis kompanije {name}'
            )
            db.session.add(company)
            companies.append(company)
        
        db.session.commit()
        
        # Create mockup projects
        projects = []
        project_data = [
            ('Web Development', 'Razvoj web aplikacije', 5000, 'active'),
            ('Mobile App', 'Razvoj mobilne aplikacije', 8000, 'active'),
            ('UI/UX Design', 'Dizajn korisničkog interfejsa', 3000, 'completed'),
            ('Database Design', 'Dizajn baze podataka', 2500, 'active'),
            ('API Development', 'Razvoj API-ja', 4000, 'on_hold'),
            ('Testing', 'Testiranje aplikacije', 2000, 'active'),
            ('Maintenance', 'Održavanje sistema', 1500, 'active'),
            ('Consulting', 'Konsultantske usluge', 6000, 'completed')
        ]
        
        for i, (name, desc, budget, status) in enumerate(project_data):
            company = companies[i % len(companies)]
            project = Project(
                name=name,
                description=desc,
                company_id=company.id,
                start_date=datetime.now().date() - timedelta(days=30 + i*5),
                end_date=datetime.now().date() + timedelta(days=60 + i*10),
                budget=budget,
                status=status
            )
            db.session.add(project)
            projects.append(project)
        
        db.session.commit()
        
        # Assign user to projects
        for i, project in enumerate(projects):
            role = 'project_admin' if i % 3 == 0 else 'user'
            db.session.execute(text("""
                INSERT INTO project_users (project_id, user_id, role, assigned_at, is_active)
                VALUES (:project_id, :user_id, :role, NOW(), 1)
            """), {
                'project_id': project.id,
                'user_id': user_id,
                'role': role
            })
        
        # Create mockup time entries for the last 30 days
        time_entries = []
        for i in range(30):
            date = datetime.now().date() - timedelta(days=29-i)
            
            # Skip weekends (Saturday=5, Sunday=6)
            if date.weekday() >= 5:
                continue
            
            # Create 1-3 time entries per day
            num_entries = min(3, len(projects))
            for j in range(num_entries):
                project = projects[j % len(projects)]
                hours = round(random.uniform(2.0, 8.0), 2)
                
                time_entry = TimeEntry(
                    user_id=user_id,
                    project_id=project.id,
                    date=date,
                    hours=hours,
                    description=f'Mockup rad na projektu {project.name} - {["Analiza", "Razvoj", "Testiranje", "Dokumentacija"][j % 4]}'
                )
                db.session.add(time_entry)
                time_entries.append(time_entry)
        
        db.session.commit()
        
        flash(f'Uspešno generisani mockup podaci za korisnika {user.get_full_name()} (ID: 21): {len(companies)} kompanija, {len(projects)} projekata, {len(time_entries)} time entries', 'success')
        return redirect(url_for('admin.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Greška pri generisanju mockup podataka: {str(e)}', 'danger')
        return redirect(url_for('admin.index')) 

@admin.route('/mockup-user-21')
@login_required
@admin_required
def mockup_user_21():
    """Quick route to generate mockup data for user ID 21"""
    return redirect(url_for('admin.generate_mockup_data_user_21')) 