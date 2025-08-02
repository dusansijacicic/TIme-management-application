# 🕐 Dixi Time Management System

**Modern time tracking application** built with Flask, SQLAlchemy, and Bootstrap. Perfect for managing project time entries across multiple companies and users with flexible user-project assignments, comprehensive reporting, and customizable user preferences.

## 🎯 **Overview**

This is a sophisticated time management system designed for companies that work with multiple clients and projects. It allows users to log time entries for projects across different companies, with role-based access control and comprehensive reporting capabilities.

### **Key Highlights:**
- ✅ **Multi-company support** - Work with multiple clients simultaneously
- ✅ **Flexible user assignments** - Users can work on projects from different companies
- ✅ **Role-based access control** - Super Admin, Company Admin, Project Admin, Regular User
- ✅ **Comprehensive reporting** - Detailed reports with Excel export functionality
- ✅ **Customizable UI** - User-defined color themes and preferences
- ✅ **Real-time updates** - AJAX-powered dynamic content
- ✅ **Mobile-responsive** - Works perfectly on all devices

---

## 🚀 **Features & Functionality**

### **👥 User Management System**

#### **User Roles & Permissions:**

**🔴 Super Admin**
- Full system access and control
- Can manage all companies, projects, and users
- Access to all reports and statistics
- Can assign users to projects with specific roles
- Can edit user roles and hourly rates
- Access to admin panel and all administrative functions
- Can clear database (preserving super admin data)

**🟡 Company Admin**
- Can manage all companies and projects
- Can view all reports and statistics
- Can manage users across all companies
- Can assign users to projects
- Cannot edit super admin users
- Cannot change user roles to super admin

**🟢 Project Admin**
- Can manage users assigned to their specific projects
- Can view all time entries for their projects
- Can add/remove users from their projects
- Access to project-specific reports
- Cannot manage other projects

**🔵 Regular User**
- Can only log time entries for assigned projects
- Can view personal time reports and dashboard
- Cannot change other users or their own hourly rate
- Cannot assign themselves to projects
- Cannot access admin panel
- Can customize their UI colors and preferences

#### **User-Project Relationship:**
- Users can work on projects from different companies simultaneously
- Each user-project assignment has a role (user or project_admin)
- Soft deletion system - users can be "deactivated" from projects without losing data
- Project admins can manage their specific projects independently

### **🏢 Company & Project Management**

#### **Company Features:**
- Create and manage multiple companies
- Company-specific project management
- Company status tracking (active/inactive)
- Company contact information and details

#### **Project Features:**
- Create projects within companies
- Project status tracking (Active, Completed, On Hold)
- Project budget and description management
- User assignment with specific roles
- Project-specific time tracking

### **⏰ Time Tracking System**

#### **Time Entry Features:**
- **Quick entry form** with project selection
- **Backward time logging** - log time for past dates
- **Real-time validation** and error handling
- **Project format display** - shows "PROJECT_NAME (COMPANY_NAME)"
- **Description field** for detailed time entry notes
- **Audit trail** - track who logged what and when

#### **Time Entry Interface:**
- Dropdown with assigned projects in format: `PROJECT_NAME (COMPANY_NAME)`
- Date picker for selecting entry date
- Hours input with decimal support
- Description field for detailed notes
- Real-time form validation

### **📊 Reporting System**

#### **Report Types:**

**📈 Personal Reports (Regular Users)**
- Personal time summary grouped by companies and projects
- Daily breakdown of hours worked
- Total hours per project and company
- Excel export functionality
- Interactive charts (company distribution, hours by project)
- Date range filtering

**📊 Admin Reports (Super/Company Admins)**
- **User Summary Reports** - Time spent by users across projects
- **Project Summary Reports** - Time spent on specific projects by team members
- **Company Summary Reports** - Complete overview for company clients
- **Daily Reports** - Daily time entries with detailed breakdown
- **All Users Report** - Comprehensive report for all users with summary tables

#### **Excel Export Features:**
- **Personal Report Export**: Grouped by companies and projects, daily columns, project totals, company totals, final summary
- **User Report Export**: Same format as personal reports for individual users
- **All Users Export**: Comprehensive summary with totals by company, project, and user
- **Dynamic date columns** based on selected period
- **Professional formatting** with headers, borders, and color coding

### **🎨 User Interface & Customization**

#### **Color Theme System:**
- **Primary Colors**: Emerald, Purple, Chocolate, Blue, Red, Orange, Teal, Pink, Custom
- **Secondary Colors**: White, Emerald, Purple, Chocolate, Blue, Red, Orange, Teal, Pink, Custom
- **Text Colors**: Primary, Secondary, Light, White, Dark, Custom
- **Custom Color Picker**: RGB color picker with hex input validation
- **Real-time Preview**: See changes before saving
- **Persistent Settings**: Colors are saved and applied on every visit

