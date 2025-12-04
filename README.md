# LIMS FastAPI

A modern Laboratory Information Management System (LIMS) built with FastAPI and React, migrated from the original MATLAB-based system.

## Overview

This project is a complete full-stack web application for managing laboratory operations, including sample tracking, quality control measurements, specification management, and automated report generation. The system replaces the legacy MATLAB-based LIMS with a modern, scalable web application built on Python FastAPI (backend) and React + TypeScript (frontend).

## Features

### Core Features
- **Sample Management**: Handle production, customer, and manual samples with full CRUD operations
- **Report Generation**: Generate COA, COC, and day certificate reports in PDF format
- **Master Data Management**: Excel-based import/export for products, qualities, variables, specifications, etc.
- **User Authentication**: JWT-based authentication with role-based access control
- **User Administration**: Complete user management with access permissions and digital signatures
- **Web Interface**: Modern React-based web UI with AG-Grid for data tables
- **RESTful API**: Complete REST API with automatic OpenAPI documentation

### New Features (Latest Version)
- **Manual Sample Management**: Create, edit, and delete manual samples via web UI
- **User Administration UI**: Manage users, permissions, and upload signature images
- **Master Data UI**: Download/upload Excel templates directly from web interface
- **Input Data UI**: Lab technicians can enter sample measurements with real-time validation
- **Single Page Application**: Responsive web UI that runs entirely in the browser

## Technology Stack

### Backend
- **Framework**: FastAPI + Python 3.11
- **Database**: SQL Server with SQLAlchemy ORM
- **Authentication**: JWT tokens with passlib password hashing
- **Reports**: ReportLab for PDF generation
- **API Documentation**: OpenAPI (Swagger) + ReDoc

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Data Grid**: AG-Grid Community Edition
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **UI**: Custom CSS with responsive design

## Project Structure

```
lims-fastapi/
├── app/
│   ├── api/                    # API route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── samples.py         # Sample management & manual samples
│   │   ├── reports.py         # Report generation endpoints
│   │   ├── master_data.py     # Master data management
│   │   └── users.py           # User administration (NEW)
│   ├── core/                  # Core configuration and security
│   │   ├── config.py          # Application settings
│   │   └── security.py        # Security utilities
│   ├── database/              # Database configuration
│   │   └── connection.py      # Database connection setup
│   ├── models/                # SQLAlchemy models
│   │   ├── base.py           # Base model class
│   │   ├── user.py           # User-related models
│   │   ├── laboratory.py     # Laboratory data models
│   │   ├── sample.py         # Sample and measurement models
│   │   └── specification.py  # Specification models
│   ├── services/              # Business logic services
│   │   ├── auth_service.py   # Authentication service
│   │   ├── sample_service.py # Sample management service
│   │   ├── user_service.py   # User administration (NEW)
│   │   ├── report_service.py # Report generation service
│   │   └── master_data_service.py # Master data service
│   ├── reports/              # Report generation utilities
│   └── utils/                # Utility functions
├── frontend/                 # React frontend (NEW)
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Layout/      # Sidebar & layout
│   │   │   ├── Login/       # Login page
│   │   │   ├── MasterTable/ # Master data UI
│   │   │   ├── InputData/   # Lab data entry
│   │   │   ├── ManualSample/# Manual sample management
│   │   │   └── UserAdmin/   # User administration
│   │   ├── services/        # API service layer
│   │   ├── types/           # TypeScript types
│   │   ├── App.tsx          # Main app component
│   │   └── main.tsx         # Entry point
│   ├── package.json         # NPM dependencies
│   ├── vite.config.ts       # Vite configuration
│   └── tsconfig.json        # TypeScript config
├── static/                  # Built frontend files
├── signatures/              # User signature images (NEW)
├── tests/                   # Test suite
├── images/                  # MATLAB UI screenshots
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── FRONTEND_IMPLEMENTATION_GUIDE.md  # Frontend dev guide (NEW)
├── PROJECT_SUMMARY.md      # Project summary (NEW)
└── README.md              # This file
```

## Quick Start

### Option 1: Full Stack Development

**Backend Setup:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database in .env file
cp .env.example .env
nano .env  # Edit with your settings

# Start backend
python main.py
```
Backend runs at http://localhost:8000

**Frontend Setup:**
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```
Frontend dev server runs at http://localhost:5173

### Option 2: Production Deployment

```bash
# Build frontend
cd frontend
npm run build

# This creates the static/ directory
# Now just run the backend
python main.py
```
Access the full application at http://localhost:8000

