# Backend Deployment Guide

Comprehensive guide for deploying the Hackathon Todo FastAPI backend to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Options](#deployment-options)
  - [Option A: Railway (Recommended)](#option-a-railway-recommended)
  - [Option B: Render](#option-b-render)
  - [Option C: Self-Hosted (VPS)](#option-c-self-hosted-vps)
- [Database Setup](#database-setup)
- [Environment Variables](#environment-variables)
- [Running Migrations](#running-migrations)
- [Security Checklist](#security-checklist)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

1. **Python 3.13+** installed (on deployment server)
2. **Neon PostgreSQL** database (production instance)
3. **Git repository** with backend code
4. **Domain name** (optional, for custom domain)
5. **SSL certificate** (automatic with most platforms)

## Environment Setup

### 1. Prepare Production Environment Variables

Create a production `.env` file (never commit to git):

```env
# Database Configuration (Production)
DATABASE_URL=postgresql://user:password@prod-host.neon.tech/dbname?sslmode=require

# JWT Configuration (Production)
# IMPORTANT: Generate a new secret for production!
JWT_SECRET=<generate-with-openssl-rand-base64-32>
JWT_ALGORITHM=HS256

# CORS Configuration (Production)
# Add your frontend production domain
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# Application Configuration
ENVIRONMENT=production
```

### 2. Generate Production Secrets

Generate a secure JWT secret:

```bash
openssl rand -base64 32
```

Copy this value to both:
- Backend `JWT_SECRET` environment variable
- Frontend `BETTER_AUTH_SECRET` environment variable

**IMPORTANT**: Use the same secret in both frontend and backend!

## Deployment Options

### Option A: Railway (Recommended)

Railway provides zero-config deployment with automatic HTTPS, environment variables, and logging.

#### Step 1: Sign Up

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project

#### Step 2: Deploy from GitHub

1. Click "Deploy from GitHub repo"
2. Select your backend repository
3. Railway auto-detects FastAPI and configures deployment

#### Step 3: Configure Environment Variables

In Railway dashboard:
1. Go to your service → "Variables" tab
2. Add all environment variables:
   ```
   DATABASE_URL=<neon-production-url>
   JWT_SECRET=<your-generated-secret>
   CORS_ORIGINS=https://your-frontend.com
   ENVIRONMENT=production
   ```

#### Step 4: Configure Build Settings

Railway auto-detects Python, but verify:
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Build Command**: `pip install -e .`

#### Step 5: Deploy

1. Click "Deploy"
2. Railway builds and deploys automatically
3. Get your deployment URL: `https://your-app.railway.app`

#### Step 6: Custom Domain (Optional)

1. Go to "Settings" → "Domains"
2. Add custom domain
3. Update DNS records as instructed
4. HTTPS certificate issued automatically

**Railway Pricing**:
- Free tier: $5/month credits (enough for small projects)
- Paid: $20/month (includes all services)

---

### Option B: Render

Render offers free tier with automatic HTTPS and simple deployment.

#### Step 1: Sign Up

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Create new "Web Service"

#### Step 2: Connect Repository

1. Select "Build and deploy from a Git repository"
2. Connect your GitHub account
3. Select backend repository

#### Step 3: Configure Service

- **Name**: hackathon-todo-api
- **Environment**: Python 3
- **Build Command**: `pip install -e .`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 4`

#### Step 4: Environment Variables

Add in "Environment" section:
```
DATABASE_URL=<neon-production-url>
JWT_SECRET=<your-generated-secret>
CORS_ORIGINS=https://your-frontend.com
ENVIRONMENT=production
```

#### Step 5: Deploy

1. Click "Create Web Service"
2. Render builds and deploys
3. Get URL: `https://your-app.onrender.com`

**Render Pricing**:
- Free tier: Available (with limitations)
- Paid: $7/month per service

---

### Option C: Self-Hosted (VPS)

Deploy on your own Ubuntu 22.04+ server (DigitalOcean, Linode, AWS EC2, etc.).

#### Step 1: Server Setup

SSH into your server:
```bash
ssh user@your-server-ip
```

Update system:
```bash
sudo apt update && sudo apt upgrade -y
```

Install Python 3.13:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.13 python3.13-venv python3.13-dev -y
```

Install system dependencies:
```bash
sudo apt install nginx postgresql-client git build-essential -y
```

#### Step 2: Clone Repository

```bash
cd /opt
sudo mkdir -p /opt/hackathon-todo
sudo chown $USER:$USER /opt/hackathon-todo
git clone https://github.com/your-repo/backend.git /opt/hackathon-todo/backend
cd /opt/hackathon-todo/backend
```

#### Step 3: Create Virtual Environment

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .
```

#### Step 4: Configure Environment Variables

Create production `.env` file:
```bash
nano /opt/hackathon-todo/backend/.env
```

Add production variables:
```env
DATABASE_URL=postgresql://user:password@prod-host.neon.tech/dbname?sslmode=require
JWT_SECRET=<your-generated-secret>
JWT_ALGORITHM=HS256
CORS_ORIGINS=https://your-frontend-domain.com
ENVIRONMENT=production
```

#### Step 5: Run Database Migrations

```bash
source venv/bin/activate
cd /opt/hackathon-todo/backend

# Run SQL migrations
psql "$DATABASE_URL" < migrations/001_create_tasks_table.sql
psql "$DATABASE_URL" < migrations/002_updated_at_trigger.sql

# Verify
psql "$DATABASE_URL" -c "\dt"
```

#### Step 6: Create Systemd Service

Create service file:
```bash
sudo nano /etc/systemd/system/hackathon-todo-api.service
```

Add configuration:
```ini
[Unit]
Description=Hackathon Todo FastAPI Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/hackathon-todo/backend
Environment="PATH=/opt/hackathon-todo/backend/venv/bin"
EnvironmentFile=/opt/hackathon-todo/backend/.env
ExecStart=/opt/hackathon-todo/backend/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Set permissions:
```bash
sudo chown www-data:www-data /opt/hackathon-todo/backend -R
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hackathon-todo-api
sudo systemctl start hackathon-todo-api
```

Check status:
```bash
sudo systemctl status hackathon-todo-api
```

View logs:
```bash
sudo journalctl -u hackathon-todo-api -f
```

#### Step 7: Configure Nginx Reverse Proxy

Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/hackathon-todo-api
```

Add configuration:
```nginx
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/hackathon-todo-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 8: Setup SSL with Let's Encrypt

Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

Obtain SSL certificate:
```bash
sudo certbot --nginx -d api.your-domain.com
```

Follow prompts and select "Redirect HTTP to HTTPS".

Verify auto-renewal:
```bash
sudo certbot renew --dry-run
```

#### Step 9: Enable HSTS (Production Security)

After HTTPS is working, enable HSTS in `backend/main.py`:

Uncomment the HSTS header in SecurityHeadersMiddleware:
```python
response.headers["Strict-Transport-Security"] = (
    "max-age=31536000; includeSubDomains"
)
```

Restart service:
```bash
sudo systemctl restart hackathon-todo-api
```

---

## Database Setup

### Production Database (Neon)

1. **Create Production Database**:
   - Go to [neon.tech](https://neon.tech)
   - Create new project for production
   - Create database: `hackathon_todo_prod`
   - Copy connection string

2. **Set DATABASE_URL**:
   ```
   postgresql://user:password@prod-host.neon.tech/hackathon_todo_prod?sslmode=require
   ```

3. **Run Migrations** (see below)

### Running Migrations

Using psql:
```bash
psql "$DATABASE_URL" < migrations/001_create_tasks_table.sql
psql "$DATABASE_URL" < migrations/002_updated_at_trigger.sql
```

Verify migrations:
```bash
psql "$DATABASE_URL" -c "\dt"  # List tables
psql "$DATABASE_URL" -c "\di"  # List indexes
```

### Backup Strategy

**Automated Backups** (Neon):
- Neon provides automatic daily backups
- Enable point-in-time recovery in Neon dashboard

**Manual Backup**:
```bash
pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Restore from Backup**:
```bash
psql "$DATABASE_URL" < backup_20251212_120000.sql
```

---

## Environment Variables

### Required Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | Neon PostgreSQL production connection |
| `JWT_SECRET` | `openssl rand -base64 32` | JWT signing secret (MUST match frontend) |
| `CORS_ORIGINS` | `https://app.com,https://www.app.com` | Comma-separated frontend domains |
| `ENVIRONMENT` | `production` | Environment name |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `API_V1_PREFIX` | `/api` | API route prefix |

### Setting Environment Variables

**Railway/Render**: Use dashboard environment variables section

**Self-Hosted**: Add to `/opt/hackathon-todo/backend/.env`

**Docker**: Use `-e` flags or `.env` file with `docker-compose`

---

## Security Checklist

Before going live, verify all security measures:

- [ ] **JWT_SECRET** is randomly generated (32+ characters)
- [ ] **DATABASE_URL** uses production database (not dev/test)
- [ ] **HTTPS enabled** (SSL certificate installed)
- [ ] **CORS_ORIGINS** restricted to frontend domain only
- [ ] **HSTS header enabled** (after HTTPS is working)
- [ ] **Rate limiting active** (default: 100 req/hour per user)
- [ ] **Security headers enabled** (X-Frame-Options, CSP, etc.)
- [ ] **.env file NOT committed** to git (check `.gitignore`)
- [ ] **Database backups configured** (Neon auto-backup enabled)
- [ ] **Firewall configured** (only ports 80, 443, 22 open)
- [ ] **SSH key authentication** enabled (password login disabled)
- [ ] **Log rotation configured** (systemd handles for services)
- [ ] **Monitoring setup** (health checks, error tracking)

---

## Monitoring and Logging

### Health Check

Monitor API health:
```bash
curl https://api.your-domain.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### Application Logs

**Railway/Render**: View logs in dashboard

**Self-Hosted (systemd)**:
```bash
# View live logs
sudo journalctl -u hackathon-todo-api -f

# View last 100 lines
sudo journalctl -u hackathon-todo-api -n 100

# View logs since today
sudo journalctl -u hackathon-todo-api --since today
```

**Nginx Logs**:
```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### Error Tracking (Optional)

Consider integrating error tracking services:

**Sentry**:
```bash
pip install sentry-sdk[fastapi]
```

Add to `main.py`:
```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### Uptime Monitoring

Use uptime monitoring services:
- **UptimeRobot**: Free tier available
- **Pingdom**: Paid service
- **Better Uptime**: Free tier available

Monitor endpoint: `https://api.your-domain.com/health`

---

## Troubleshooting

### Issue: Service won't start

**Check logs**:
```bash
sudo journalctl -u hackathon-todo-api -n 50
```

**Common causes**:
- Missing environment variables
- Database connection failure
- Port already in use
- Python package missing

**Solution**:
```bash
# Check environment file exists
ls -la /opt/hackathon-todo/backend/.env

# Test database connection
psql "$DATABASE_URL" -c "SELECT 1"

# Check port availability
sudo lsof -i :8000

# Reinstall dependencies
source venv/bin/activate
pip install -e .
```

### Issue: 502 Bad Gateway (Nginx)

**Check backend service**:
```bash
sudo systemctl status hackathon-todo-api
curl http://127.0.0.1:8000/health
```

**Check Nginx config**:
```bash
sudo nginx -t
sudo systemctl status nginx
```

**Solution**:
```bash
# Restart backend service
sudo systemctl restart hackathon-todo-api

# Restart Nginx
sudo systemctl restart nginx
```

### Issue: Database connection errors

**Test connection**:
```bash
psql "$DATABASE_URL" -c "SELECT NOW()"
```

**Common causes**:
- Invalid DATABASE_URL
- Neon database paused (free tier)
- Network/firewall blocking connection
- SSL mode required

**Solution**:
- Verify DATABASE_URL in Neon dashboard
- Check Neon database is active (not paused)
- Ensure `?sslmode=require` is in connection string

### Issue: CORS errors

**Symptoms**: Frontend can't connect to API

**Check CORS_ORIGINS**:
```bash
echo $CORS_ORIGINS
```

**Solution**:
- Add frontend domain to CORS_ORIGINS
- Use exact domain (including https://)
- Restart service after changing env vars

### Issue: JWT authentication failing

**Check secret match**:
- Backend `JWT_SECRET` must match frontend `BETTER_AUTH_SECRET`
- Secrets are case-sensitive

**Solution**:
```bash
# Generate new secret
openssl rand -base64 32

# Update both frontend and backend
# Restart both services
```

### Issue: High CPU/Memory usage

**Check resource usage**:
```bash
htop
```

**Optimize**:
- Reduce number of uvicorn workers (default: 4)
- Enable caching (already implemented)
- Upgrade server resources
- Add connection pooling for database

**Adjust workers**:
Edit systemd service file:
```ini
ExecStart=/opt/hackathon-todo/backend/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2
```

Restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart hackathon-todo-api
```

---

## Post-Deployment

### Update CORS Origins

Update frontend domain in environment variables:
```env
CORS_ORIGINS=https://your-frontend.com,https://www.your-frontend.com
```

### Test All Endpoints

Use the deployed Swagger UI:
```
https://api.your-domain.com/api/docs
```

### Update Frontend API URL

In frontend `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

### Monitor Performance

- Check response times in Swagger docs
- Monitor error rates in logs
- Set up alerts for downtime

---

## Scaling Considerations

### Horizontal Scaling

**Railway/Render**: Use platform's scaling features

**Self-Hosted**: Use load balancer (Nginx) with multiple backend instances

### Database Scaling

**Neon**: Upgrade plan for more compute/storage

**Connection Pooling**: Already handled by SQLAlchemy

### Caching

**Redis** (optional for larger scale):
```bash
pip install redis
```

Add caching layer for frequently accessed data.

---

## Support

For deployment issues:
- Check [Troubleshooting](#troubleshooting) section
- Review application logs
- Test locally first: `uvicorn backend.main:app --reload`
- Check [Backend README](README.md) for configuration help

## Additional Resources

- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **Nginx Docs**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/getting-started/
- **Neon Docs**: https://neon.tech/docs
