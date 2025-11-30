# Project Structure

## Directory Organization

```
├── app/                        # Main application package
│   ├── __init__.py            # Application factory
│   ├── config.py              # Configuration classes
│   ├── cli_commands.py        # Flask CLI commands
│   ├── models/                # SQLAlchemy models
│   ├── routes/                # Blueprint route handlers
│   ├── services/              # Business logic layer
│   ├── forms/                 # WTForms form classes
│   ├── jobs/                  # Background job definitions
│   ├── templates/             # Jinja2 HTML templates
│   └── utils/                 # Utility functions
├── ml_models/                 # Machine learning models
├── static/                    # Static assets (CSS, JS, images)
├── tests/                     # Test suite
├── scripts/                   # Utility scripts
├── docs/                      # Documentation
└── migrations/                # Database migrations
```

## Architecture Patterns

### Application Factory Pattern
- `app/__init__.py` creates Flask app with `create_app(config_name)`
- Supports multiple configurations (development, production, testing)
- Extensions initialized with app context

### Layered Architecture
1. **Routes** (`app/routes/`) - HTTP request handling, form validation, response rendering
2. **Services** (`app/services/`) - Business logic, transaction management, data orchestration
3. **Models** (`app/models/`) - Database entities, relationships, basic validation
4. **Utils** (`app/utils/`) - Cross-cutting concerns (logging, error handling, security)

### Blueprint Organization
Each feature area has its own blueprint:
- `auth` - Authentication (login, register, profile)
- `dashboard` - Main dashboard and predictions
- `portfolio` - Portfolio viewing and wallet management
- `orders` - Buy/sell order execution
- `reports` - Report generation
- `admin` - Admin panel
- `api` - REST API endpoints
- `notifications` - Notification management

## Key Conventions

### Models
- Use SQLAlchemy ORM with declarative base
- Table names are plural (e.g., `users`, `orders`)
- Primary keys named `{table}_id` (e.g., `user_id`, `order_id`)
- Timestamps: `created_at`, `updated_at`, `last_updated`
- Use Enums for status fields
- Define relationships with `backref` and `cascade` options

### Services
- One service class per domain (e.g., `PortfolioService`, `TransactionEngine`)
- Methods raise custom exceptions (`ValidationError`, `InsufficientFundsError`)
- Use database transactions with proper rollback handling
- Log important operations and errors
- Return domain objects or dictionaries, not database models directly

### Routes
- Use `@login_required` decorator for protected routes
- Flash messages for user feedback (categories: success, error, info, warning)
- Redirect after POST (PRG pattern)
- Handle exceptions with try/except and user-friendly messages
- Use forms for input validation

### Forms
- WTForms with Flask-WTF integration
- CSRF protection enabled by default
- Custom validators in form classes
- Separate form classes per feature (e.g., `auth_forms.py`, `order_forms.py`)

### Templates
- Base template: `templates/base.html`
- Feature-specific subdirectories (e.g., `templates/portfolio/`, `templates/orders/`)
- Use Jinja2 template inheritance
- XSS protection with custom filters (`safe_url`, `sanitize`)

### Testing
- Test files mirror source structure: `tests/test_models/`, `tests/test_services/`, etc.
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.routes`
- Fixtures in `tests/conftest.py`
- Target: 85%+ code coverage
- AAA pattern (Arrange, Act, Assert)

### Security
- CSRF protection on all forms
- Password hashing with bcrypt
- SQL injection prevention via SQLAlchemy ORM
- XSS protection with output sanitization
- Security headers on all responses
- Input validation at form and service layers

### Error Handling
- Custom exception classes in `app/utils/exceptions.py`
- Global error handlers in `app/utils/error_handlers.py`
- Custom error pages: `templates/errors/400.html`, `404.html`, `500.html`
- Structured logging with context

### Background Jobs
- APScheduler for scheduled tasks
- Job definitions in `app/jobs/`
- Job logs in `job_log` table
- Configurable via `JOBS_ENABLED` environment variable

## File Naming Conventions

- Python files: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Templates: `snake_case.html`
- Static files: `kebab-case.css`, `kebab-case.js`

## Import Order (isort profile: black)
1. Standard library imports
2. Third-party imports
3. Local application imports
4. Relative imports

## Code Style
- Black formatter (line length: 120)
- Type hints encouraged but not required
- Docstrings for classes and public methods
- Comments for complex logic only
