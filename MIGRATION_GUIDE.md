# Database Migration Guide

This guide explains how to use Flask-Migrate (Alembic) for database schema management.

## Initial Setup

### 1. Initialize Migrations

Run this once to create the migrations directory:

```bash
flask db init
```

This creates a `migrations/` directory with the following structure:
```
migrations/
├── alembic.ini
├── env.py
├── README
├── script.py.mako
└── versions/
```

## Creating Migrations

### 2. Create Initial Migration

After defining your models, create the first migration:

```bash
flask db migrate -m "Initial migration"
```

This generates a migration script in `migrations/versions/` that creates all tables.

### 3. Review the Migration

Always review the generated migration file before applying it:

```bash
cat migrations/versions/xxxx_initial_migration.py
```

Check that:
- All tables are being created
- Foreign keys are correct
- Indexes are in place
- Constraints are defined

### 4. Apply the Migration

Apply the migration to create tables in the database:

```bash
flask db upgrade
```

## Making Changes

### When You Modify Models

1. **Edit the model** in `app/models/`
2. **Generate migration**:
   ```bash
   flask db migrate -m "Add column to users table"
   ```
3. **Review the migration** file
4. **Apply the migration**:
   ```bash
   flask db upgrade
   ```

### Example: Adding a Column

```python
# In app/models/user.py
class User(db.Model):
    # ... existing fields ...
    phone_number = db.Column(db.String(20))  # New field
```

```bash
flask db migrate -m "Add phone_number to users"
flask db upgrade
```

## Common Commands

### Show Current Revision

```bash
flask db current
```

### Show Migration History

```bash
flask db history
```

### Upgrade to Specific Revision

```bash
flask db upgrade <revision>
```

### Downgrade One Revision

```bash
flask db downgrade
```

### Downgrade to Specific Revision

```bash
flask db downgrade <revision>
```

### Downgrade to Base (Remove All)

```bash
flask db downgrade base
```

## Best Practices

### 1. Always Review Migrations

Auto-generated migrations may not be perfect. Review and edit if needed:
- Check for data loss operations
- Verify foreign key relationships
- Ensure indexes are created
- Add data migrations if needed

### 2. Test Migrations

Test migrations in development before applying to production:

```bash
# Create test database
flask db upgrade

# Test downgrade
flask db downgrade

# Re-upgrade
flask db upgrade
```

### 3. Version Control

Always commit migration files to version control:

```bash
git add migrations/versions/xxxx_*.py
git commit -m "Add migration for user table changes"
```

### 4. Production Deployment

For production:

```bash
# Backup database first!
mysqldump -u user -p stock_portfolio > backup.sql

# Apply migrations
flask db upgrade

# Verify
flask db current
```

### 5. Handle Data Migrations

For complex changes, add data migration code:

```python
# In migration file
def upgrade():
    # Schema changes
    op.add_column('users', sa.Column('status', sa.String(20)))
    
    # Data migration
    connection = op.get_bind()
    connection.execute(
        "UPDATE users SET status = 'active' WHERE account_status = 'active'"
    )

def downgrade():
    op.drop_column('users', 'status')
```

## Troubleshooting

### Migration Conflicts

If you have conflicts (multiple heads):

```bash
flask db merge heads -m "Merge migrations"
flask db upgrade
```

### Reset Migrations

To start fresh (⚠️ DESTROYS DATA):

```bash
# Drop all tables
flask db downgrade base

# Delete migrations
rm -rf migrations/

# Start over
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Manual Migration Editing

If auto-generation fails, create empty migration:

```bash
flask db revision -m "Manual migration"
```

Edit the file in `migrations/versions/` manually.

## Migration File Structure

```python
"""Description of migration

Revision ID: xxxxxxxxxxxx
Revises: yyyyyyyyyyyy
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'xxxxxxxxxxxx'
down_revision = 'yyyyyyyyyyyy'
branch_labels = None
depends_on = None

def upgrade():
    # Schema changes to apply
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('user_id')
    )

def downgrade():
    # Reverse the changes
    op.drop_table('users')
```

## Integration with CI/CD

### Automated Testing

```bash
# In CI pipeline
flask db upgrade
pytest
flask db downgrade base
```

### Production Deployment

```yaml
# Example deployment script
steps:
  - name: Backup Database
    run: ./scripts/backup_db.sh
  
  - name: Run Migrations
    run: flask db upgrade
  
  - name: Verify Migration
    run: flask db current
  
  - name: Run Health Check
    run: python scripts/test_db_connection.py
```

## Additional Resources

- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
