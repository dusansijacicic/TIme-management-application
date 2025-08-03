from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.main import main
from app.models import User, Company, Project, TimeEntry
from app import db
from datetime import datetime, date
from sqlalchemy import func, text
from app import csrf

def format_date_for_display(date_obj):
    """Convert date to DD.MM.YYYY format for display"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
    return date_obj.strftime('%d.%m.%Y')

def format_date_for_input(date_obj):
    """Convert date to DD.MM.YYYY format for input fields"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
    return date_obj.strftime('%d.%m.%Y')

def parse_date_from_input(date_str):
    """Parse date from DD.MM.YYYY format to date object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%d.%m.%Y').date()
    except ValueError:
        # Fallback to YYYY-MM-DD format for backward compatibility
        return datetime.strptime(date_str, '%Y-%m-%d').date()

def format_date_for_api(date_obj):
    """Convert date to DD.MM.YYYY format for API responses"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
        except ValueError:
            # If it's already in DD.MM.YYYY format, try to parse it
            try:
                date_obj = datetime.strptime(date_obj, '%d.%m.%Y').date()
            except ValueError:
                return date_obj  # Return as is if can't parse
    return date_obj.strftime('%d.%m.%Y')

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_super_admin():
        # Super admin sees all companies and projects
        companies = Company.query.filter_by(is_active=True).all()
        projects = Project.query.filter_by(is_active=True).all()
        recent_entries = TimeEntry.query.order_by(TimeEntry.created_at.desc()).limit(10).all()
    elif current_user.is_company_admin():
        # Company admin sees their company's projects
        companies = Company.query.filter_by(is_active=True).all()  # Can see all companies
        projects = Project.query.filter_by(is_active=True).all()  # Can see all projects
        recent_entries = TimeEntry.query.order_by(TimeEntry.created_at.desc()).limit(10).all()
    else:
        # Regular user sees their assigned projects
        # Get projects where user is assigned
        result = db.session.execute(text("""
            SELECT DISTINCT c.* FROM companies c
            JOIN projects p ON c.id = p.company_id
            JOIN project_users pu ON p.id = pu.project_id
            WHERE pu.user_id = :user_id AND pu.is_active = 1
        """), {'user_id': current_user.id})
        companies = [Company(**row._mapping) for row in result.fetchall()]
        
        # Get user's assigned projects with company information
        result = db.session.execute(text("""
            SELECT p.*, c.name as company_name FROM projects p
            JOIN project_users pu ON p.id = pu.project_id
            JOIN companies c ON p.company_id = c.id
            WHERE pu.user_id = :user_id AND pu.is_active = 1
        """), {'user_id': current_user.id})
        
        # Create Project objects with company information
        projects = []
        for row in result.fetchall():
            project_data = dict(row._mapping)
            company_name = project_data.pop('company_name')
            project = Project(**project_data)
            # Add company name as a property
            project.company_name = company_name
            projects.append(project)
        
        recent_entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(
            TimeEntry.created_at.desc()
        ).limit(10).all()
    
    return render_template('main/dashboard.html', 
                         companies=companies, 
                         projects=projects, 
                         recent_entries=recent_entries)