#### **Responsive Design:**
- Mobile-friendly interface
- Bootstrap 5 framework
- Modern, clean design
- Intuitive navigation

### **🔍 Advanced Features**

#### **Filtering & Search:**
- **Project filtering** by company
- **Date range filtering** for reports and time entries
- **Company filtering** for time entries
- **Dynamic dropdown updates** based on selections
- **Search functionality** in user management

#### **Data Management:**
- **Database clearing** functionality (preserves super admin data)
- **Mock data generation** for testing
- **Soft deletion** for user-project assignments
- **Data validation** and error handling

---

## 🛠️ **Technical Stack**

### **Backend:**
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **PyMySQL** - MySQL database connector
- **Flask-Login** - User authentication
- **Flask-WTF** - Form handling and CSRF protection
- **Flask-Migrate** - Database migrations
- **openpyxl** - Excel file generation

### **Frontend:**
- **Bootstrap 5** - CSS framework
- **Vanilla JavaScript** - Dynamic functionality
- **AJAX** - Asynchronous data loading
- **Chart.js** - Interactive charts and graphs

### **Database:**
- **MariaDB/MySQL** - Relational database
- **UTF-8 encoding** - International character support

---

## 📋 **Prerequisites**

### **Required Software:**
- **Python 3.8+**
- **MariaDB/MySQL server**
- **Git** (for cloning)
- **pip** (Python package manager)

### **System Requirements:**
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: 1GB free space
- **Network**: Internet connection for package installation

---

## 🚀 **Installation Guide**

### **Step-by-Step Setup Instructions**

#### **1. Clone the Repository**
```bash
# Clone the repository
git clone <repository-url>
cd "Dixi time managment za lupu"

# Verify the directory structure
ls -la
```

#### **2. Set Up Python Environment**

**On macOS:**
```bash
# Check Python version (should be 3.8+)
python3 --version

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show venv in prompt)
which python
```

**On Windows:**
```bash
# Check Python version
python --version

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

#### **3. Install Dependencies**
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

#### **4. Database Setup**

**Install MariaDB/MySQL:**

**On macOS (using Homebrew):**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install MariaDB
brew install mariadb

# Start MariaDB service
brew services start mariadb

# Secure installation
mysql_secure_installation
```

**On macOS (using MAMP):**
1. Download and install MAMP from https://www.mamp.info/
2. Start MAMP and ensure MySQL is running
3. Access phpMyAdmin to create database

**Create Database:**
```sql
-- Connect to MySQL/MariaDB
mysql -u root -p

-- Create database
CREATE DATABASE time_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (optional but recommended)
CREATE USER 'timeuser'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON time_management.* TO 'timeuser'@'localhost';
FLUSH PRIVILEGES;

-- Exit MySQL
EXIT;
```

#### **5. Configure Application**

**Create Environment File:**
```bash
# Create .env file
touch .env
```

**Add to .env file:**
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://username:password@localhost/time_management
```

**Update config.py:**
```python
# Update database connection in config.py
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://username:password@localhost/time_management'
```

#### **6. Initialize Database**

**Set up Flask environment:**
```bash
# Set Flask app
export FLASK_APP=run.py

# On Windows:
# set FLASK_APP=run.py
```

**Initialize database:**
```bash
# Initialize migrations (first time only)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade

# Verify database tables
flask db current
```

#### **7. Create Super Admin**
```bash
# Create super admin user
flask create-super-admin

# Follow prompts to create admin account
```

#### **8. Run the Application**
```bash
# Start the application
python run.py

# Or using Flask
flask run --host=0.0.0.0 --port=5000
```

**Access the application:**
- **Local**: http://localhost:5000
- **Network**: http://your-ip-address:5000

---

## 🎯 **Usage Guide**

### **First Time Setup**

1. **Login as Super Admin**
   - Use the credentials created during setup
   - Access admin panel from navigation

2. **Create Companies**
   - Go to Admin → Companies → New Company
   - Add company details and contact information

3. **Create Projects**
   - Go to Admin → Projects → New Project
   - Select company and add project details

4. **Create Users**
   - Go to Admin → Users → New User
   - Set appropriate role and hourly rate

5. **Assign Users to Projects**
   - Go to Admin → Projects → Select Project → Users
   - Assign users with appropriate roles

### **Daily Usage**

#### **For Regular Users:**
1. **Log Time Entries**
   - Go to Dashboard → Quick Actions → Unesi vreme
   - Select project from dropdown
   - Enter hours and description
   - Save entry

2. **View Reports**
   - Go to Izveštaji (Reports)
   - View personal time summary
   - Export to Excel if needed

3. **Customize Interface**
   - Go to Podešavanja (Settings) → Preferencije
   - Choose colors and save preferences

#### **For Admins:**
1. **Manage Users and Projects**
   - Use admin panel for user/project management
   - Assign users to projects as needed

2. **Generate Reports**
   - Access comprehensive reports
   - Export data to Excel
   - View statistics and charts

3. **System Administration**
   - Monitor system usage
   - Clear database if needed
   - Generate mock data for testing

---

## 🔧 **Configuration Options**

### **Environment Variables**
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://user:pass@localhost/db
```

