"""
SQL Security Utilities
Provides utilities and guidelines for SQL injection prevention
"""
from sqlalchemy import text
from app import db


def safe_execute_query(query_string, params=None):
    """
    Safely execute a raw SQL query with parameterized inputs
    
    This function should ONLY be used when ORM queries are not feasible.
    Always prefer SQLAlchemy ORM methods over raw SQL.
    
    Args:
        query_string: SQL query with named parameters (e.g., "SELECT * FROM users WHERE id = :user_id")
        params: Dictionary of parameter values (e.g., {"user_id": 123})
    
    Returns:
        Query result
    
    Example:
        result = safe_execute_query(
            "SELECT * FROM users WHERE email = :email",
            {"email": user_email}
        )
    
    Security Notes:
        - NEVER concatenate user input directly into SQL strings
        - ALWAYS use named parameters (:param_name) or positional parameters (?)
        - Validate and sanitize all user inputs before passing to this function
    """
    if params is None:
        params = {}
    
    # Use SQLAlchemy's text() with bound parameters
    return db.session.execute(text(query_string), params)


# SQL Injection Prevention Guidelines
"""
SECURITY BEST PRACTICES FOR SQL INJECTION PREVENTION:

1. ALWAYS USE SQLAlchemy ORM:
   ✓ GOOD: User.query.filter_by(email=user_email).first()
   ✗ BAD:  db.session.execute(f"SELECT * FROM users WHERE email = '{user_email}'")

2. USE PARAMETERIZED QUERIES FOR RAW SQL:
   ✓ GOOD: db.session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
   ✗ BAD:  db.session.execute(f"SELECT * FROM users WHERE id = {user_id}")

3. VALIDATE ALL USER INPUTS:
   - Use validators.py functions to validate data types and formats
   - Sanitize inputs before database operations
   - Use WTForms validation for form inputs

4. AVOID DYNAMIC TABLE/COLUMN NAMES:
   - Never use user input to construct table or column names
   - If necessary, use a whitelist of allowed values

5. USE ORM RELATIONSHIPS:
   ✓ GOOD: user.holdings.filter_by(company_id=company_id)
   ✗ BAD:  Raw SQL joins with user input

6. LIMIT DATABASE PERMISSIONS:
   - Application database user should have minimal required permissions
   - No DROP, CREATE, or ALTER permissions in production

7. LOG SUSPICIOUS ACTIVITY:
   - Log all failed validation attempts
   - Monitor for SQL injection patterns in inputs

EXAMPLES OF SAFE QUERIES:

# Filter by single field
user = User.query.filter_by(email=email).first()

# Filter with multiple conditions
holdings = Holdings.query.filter(
    Holdings.user_id == user_id,
    Holdings.quantity > 0
).all()

# Join with relationships
orders = Order.query.join(Company).filter(
    Order.user_id == user_id,
    Company.symbol == symbol
).all()

# Parameterized raw query (only when ORM is not feasible)
result = db.session.execute(
    text("SELECT * FROM users WHERE email = :email AND status = :status"),
    {"email": email, "status": "active"}
)

NEVER DO THIS:
# String concatenation - VULNERABLE TO SQL INJECTION!
query = f"SELECT * FROM users WHERE email = '{email}'"  # ✗ DANGEROUS!
db.session.execute(query)

# String formatting - STILL VULNERABLE!
query = "SELECT * FROM users WHERE id = {}".format(user_id)  # ✗ DANGEROUS!
db.session.execute(query)
"""