@main.route('/time-entry', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def time_entry():
    if request.method == 'POST':
        data = request.get_json()
        
        try:
            entry = TimeEntry(
                user_id=current_user.id,
                project_id=data['project_id'],
                date=parse_date_from_input(data['date']),
                hours=float(data['hours']),
                description=data.get('description', '')
            )
            db.session.add(entry)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Vreme je uspešno uneto'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    # Get user's projects
    if current_user.is_super_admin() or current_user.is_company_admin():
        # Get all projects with company information for admin users
        result = db.session.execute(text("""
            SELECT p.*, c.name as company_name FROM projects p
            JOIN companies c ON p.company_id = c.id
            WHERE p.is_active = 1
        """))
        
        # Create Project objects with company information
        projects = []
        for row in result.fetchall():
            project_data = dict(row._mapping)
            company_name = project_data.pop('company_name')
            project = Project(**project_data)
            # Add company name as a property
            project.company_name = company_name
            projects.append(project)
    else:
        # Get user's assigned projects with company information
        result = db.session.execute(text("""
            SELECT p.*, c.name as company_name FROM projects p
            JOIN project_users pu ON p.id = pu.project_id
            JOIN companies c ON p.company_id = c.id
            WHERE pu.user_id = :user_id AND pu.is_active = 1
        """), {'user_id': current_user.id})
        
        # Create Project objects with company information
        projects = []
        for row in result.fetchall():
            project_data = dict(row._mapping)
            company_name = project_data.pop('company_name')
            project = Project(**project_data)
            # Add company name as a property
            project.company_name = company_name
            projects.append(project)
    
    return render_template('main/time_entry.html', projects=projects)

@main.route('/my-time-entries')
@login_required
def my_time_entries():
    # Get filter parameters
    project_id = request.args.get('project', type=int)
    company_id = request.args.get('company', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query
    query = TimeEntry.query.filter_by(user_id=current_user.id)
    
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    if date_from:
        query = query.filter(TimeEntry.date >= parse_date_from_input(date_from))
    
    if date_to:
        query = query.filter(TimeEntry.date <= parse_date_from_input(date_to))
    
    if current_user.is_super_admin() or current_user.is_company_admin():
        entries = query.order_by(TimeEntry.date.desc()).all()
    else:
        # For regular users, load entries with company information and apply filters
        sql_query = """
            SELECT te.*, p.name as project_name, c.name as company_name, c.id as company_id
            FROM time_entries te
            JOIN projects p ON te.project_id = p.id
            JOIN companies c ON p.company_id = c.id
            WHERE te.user_id = :user_id
        """
        params = {'user_id': current_user.id}
        
        # Add project filter
        if project_id:
            sql_query += " AND te.project_id = :project_id"
            params['project_id'] = project_id
        
        # Add company filter
        if company_id:
            sql_query += " AND c.id = :company_id"
            params['company_id'] = company_id
        
        # Add date filters - only if both dates are provided
        if date_from and date_to:
            sql_query += " AND te.date >= :date_from AND te.date <= :date_to"
            params['date_from'] = parse_date_from_input(date_from)
            params['date_to'] = parse_date_from_input(date_to)
        elif date_from:
            sql_query += " AND te.date >= :date_from"
            params['date_from'] = parse_date_from_input(date_from)
        elif date_to:
            sql_query += " AND te.date <= :date_to"
            params['date_to'] = parse_date_from_input(date_to)
        
        sql_query += " ORDER BY te.date DESC"
        
        result = db.session.execute(text(sql_query), params)
        
        # Create TimeEntry objects with company information
        entries = []
        for row in result.fetchall():
            entry_data = dict(row._mapping)
            project_name = entry_data.pop('project_name')
            company_name = entry_data.pop('company_name')
            company_id = entry_data.pop('company_id')
            
            # Create a simple object with the needed attributes
            entry = type('TimeEntry', (), {
                'id': entry_data['id'],
                'date': entry_data['date'],
                'hours': entry_data['hours'],
                'description': entry_data['description'],
                'project': type('Project', (), {
                    'name': project_name, 
                    'company_name': company_name,
                    'company_id': company_id
                })(),
                'user': current_user
            })()
            entries.append(entry)
    
    # Calculate statistics
    total_hours = sum(float(entry.hours) for entry in entries)
    avg_hours_per_day = total_hours / len(entries) if entries else 0
    
    # Get user's projects and companies for filter
    if current_user.is_super_admin() or current_user.is_company_admin():
        # Get all projects with company information for admin users
        result = db.session.execute(text("""
            SELECT p.*, c.name as company_name FROM projects p
            JOIN companies c ON p.company_id = c.id
            WHERE p.is_active = 1
        """))
        
        # Create Project objects with company information
        projects = []
        for row in result.fetchall():
            project_data = dict(row._mapping)
            company_name = project_data.pop('company_name')
            project = Project(**project_data)
            # Add company name as a property
            project.company_name = company_name
            projects.append(project)
        
        # Get all companies for admin users
        companies = Company.query.filter_by(is_active=True).all()
    else:
        # Get user's assigned projects with company information
        result = db.session.execute(text("""
            SELECT p.*, c.name as company_name FROM projects p
            JOIN project_users pu ON p.id = pu.project_id
            JOIN companies c ON p.company_id = c.id
            WHERE pu.user_id = :user_id AND pu.is_active = 1
        """), {'user_id': current_user.id})
        
        # Create Project objects with company information
        projects = []
        for row in result.fetchall():
            project_data = dict(row._mapping)
            company_name = project_data.pop('company_name')
            project = Project(**project_data)
            # Add company name as a property
            project.company_name = company_name
            projects.append(project)
        
        # Get user's companies (companies where user has assigned projects)
        result = db.session.execute(text("""
            SELECT DISTINCT c.* FROM companies c
            JOIN projects p ON c.id = p.company_id
            JOIN project_users pu ON p.id = pu.project_id
            WHERE pu.user_id = :user_id AND pu.is_active = 1 AND c.is_active = 1
        """), {'user_id': current_user.id})
        companies = [Company(**row._mapping) for row in result.fetchall()]
    
    return render_template('main/my_time_entries.html', 
                         entries=entries,
                         projects=projects,
                         companies=companies,
                         total_hours=total_hours,
                         avg_hours_per_day=avg_hours_per_day)

@main.route('/project-time-entries/<int:project_id>')
@login_required
def project_time_entries(project_id):
    """View all time entries for a specific project (for project admins)"""
    project = Project.query.get_or_404(project_id)
    
    # Check if user can view this project's entries
    if not (current_user.is_super_admin() or 
            current_user.is_company_admin() or 
            current_user.can_manage_project(project_id)):
        flash('Nemate dozvolu za pristup ovoj stranici', 'danger')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    entries = TimeEntry.query.filter_by(project_id=project_id).order_by(
        TimeEntry.date.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('main/project_time_entries.html', 
                         project=project, 
                         entries=entries)

@main.route('/api/time-entries')
@login_required
@csrf.exempt
def api_time_entries():
    project_id = request.args.get('project_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = TimeEntry.query
    
    if current_user.is_super_admin():
        pass  # Can see all entries
    elif current_user.is_company_admin():
        pass  # Can see all entries
    elif project_id and current_user.can_manage_project(project_id):
        # Project admin can see all entries for their project
        query = query.filter_by(project_id=project_id)
    else:
        # Regular user can only see their own entries
        query = query.filter_by(user_id=current_user.id)
    
    if project_id and not current_user.can_manage_project(project_id):
        query = query.filter_by(project_id=project_id)
    
    if start_date:
        query = query.filter(TimeEntry.date >= parse_date_from_input(start_date))
    
    if end_date:
        query = query.filter(TimeEntry.date <= parse_date_from_input(end_date))
    
    entries = query.order_by(TimeEntry.date.desc()).all()
    
    return jsonify([{
        'id': entry.id,
        'date': format_date_for_api(entry.date),
        'hours': float(entry.hours),
        'description': entry.description,
        'project_name': entry.project.name,
        'user_name': entry.user.get_full_name(),
        'created_at': entry.created_at.strftime('%d.%m.%Y %H:%M'),
        'updated_at': entry.updated_at.strftime('%d.%m.%Y %H:%M')
    } for entry in entries]) 

@main.route('/create-super-admin')
def create_super_admin():
    """Create super admin user for development - remove in production"""
    from app.models import User
    
    # Check if super admin already exists
    user = User.query.filter_by(username="lupa_admin_time").first()
    
    if not user:
        user = User(
            username="lupa_admin_time",
            email="lupa@admin.com",
            first_name="Lupa",
            last_name="Admin",
            role="super_admin",
            is_active=True
        )
        user.set_password("lupa2025!#")
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Super admin kreiran!", "username": "lupa_admin_time", "password": "lupa2025!#"})
    else:
        return jsonify({"message": "Super admin već postoji!", "username": "lupa_admin_time", "password": "lupa2025!#"})

@main.route('/api/time-entries/<int:entry_id>', methods=['GET'])
@login_required
@csrf.exempt
def api_get_time_entry(entry_id):
    """Get a specific time entry"""
    entry = TimeEntry.query.get_or_404(entry_id)
    
    # Check permissions
    if not (current_user.is_super_admin() or 
            current_user.is_company_admin() or 
            current_user.can_manage_project(entry.project_id) or
            entry.user_id == current_user.id):
        return jsonify({'success': False, 'message': 'Nemate dozvolu za pristup ovom unosu'})
    
    return jsonify({
        'success': True,
        'entry': {
            'id': entry.id,
            'date': format_date_for_api(entry.date),
            'hours': float(entry.hours),
            'description': entry.description,
            'project_id': entry.project_id,
            'user_id': entry.user_id
        }
    })

@main.route('/api/time-entries/<int:entry_id>', methods=['PUT'])
@login_required
@csrf.exempt
def api_update_time_entry(entry_id):
    """Update a specific time entry"""
    entry = TimeEntry.query.get_or_404(entry_id)
    
    # Check permissions
    if not (current_user.is_super_admin() or 
            current_user.is_company_admin() or 
            current_user.can_manage_project(entry.project_id) or
            entry.user_id == current_user.id):
        return jsonify({'success': False, 'message': 'Nemate dozvolu za izmenu ovog unosa'})
    
    data = request.get_json()
    
    try:
        entry.date = parse_date_from_input(data['date'])
        entry.hours = data['hours']
        entry.description = data.get('description', '')
        entry.project_id = data['project_id']
        entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Unos je uspešno ažuriran'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Greška pri ažuriranju: {str(e)}'})

@main.route('/api/time-entries/<int:entry_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def api_delete_time_entry(entry_id):
    """Delete a specific time entry"""
    entry = TimeEntry.query.get_or_404(entry_id)
    
    # Check permissions
    if not (current_user.is_super_admin() or 
            current_user.is_company_admin() or 
            current_user.can_manage_project(entry.project_id) or
            entry.user_id == current_user.id):
        return jsonify({'success': False, 'message': 'Nemate dozvolu za brisanje ovog unosa'})
    
    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Unos je uspešno obrisan'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Greška pri brisanju: {str(e)}'})

@main.route('/my-projects')
@login_required
def my_projects():
    """View user's assigned projects (read-only for regular users)"""
    # Only allow project admins, company admins, and super admins to access this page
    if not (current_user.is_super_admin() or current_user.is_company_admin() or current_user.is_project_admin()):
        flash('Nemate dozvolu za pristup ovoj stranici.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if current_user.is_super_admin() or current_user.is_company_admin():
        # Admin users see all projects
        result = db.session.execute(text("""
            SELECT p.*, c.name as company_name FROM projects p
            JOIN companies c ON p.company_id = c.id
            WHERE p.is_active = 1
        """))
    else:
        # Project admins see only their managed projects
        result = db.session.execute(text("""
            SELECT p.*, c.name as company_name FROM projects p
            JOIN companies c ON p.company_id = c.id
            WHERE p.project_admin_id = :user_id AND p.is_active = 1
        """), {'user_id': current_user.id})
    
    # Create Project objects with company information
    projects = []
    for row in result.fetchall():
        project_data = dict(row._mapping)
        company_name = project_data.pop('company_name')
        project = Project(**project_data)
        # Add company name as a property
        project.company_name = company_name
        projects.append(project)
    
    return render_template('main/my_projects.html', projects=projects)

@main.route('/api/user-projects')
@login_required
@csrf.exempt
def api_user_projects():
    """Get projects available to the current user"""
    if current_user.is_super_admin() or current_user.is_company_admin():
        # Get all projects with company information for admin users
        result = db.session.execute(text("""
            SELECT p.*, c.name as company_name FROM projects p
            JOIN companies c ON p.company_id = c.id
            WHERE p.is_active = 1
        """))
        
        # Create Project objects with company information
        projects = []
        for row in result.fetchall():
            project_data = dict(row._mapping)
            company_name = project_data.pop('company_name')
            project = Project(**project_data)
            # Add company name as a property
            project.company_name = company_name
            projects.append(project)
    else:
        # Get user's assigned projects with company information
        result = db.session.execute(text("""
            SELECT p.*, c.name as company_name FROM projects p
            JOIN project_users pu ON p.id = pu.project_id
            JOIN companies c ON p.company_id = c.id
            WHERE pu.user_id = :user_id AND pu.is_active = 1
        """), {'user_id': current_user.id})
        
        # Create Project objects with company information
        projects = []
        for row in result.fetchall():
            project_data = dict(row._mapping)
            company_name = project_data.pop('company_name')
            project = Project(**project_data)
            # Add company name as a property
            project.company_name = company_name
            projects.append(project)
    
    return jsonify([{
        'id': project.id,
        'name': project.name,
        'company_name': project.company_name if hasattr(project, 'company_name') else project.company.name
    } for project in projects]) 