### **Database Configuration**
```python
# config.py
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/time_management'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### **Application Settings**
- **Debug Mode**: Set `FLASK_ENV=development` for debug mode
- **Port**: Change port in `run.py` or use `--port` flag
- **Host**: Use `--host=0.0.0.0` for network access

---

## 🗄️ **Database Management**

### **Migration Commands**
```bash
# Initialize migrations (first time)
flask db init

# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# Show migration history
flask db history

# Show current version
flask db current
```

### **Database Backup**
```bash
# Backup database
mysqldump -u username -p time_management > backup.sql

# Restore database
mysql -u username -p time_management < backup.sql
```

### **Clear Database**
- Access Admin → Clear Database
- Enter confirmation code: `DELETE_ALL_DATA`
- Super admin data will be preserved

---

## 🔒 **Security Features**

### **Authentication & Authorization**
- **Password Hashing**: Werkzeug security
- **Session Management**: Flask-Login
- **CSRF Protection**: Flask-WTF
- **Role-based Access**: Custom decorators

### **Data Protection**
- **Input Validation**: Form validation and sanitization
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Protection**: Template escaping
- **Secure Headers**: Flask security headers

---

## 📈 **Troubleshooting**

### **Common Issues & Solutions**

#### **Database Connection Issues**
```bash
# Check MySQL service
brew services list | grep mysql

# Restart MySQL
brew services restart mariadb

# Check connection
mysql -u username -p -h localhost
```

#### **Python Environment Issues**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **Port Already in Use**
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
flask run --port=5001
```

#### **Migration Issues**
```bash
# Reset migrations
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### **Log Files**
- **Application logs**: Check console output
- **Database logs**: Check MySQL error log
- **System logs**: Check system logs for errors

---

## 🚀 **Deployment**

### **Production Setup**

#### **1. Environment Preparation**
```bash
# Set production environment
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
```

#### **2. Database Configuration**
```bash
# Use production database
# Configure proper user permissions
# Set up database backup schedule
```

#### **3. Web Server Setup**
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

#### **4. Reverse Proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📚 **API Documentation**

### **Authentication Endpoints**
- `POST /login` - User login
- `POST /logout` - User logout

### **Time Entry Endpoints**
- `GET /time-entry` - Time entry form
- `POST /time-entry` - Submit time entry
- `GET /my-time-entries` - Personal time entries

### **Admin Endpoints**
- `GET /admin/` - Admin dashboard
- `GET /admin/users` - User management
- `POST /admin/users/new` - Create user
- `GET /admin/projects` - Project management

### **Report Endpoints**
- `GET /reports/` - Reports overview
- `GET /reports/export/user/<id>` - Export user report
- `GET /reports/export/all-users` - Export all users report

---

## 🔮 **Future Enhancements**

### **Planned Features**
- [ ] **Task Management** - Create and track tasks within projects
- [ ] **Sprint Planning** - Agile project management features
- [ ] **Invoice Generation** - Automatic invoice creation
- [ ] **Email Notifications** - Automated email alerts
- [ ] **Mobile App** - Native mobile application
- [ ] **API Integration** - Third-party service integrations
- [ ] **Advanced Analytics** - Machine learning insights
- [ ] **Time Approval Workflow** - Manager approval system
- [ ] **Project Budget Tracking** - Budget monitoring
- [ ] **Calendar Integration** - Sync with calendar systems

### **Technical Improvements**
- [ ] **Performance Optimization** - Database query optimization
- [ ] **Caching System** - Redis integration
- [ ] **Microservices Architecture** - Service decomposition
- [ ] **Containerization** - Docker support
- [ ] **CI/CD Pipeline** - Automated deployment

---

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit changes: `git commit -m "Add feature"`
5. Push to branch: `git push origin feature-name`
6. Create pull request

### **Code Standards**
- Follow PEP 8 Python style guide
- Add comments for complex logic
- Write tests for new features
- Update documentation

---

## 📝 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 **Support & Contact**

### **Getting Help**
- **Documentation**: Check this README first
- **Issues**: Create an issue in the repository
- **Email**: Contact the development team

### **Useful Commands**
```bash
# Check application status
flask routes

# Check database status
flask db current

# Run tests (if available)
python -m pytest

# Check Python packages
pip list

# Check system resources
top
```

---

## 🎉 **Acknowledgments**

- **Flask Community** - Excellent web framework
- **Bootstrap Team** - Beautiful UI components
- **SQLAlchemy Team** - Powerful ORM
- **All Contributors** - Your feedback and contributions

---

**Made with ❤️ for efficient time management!**

*This application helps teams track time effectively across multiple projects and companies, providing comprehensive reporting and user-friendly interface for optimal productivity.* 