The backend will serve the built React app automatically.

## API Documentation

Once the application is running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/login` - User login, returns JWT token
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info with permissions

### Samples
- `GET /api/samples` - List samples (with optional filters)
- `GET /api/samples/get_samples` - Get samples with measurements for a date
- `POST /api/samples/create-sample` - Create samples for a specific date
- `POST /api/samples/update_samples` - Batch update sample measurements
- `POST /api/samples/load-customer-samples` - Load customer samples from logistic data
- `POST /api/samples/load-production-samples` - Generate production samples
- `POST /api/samples/{sample_number}/refresh` - Refresh sample specifications
- `GET /api/samples/{sample_number}/status` - Get sample completion status

### Manual Samples (NEW)
- `GET /api/samples/manual-samples` - Get manual samples for a date
- `POST /api/samples/manual-samples` - Create new manual sample
- `PUT /api/samples/manual-samples/{id}` - Update manual sample
- `DELETE /api/samples/manual-samples/{id}` - Delete manual sample

### Reports
- `GET /api/reports/coa/{sample_number}` - Generate COA report (PDF)
- `GET /api/reports/coc/{sample_number}` - Generate COC report (PDF)
- `GET /api/reports/day-certificate/{sample_number}` - Generate daily certificate (PDF)

### Master Data
- `GET /api/master-data/products` - List all products (NEW)
- `GET /api/master-data/qualities` - List all qualities (NEW)
- `GET /api/master-data/sample-points` - List all sample points (NEW)
- `GET /api/master-data/variables` - List all variables (NEW)
- `GET /api/master-data/download/{table_type}` - Download Excel template
- `POST /api/master-data/upload` - Upload Excel data
- `GET /api/master-data/download-errors/{filename}` - Download error file

**Supported table types:** products, qualities, variables, holidays, sample_points, spec-client, spec-gen, samplematrix, maps

### User Administration (NEW)
- `GET /api/users/` - List all users (admin only)
- `GET /api/users/{id}` - Get user details
- `POST /api/users/` - Create new user (admin only)
- `PUT /api/users/{id}` - Update user (admin only)
- `POST /api/users/{id}/reset-password` - Reset user password (admin only)
- `POST /api/users/{id}/signature` - Upload user signature image
- `GET /api/users/{id}/signature` - Get user signature image
- `GET /api/users/{id}/access` - Get user access permissions
- `PUT /api/users/{id}/access` - Update user access permissions

## Web Interface

The application includes a modern web interface with the following pages:

### 1. Login Page
- User authentication with username/password
- Password change for new users
- JWT token management

### 2. Master Tables
- Dropdown to select table type
- AG-Grid display with dynamic columns
- Download to Excel functionality
- Upload from Excel with validation
- Error display for failed uploads

### 3. Input Data (Lab Results)
- Date picker for sample selection
- Sample list with color coding:
  - Green: All measurements complete
  - Orange: Incomplete measurements
- Sample details panel with measurement grid
- Quality information with min/max ranges
- Buttons: Get Data, Update, COA, COC, C of Day
- Real-time validation of measurement values

### 4. Manual Sample
- Create, edit, and delete manual samples
- Date-based filtering
- Dropdowns for Sample Point, Product, Quality
- AG-Grid for sample list
- Form for sample details

### 5. User Administration
- User grid with all users
- Create/edit user form
- Active and Administrator checkboxes
- Signature image upload
- Access permissions grid
- Password reset functionality

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=1433
DATABASE_NAME=LIMS
DATABASE_USER=sa
DATABASE_PASSWORD=YourPassword

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Application
APP_NAME=LIMS @ INC
APP_VERSION=2.0.0
DEBUG=True
LOG_LEVEL=INFO
LOG_FILE=lims.log

# CORS Settings
CORS_ORIGINS=["http://localhost:5173","http://localhost:8000"]
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

### Database Setup

1. **SQL Server**: Ensure SQL Server is running and accessible
2. **Database**: Create the LIMS database
3. **Tables**: Tables will be created automatically on first run
4. **Initial Data**: Use master data upload to populate reference tables

## Development

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Backend Development

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience script
python main.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## Migration from MATLAB

The system includes utilities to migrate data from the original MATLAB LIMS:

### Compatibility Features
1. **Database Schema**: SQLAlchemy models match the original database schema
2. **Authentication**: Compatible hash verification for existing users
3. **Sample Numbers**: Maintains the same sample numbering format (PRO/CLI/MAN + YYYYMMDD + SEQ)
4. **Reports**: PDF reports replicate the MATLAB-generated formats
5. **Business Logic**: Migrated algorithms for sample generation and validation

### Migration Steps

1. **Backup**: Backup the original MATLAB database
2. **Database**: Point the FastAPI app to the existing database
3. **Master Data**: Verify all reference tables are populated
4. **Users**: Test authentication with existing user accounts
5. **Samples**: Test sample creation and measurement entry
6. **Reports**: Verify PDF generation matches MATLAB output
7. **Training**: Train users on the new web interface

### MATLAB vs Web Interface Mapping

| MATLAB Form | Web Page | Functionality |
|-------------|----------|---------------|
| Main (Login) | Login Page | User authentication |
| MasterTables | Master Tables | Excel import/export |
| InputData/ViewLabo | Input Data | Lab measurement entry |
| ManualSample | Manual Sample | Manual sample CRUD |
| UserAdministration | User Admin | User management |

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Build frontend: `npm run build`
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Set up backup procedures
- [ ] Configure logging and monitoring
- [ ] Test all functionality
- [ ] Train end users

### Docker Deployment (Optional)

```bash
# Build production image
docker build -t lims-fastapi:latest .

