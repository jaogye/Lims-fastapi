# LIMS FastAPI

A modern Laboratory Information Management System (LIMS) built with FastAPI, migrated from the original MATLAB-based system.

## Overview

This project is a complete RESTful API implementation for managing laboratory operations, including sample tracking, quality control measurements, specification management, and automated report generation. The system replaces the legacy MATLAB-based LIMS with a modern, scalable web API built on Python and FastAPI.

## Features

- **Sample Management**: Handle production, customer, and manual samples
- **Report Generation**: Generate COA, COC, and certificate reports in PDF format
- **Master Data Management**: Excel-based import/export for products, qualities, variables, etc.
- **User Authentication**: JWT-based authentication with role-based access control
- **Background Tasks**: Scheduled sample generation and report processing
- **RESTful API**: Complete REST API with automatic documentation

## Technology Stack

- **Backend**: FastAPI + Python 3.11
- **Database**: SQL Server with SQLAlchemy ORM
- **Authentication**: JWT tokens with passlib
- **Reports**: ReportLab for PDF generation
- **Background Tasks**: Celery + Redis
- **Containerization**: Docker + Docker Compose

## Project Structure

```
lims-fastapi/
├── app/
│   ├── api/                    # API route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── samples.py         # Sample management endpoints
│   │   ├── reports.py         # Report generation endpoints
│   │   └── master_data.py     # Master data endpoints
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
│   │   ├── report_service.py # Report generation service
│   │   └── master_data_service.py # Master data service
│   ├── reports/              # Report generation utilities
│   ├── utils/                # Utility functions
│   └── main.py              # FastAPI application entry point
├── tests/                    # Test suite
├── docs/                     # Documentation
├── scripts/                  # Database and deployment scripts
├── templates/               # Report templates
├── static/                  # Static files
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Multi-container setup
└── README.md               # This file
```

## Quick Start

### 1. Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd lims-fastapi

# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f lims-api
```

The application will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your database settings
nano .env

# Run database migrations (if applicable)
python -m alembic upgrade head

# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=1433
DATABASE_NAME=LIMS_PVS
DATABASE_USER=sa
DATABASE_PASSWORD=YourPassword

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
LOG_LEVEL=INFO
```

### Database Setup

1. **SQL Server**: Ensure SQL Server is running and accessible
2. **Database**: Create the LIMS_PVS database
3. **Tables**: Tables will be created automatically on first run
4. **Data Migration**: Use the provided scripts to migrate data from MATLAB system

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Samples
- `GET /api/samples` - List samples
- `POST /api/samples` - Create new sample
- `GET /api/samples/{id}` - Get sample details
- `GET /api/samples/{id}/measurements` - Get sample measurements
- `POST /api/samples/{id}/measurements` - Add measurement

### Reports
- `GET /api/reports/coa/{sample_id}` - Generate COA report
- `GET /api/reports/coc/{sample_id}` - Generate COC report
- `GET /api/reports/day-certificate` - Generate daily certificate

### Master Data
- `GET /api/master-data/products` - List products
- `GET /api/master-data/qualities` - List qualities
- `GET /api/master-data/variables` - List variables
- `POST /api/master-data/upload` - Upload Excel data
- `GET /api/master-data/download/{type}` - Download Excel template

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Code Quality

```bash
# Format code
black app/

# Check linting
flake8 app/

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

## Deployment

### Production Deployment

1. **Environment**: Set `DEBUG=False` and configure production settings
2. **Database**: Use production SQL Server instance
3. **Security**: Use strong secret keys and secure passwords
4. **HTTPS**: Configure SSL/TLS certificates
5. **Monitoring**: Set up logging and monitoring

### Docker Deployment

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

## Migration from MATLAB

The system includes utilities to migrate data from the original MATLAB LIMS:

1. **Database Schema**: SQLAlchemy models match the original database schema
2. **Authentication**: Compatible hash verification for existing users
3. **Sample Numbers**: Maintains the same sample numbering format
4. **Reports**: PDF reports replicate the MATLAB-generated formats

### Migration Steps

1. Backup the original MATLAB database
2. Run data validation scripts
3. Import master data using Excel templates
4. Verify sample data integrity
5. Test report generation
6. Train users on the new interface

## Troubleshooting

### Common Issues

1. **Database Connection**: Check connection string and SQL Server availability
2. **Authentication**: Verify JWT secret key configuration
3. **Reports**: Ensure ReportLab dependencies are installed
4. **File Permissions**: Check upload/temp directory permissions

### Logs

```bash
# View application logs
docker-compose logs -f lims-api

# View database logs
docker-compose logs -f sqlserver

# View worker logs
docker-compose logs -f celery-worker
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Code Documentation

All Python files in this project include comprehensive docstrings following PEP 257 conventions:
- Module-level docstrings explaining the purpose of each file
- Class docstrings describing attributes and responsibilities
- Function/method docstrings with parameters, returns, and exceptions
- Inline comments for complex logic

### Key Files

- `main.py` - Main FastAPI application entry point
- `working_app.py` - Simplified test application
- `load_logisticdata.py` - Script to populate logistic data for testing
- `app/models/` - SQLAlchemy ORM models for database tables
- `app/services/` - Business logic and data processing services
- `app/api/` - FastAPI route handlers and endpoints
- `app/core/` - Configuration and security utilities
- `app/database/` - Database connection and session management

## Project Status

This is an active development project migrating from MATLAB to FastAPI. Current features include:
- Core sample management
- Report generation (COA, COC, certificates)
- User authentication with JWT
- Master data management via Excel import/export
- Logistic data integration

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs` when running the application