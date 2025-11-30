# Deployment Guide
## Stock Portfolio Management Platform

This guide provides comprehensive instructions for deploying the Stock Portfolio Management Platform in various environments.

## Table of Contents
- [System Requirements](#system-requirements)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Production Deployment](#production-deployment)
- [Backup and Restore](#backup-and-restore)
- [Troubleshooting](#troubleshooting)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Database**: MySQL 8.0+ or MariaDB 10.5+
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 5GB minimum
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+

### Recommended Production Requirements
- **Python**: 3.10+
- **Database**: MySQL 8.0+ with InnoDB engine
- **RAM**: 8GB+
- **CPU**: 4 cores+
- **Disk Space**: 20GB+ (SSD recommended)
- **OS**: Ubuntu 22.04 LTS or similar Linux distribution

### Required Software
- Python 3.8+
- pip (Python package manager)
- MySQL 8.0+ or MariaDB 10.5+
- Git (for version control)
- Virtual environment tool (venv or virtualenv)

### Optional Software
- **gunicorn** (production WSGI server for Linux)
- **waitress** (production WSGI server for Windows)
- **nginx** or **Apache** (reverse proxy)
- **Redis** (for caching - future enhancement)
- **Supervisor** or **systemd** (process management)

---

## Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] Python 3.8+ installed
- [ ] MySQL 8.0+ installed and running
- [ ] Database created (e.g., `stock_portfolio`)
- [ ] Database user with appropriate permissions
- [ ] Twitter API credentials (optional, for sentiment analysis)
- [ ] Secure SECRET_KEY generated
- [ ] Environment variables configured
- [ ] Firewall rules configured (if applicable)
- [ ] SSL certificate (for production HTTPS)
- [ ] Backup strategy planned

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd stock-portfolio-platform
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
- `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `DATABASE_URL`: Your MySQL connection string
- `FLASK_ENV`: Set to `production` for production deployment

See [Configuration](#configuration) section for details.

---

## Configuration

### Environment Variables

Edit the `.env` file with your configuration:

```bash
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=<your-secure-secret-key>

# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/stock_portfolio

# Optional: Twitter API (for sentiment analysis)
TWITTER_API_KEY=<your-api-key>
TWITTER_API_SECRET=<your-api-secret>
TWITTER_ACCESS_TOKEN=<your-access-token>
TWITTER_ACCESS_SECRET=<your-access-secret>
```

### Generate Secure SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database Connection String Format

```
mysql+pymysql://username:password@host:port/database
```

**Examples:**
- Local: `mysql+pymysql://root:password@localhost:3306/stock_portfolio`
- Remote: `mysql+pymysql://user:pass@db.example.com:3306/stock_portfolio_prod`

---

## Database Setup

### 1. Create Database

```sql
CREATE DATABASE stock_portfolio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stock_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON stock_portfolio.* TO 'stock_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Initialize Database Schema

```bash
# Run database migrations
flask db upgrade

# Or use the setup script
./scripts/setup_database.sh  # Linux/macOS
scripts\setup_database.bat   # Windows
```

### 3. Seed Initial Data

```bash
# Load initial data (companies, admin user)
python scripts/seed_data.py
```

**Default Admin Credentials:**
- Email: `admin@example.com`
- Password: `Admin123!@#`

**⚠️ IMPORTANT:** Change the admin password immediately after first login!

### 4. Verify Database Connection

```bash
python scripts/test_db_connection.py
```

---

## Running the Application

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Run development server
flask run

# Access at: http://localhost:5000
```

### Production Mode

#### Using Gunicorn (Linux/macOS)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:8000 'run:app'

# Or use the startup script
./scripts/start_production.sh
```

#### Using Waitress (Windows)

```bash
# Install waitress
pip install waitress

# Run server
waitress-serve --port=8000 run:app
```

---

## Production Deployment

### Quick Deployment

Use the provided deployment script:

```bash
# Linux/macOS
./scripts/deploy.sh production

# Windows
scripts\deploy.bat production
```

### Manual Production Deployment

#### 1. Set Production Environment

```bash
export FLASK_ENV=production
export SECRET_KEY=<your-secure-key>
export DATABASE_URL=<your-database-url>
```

#### 2. Install Production Dependencies

```bash
pip install gunicorn  # Linux/macOS
pip install waitress  # Windows
```

#### 3. Run Database Migrations

```bash
flask db upgrade
```

#### 4. Collect Static Files (if applicable)

```bash
# Ensure static files are in place
ls static/
```

#### 5. Start Application Server

```bash
# Gunicorn (Linux/macOS)
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    'run:app'

# Waitress (Windows)
waitress-serve --port=8000 --threads=4 run:app
```

### Using Nginx as Reverse Proxy

#### Install Nginx

```bash
sudo apt-get install nginx  # Ubuntu/Debian
```

#### Configure Nginx

Create `/etc/nginx/sites-available/stock-portfolio`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/stock-portfolio-platform/static;
        expires 30d;
    }
}
```

#### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/stock-portfolio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Using Systemd (Linux)

Create `/etc/systemd/system/stock-portfolio.service`:

```ini
[Unit]
Description=Stock Portfolio Management Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/stock-portfolio-platform
Environment="PATH=/path/to/stock-portfolio-platform/venv/bin"
ExecStart=/path/to/stock-portfolio-platform/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 'run:app'
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-portfolio
sudo systemctl start stock-portfolio
sudo systemctl status stock-portfolio
```

---

## Backup and Restore

### Automated Backup

Use the provided backup script:

```bash
# Linux/macOS
./scripts/backup_database.sh

# Windows
scripts\backup_database.bat
```

Backups are stored in the `backups/` directory with timestamp.

### Manual Backup

```bash
mysqldump -u username -p stock_portfolio > backup_$(date +%Y%m%d).sql
gzip backup_$(date +%Y%m%d).sql
```

### Restore from Backup

```bash
# Decompress backup
gunzip backup_20240115.sql.gz

# Restore database
mysql -u username -p stock_portfolio < backup_20240115.sql
```

### Backup Schedule Recommendation

- **Daily**: Automated backups at 2 AM
- **Weekly**: Full system backup
- **Monthly**: Archive to external storage
- **Retention**: Keep last 7 daily, 4 weekly, 12 monthly backups

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error:** `Can't connect to MySQL server`

**Solutions:**
- Verify MySQL is running: `sudo systemctl status mysql`
- Check DATABASE_URL in .env file
- Verify database user permissions
- Check firewall rules

#### 2. Import Errors

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solutions:**
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version`

#### 3. SECRET_KEY Not Set

**Error:** `SECRET_KEY environment variable must be set`

**Solutions:**
- Generate SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
- Add to .env file
- Export environment variable: `export SECRET_KEY=<your-key>`

#### 4. Port Already in Use

**Error:** `Address already in use`

**Solutions:**
- Check running processes: `lsof -i :8000`
- Kill process: `kill -9 <PID>`
- Use different port: `gunicorn -b 0.0.0.0:8001 'run:app'`

#### 5. Permission Denied

**Error:** `Permission denied: 'logs/app.log'`

**Solutions:**
- Create logs directory: `mkdir logs`
- Set permissions: `chmod 755 logs`
- Check file ownership

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
flask run
```

### Check Application Logs

```bash
# Application logs
tail -f logs/app.log

# Gunicorn access logs
tail -f logs/access.log

# Gunicorn error logs
tail -f logs/error.log
```

---

## Monitoring and Maintenance

### Health Checks

#### Application Health

```bash
curl http://localhost:8000/
```

#### Database Health

```bash
python scripts/test_db_connection.py
```

### Performance Monitoring

Monitor key metrics:
- Response times
- Database query performance
- Memory usage
- CPU utilization
- Error rates

### Log Rotation

Configure logrotate for application logs:

```bash
# /etc/logrotate.d/stock-portfolio
/path/to/stock-portfolio-platform/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload stock-portfolio
    endscript
}
```

### Regular Maintenance Tasks

#### Daily
- Monitor application logs
- Check error rates
- Verify backup completion

#### Weekly
- Review performance metrics
- Update dependencies (security patches)
- Clean up old logs

#### Monthly
- Full system backup
- Database optimization
- Security audit
- Capacity planning review

### Updating the Application

```bash
# 1. Backup database
./scripts/backup_database.sh

# 2. Pull latest code
git pull origin main

# 3. Activate virtual environment
source venv/bin/activate

# 4. Update dependencies
pip install -r requirements.txt

# 5. Run database migrations
flask db upgrade

# 6. Restart application
sudo systemctl restart stock-portfolio
```

---

## Security Best Practices

1. **Use HTTPS in production** - Configure SSL/TLS certificates
2. **Strong SECRET_KEY** - Generate cryptographically secure key
3. **Secure database passwords** - Use strong, unique passwords
4. **Regular updates** - Keep dependencies up-to-date
5. **Firewall configuration** - Restrict access to necessary ports
6. **Regular backups** - Automated daily backups
7. **Monitor logs** - Watch for suspicious activity
8. **Limit admin access** - Use principle of least privilege
9. **Environment variables** - Never commit .env to version control
10. **Security headers** - Configure CSP, HSTS, etc.

---

## Support and Resources

### Documentation
- [README.md](README.md) - Project overview
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Development setup
- [Testing Strategy](. kiro/specs/stock-portfolio-platform/testing-strategy.md)

### Getting Help
- Check logs in `logs/` directory
- Review error messages carefully
- Consult troubleshooting section above
- Check GitHub issues (if applicable)

### Useful Commands

```bash
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Check Flask version
flask --version

# Run database migrations
flask db upgrade

# Create new migration
flask db migrate -m "description"

# Run tests
pytest tests/ -v

# Check code style
flake8 app/

# Format code
black app/
```

---

## Appendix

### A. Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| FLASK_APP | Yes | run.py | Flask application entry point |
| FLASK_ENV | Yes | development | Environment (development/production/testing) |
| SECRET_KEY | Yes | - | Secret key for sessions (MUST be set in production) |
| DATABASE_URL | Yes | - | MySQL connection string |
| DATA_MODE | No | LIVE | Data source mode (LIVE/STATIC) |
| TWITTER_API_KEY | No | - | Twitter API key for sentiment analysis |
| SENTIMENT_ENABLED | No | True | Enable/disable sentiment analysis |
| JOBS_ENABLED | No | True | Enable/disable background jobs |
| LOG_LEVEL | No | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |

### B. Port Reference

| Port | Service | Description |
|------|---------|-------------|
| 5000 | Flask Dev Server | Development server (default) |
| 8000 | Gunicorn/Waitress | Production application server |
| 3306 | MySQL | Database server |
| 80 | Nginx | HTTP (reverse proxy) |
| 443 | Nginx | HTTPS (reverse proxy) |

### C. File Permissions

```bash
# Application files
chmod 755 scripts/*.sh
chmod 644 app/**/*.py
chmod 644 requirements.txt

# Logs directory
chmod 755 logs/
chmod 644 logs/*.log

# Environment file (sensitive)
chmod 600 .env
```

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Maintained By:** Development Team