# Run with production settings
docker run -d \
  --name lims-api \
  -p 8000:8000 \
  -e DEBUG=False \
  -e DATABASE_HOST=your-db-host \
  lims-fastapi:latest
```

## Troubleshooting

### Common Issues

**Backend Issues:**
- **Database Connection**: Check connection string and SQL Server availability
- **Authentication**: Verify JWT secret key configuration
- **Reports**: Ensure ReportLab dependencies are installed
- **File Permissions**: Check upload/temp directory permissions

**Frontend Issues:**
- **API Connection**: Check if backend is running on port 8000
- **CORS Errors**: Verify CORS settings in .env
- **Build Errors**: Delete `node_modules` and reinstall: `npm install`
- **Proxy Issues**: Check vite.config.ts proxy settings

### Logs

```bash
# Application logs (configured in .env)
tail -f lims.log

# Development mode console output
python main.py

# Frontend dev server
cd frontend && npm run dev
```

## Project Status

**Current Version: 2.0.0**

### Completed Features ✅
- ✅ Complete REST API with FastAPI
- ✅ JWT authentication and authorization
- ✅ Sample management (production, customer, manual)
- ✅ Manual sample CRUD operations
- ✅ User administration with access control
- ✅ Master data Excel import/export
- ✅ PDF report generation (COA, COC, Day Certificate)
- ✅ React + TypeScript web frontend
- ✅ AG-Grid integration for data tables
- ✅ Login and authentication UI
- ✅ Navigation and layout
- ✅ Static file serving

### In Progress 🚧
- 🚧 Master Table UI component
- 🚧 Input Data UI component
- 🚧 Manual Sample UI component
- 🚧 User Admin UI component

### Planned Features 📋
- 📋 Email notifications
- 📋 Advanced reporting and analytics
- 📋 Mobile-responsive design improvements
- 📋 Audit logging
- 📋 Data export to various formats
- 📋 Advanced search and filtering

## Documentation

### Additional Documentation Files
- **`FRONTEND_IMPLEMENTATION_GUIDE.md`** - Complete guide for frontend development
- **`PROJECT_SUMMARY.md`** - High-level project overview
- **`Prompt_frontend.txt`** - Original requirements and MATLAB UI descriptions

### Code Documentation
All Python files include comprehensive docstrings following PEP 257 conventions:
- Module-level docstrings explaining the purpose
- Class docstrings describing attributes and responsibilities
- Function/method docstrings with parameters, returns, and exceptions
- Inline comments for complex logic

### Key Files
- `main.py` - Main FastAPI application entry point
- `app/api/` - FastAPI route handlers and endpoints
- `app/services/` - Business logic and data processing
- `app/models/` - SQLAlchemy ORM models
- `frontend/src/` - React application source code

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the API documentation at http://localhost:8000/docs
- Review the Frontend Implementation Guide
- Create an issue in the repository
- Contact the development team

## Acknowledgments

- Migrated from the original MATLAB-based LIMS system
- Built with FastAPI, React, and AG-Grid
- Designed for laboratory quality control and sample management

---

**Version**: 2.0.0
**Last Updated**: 2025-01-27
**Status**: Active Development
