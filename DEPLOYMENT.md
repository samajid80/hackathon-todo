# Full-Stack Deployment Guide: Railway + Vercel

Complete guide for deploying the Hackathon Todo application with backend on Railway and frontend on Vercel.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [Step 1: Database Setup (Neon PostgreSQL)](#step-1-database-setup-neon-postgresql)
- [Step 2: Backend Deployment (Railway)](#step-2-backend-deployment-railway)
- [Step 3: Frontend Deployment (Vercel)](#step-3-frontend-deployment-vercel)
- [Step 4: Integration & Testing](#step-4-integration--testing)
- [Environment Variables Reference](#environment-variables-reference)
- [Security Checklist](#security-checklist)
- [Troubleshooting](#troubleshooting)
- [Monitoring & Maintenance](#monitoring--maintenance)

## Overview

This guide will help you deploy:
- **Backend (FastAPI + Python 3.13)** → Railway
- **Frontend (Next.js 16 + React 19)** → Vercel
- **Database (PostgreSQL)** → Neon (cloud-hosted)

**Estimated Time**: 30-45 minutes

**Costs**:
- Railway: $5/month free credits (sufficient for small projects)
- Vercel: Free tier (Hobby plan)
- Neon: Free tier (0.5GB storage, sufficient for development)

## Prerequisites

Before starting, ensure you have:

- [ ] GitHub account (for repository access)
- [ ] Railway account ([railway.app](https://railway.app))
- [ ] Vercel account ([vercel.com](https://vercel.com))
- [ ] Neon account ([neon.tech](https://neon.tech))
- [ ] Domain name (optional, for custom domains)
- [ ] Git repository with your code pushed to GitHub

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│             │         │              │         │             │
│   Vercel    │ ──────► │   Railway    │ ──────► │    Neon     │
│  (Frontend) │  HTTPS  │  (Backend)   │   SQL   │ (Database)  │
│             │         │              │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
     Next.js                 FastAPI              PostgreSQL
```

**Data Flow**:
1. User accesses frontend (Vercel) via HTTPS
2. Frontend calls backend API (Railway) via HTTPS
3. Backend connects to PostgreSQL (Neon) via SSL
4. Better-Auth manages authentication with JWT tokens

**Key Integration Points**:
- `JWT_SECRET` (backend) must match `BETTER_AUTH_SECRET` (frontend)
- Backend `CORS_ORIGINS` must include frontend URL
- Frontend `NEXT_PUBLIC_API_URL` must point to backend URL

## Step 1: Database Setup (Neon PostgreSQL)

### 1.1 Create Neon Project

1. Go to [neon.tech](https://neon.tech) and sign up/login
2. Click "Create Project"
3. Configure:
   - **Name**: `hackathon-todo-prod`
   - **Region**: Choose closest to your users
   - **PostgreSQL Version**: 15 or latest
4. Click "Create Project"

### 1.2 Create Production Database

1. In Neon dashboard, click "Databases"
2. Create new database:
   - **Name**: `hackathon_todo_prod`
3. Copy the connection string:
   ```
   postgresql://user:password@ep-xxx.region.neon.tech/hackathon_todo_prod?sslmode=require
   ```
4. Save this URL - you'll need it for both backend and frontend

### 1.3 Run Database Migrations

Clone your repository locally if not already:
```bash
git clone https://github.com/your-username/hackathon-todo.git
cd hackathon-todo
```

Run migrations using psql:
```bash
# Set DATABASE_URL temporarily
export DATABASE_URL="postgresql://user:password@ep-xxx.region.neon.tech/hackathon_todo_prod?sslmode=require"

# Run migrations
psql "$DATABASE_URL" < backend/migrations/000_create_users_table.sql
psql "$DATABASE_URL" < backend/migrations/001_create_tasks_table.sql
psql "$DATABASE_URL" < backend/migrations/002_updated_at_trigger.sql
```

Verify tables were created:
```bash
psql "$DATABASE_URL" -c "\dt"
```

Expected output:
```
            List of relations
 Schema |  Name  | Type  |    Owner
--------+--------+-------+-------------
 public | tasks  | table | your_user
 public | users  | table | your_user
```

## Step 2: Backend Deployment (Railway)

### 2.1 Sign Up and Create Project

1. Go to [railway.app](https://railway.app)
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your GitHub
4. Click "New Project"
5. Select "Deploy from GitHub repo"
6. Choose your repository (e.g., `hackathon-todo`)

### 2.2 Configure Service

Railway will auto-detect your Python application.

**IMPORTANT - Root Directory Configuration:**

You have two options for configuring the root directory:

**Option A: Deploy Entire Repository (Recommended) ⭐**
- **Root Directory**: Leave empty or set to `/`
- **Why?**: Your code imports use `backend.` prefix (e.g., `from backend.auth...`)
- **Advantage**: Same code works for local development and production
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

**Option B: Deploy Backend Folder Only**
- **Root Directory**: Set to `/backend`
- **Requirement**: Must change imports in `main.py` from `from backend.auth...` to `from auth...`
- **Disadvantage**: Different code for local vs production
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**We recommend Option A** to keep your codebase consistent across environments.

**Service Name**: `hackathon-todo-api` (or your preference)

### 2.3 Generate JWT Secret

Open your terminal and generate a secure secret:

```bash
openssl rand -base64 32
```

**IMPORTANT**: Copy this value! You'll use it for both backend and frontend.

Example output:
```
YourSecretKey123456789abcdefghijklmnop=
```

### 2.4 Configure Environment Variables

In Railway dashboard:
1. Go to your service → Click "Variables" tab
2. Click "Add Variable" for each:

```env
DATABASE_URL=postgresql://user:password@ep-xxx.region.neon.tech/hackathon_todo_prod?sslmode=require
JWT_SECRET=YourSecretKey123456789abcdefghijklmnop=
JWT_ALGORITHM=HS256
CORS_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
```

**Notes**:
- `DATABASE_URL`: Use the Neon connection string from Step 1.2
- `JWT_SECRET`: Use the secret generated in Step 2.3
- `CORS_ORIGINS`: We'll update this after deploying frontend (Step 3)
- For multiple frontend URLs, use comma-separated: `https://app.vercel.app,https://custom-domain.com`

### 2.5 Configure Build Settings

Railway should auto-detect Python, but verify the commands match your chosen root directory option:

**If using Option A (Entire Repository - Recommended):**

1. Click "Settings" tab
2. Check **Build**:
   - **Root Directory**: (empty) or `/`
   - **Build Command**: `pip install -e ./backend`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

**If using Option B (Backend Folder Only):**

1. Click "Settings" tab
2. Check **Build**:
   - **Root Directory**: `/backend`
   - **Build Command**: `pip install -e .`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Note**: Remember to change imports in `main.py` first!

If settings are not correct, click "Edit" and update them.

### 2.6 Deploy Backend

1. Click "Deploy" (or it may auto-deploy)
2. Wait for build to complete (2-5 minutes)
3. Check "Deployments" tab for status

Once deployed:
1. Click "Settings" → "Networking"
2. Click "Generate Domain" to get a public URL
3. Copy the URL: `https://hackathon-todo-api-production.up.railway.app`

### 2.7 Verify Backend Deployment

Test the API health endpoint:
```bash
curl https://your-backend-url.railway.app/health
```

Expected response:
```json
{"status": "healthy"}
```

Visit the API documentation:
```
https://your-backend-url.railway.app/docs
```

You should see the Swagger UI with all endpoints.

## Step 3: Frontend Deployment (Vercel)

### 3.1 Sign Up and Import Project

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up" → "Continue with GitHub"
3. Authorize Vercel to access your GitHub
4. Click "Add New Project"
5. Import your repository (e.g., `hackathon-todo`)

### 3.2 Configure Project

1. **Framework Preset**: Next.js (auto-detected)
2. **Root Directory**:
   - If monorepo: Select `frontend`
   - If separate repo: Leave as `.`
3. **Build Settings** (auto-detected):
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

### 3.3 Configure Environment Variables

In the import screen, expand "Environment Variables" section and add:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
BETTER_AUTH_SECRET=YourSecretKey123456789abcdefghijklmnop=
DATABASE_URL=postgresql://user:password@ep-xxx.region.neon.tech/hackathon_todo_prod?sslmode=require
```

**CRITICAL**:
- `NEXT_PUBLIC_API_URL`: Use the Railway backend URL from Step 2.6
- `BETTER_AUTH_SECRET`: Use the **SAME** secret as backend `JWT_SECRET` (from Step 2.3)
- `DATABASE_URL`: Use the same Neon URL as backend

### 3.4 Deploy Frontend

1. Click "Deploy"
2. Wait for build to complete (3-7 minutes)
3. Once deployed, you'll get a URL: `https://your-project.vercel.app`

### 3.5 Update BETTER_AUTH_URL

After first deployment:

1. Go to Vercel dashboard → Your project
2. Click "Settings" → "Environment Variables"
3. Add/update:
   ```env
   BETTER_AUTH_URL=https://your-project.vercel.app
   ```
4. Click "Save"
5. Redeploy: Go to "Deployments" → Click "..." → "Redeploy"

### 3.6 Custom Domain (Optional)

If you have a custom domain:

1. Go to "Settings" → "Domains"
2. Click "Add"
3. Enter your domain (e.g., `app.yourdomain.com`)
4. Follow DNS configuration instructions:
   - **A Record**: Point to Vercel IP
   - **CNAME**: Point to `cname.vercel-dns.com`
5. Wait for DNS propagation (5-60 minutes)
6. SSL certificate issued automatically

After custom domain is active, update environment variables:
```env
BETTER_AUTH_URL=https://app.yourdomain.com
```

Then redeploy.

## Step 4: Integration & Testing

### 4.1 Update Backend CORS

Now that frontend is deployed, update backend CORS settings:

1. Go to Railway dashboard → Your service
2. Click "Variables" tab
3. Update `CORS_ORIGINS`:
   ```env
   CORS_ORIGINS=https://your-project.vercel.app,https://www.your-project.vercel.app
   ```

   If using custom domain:
   ```env
   CORS_ORIGINS=https://app.yourdomain.com,https://www.app.yourdomain.com
   ```

4. Railway will auto-redeploy with new variables

### 4.2 Update Frontend CSP Headers

If using custom backend domain, update CSP in `frontend/next.config.js`:

Find the CSP configuration and update `connect-src`:
```javascript
const cspHeader = `
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://your-backend-url.railway.app;
  object-src 'none';
  frame-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
`;
```

Commit and push changes:
```bash
git add frontend/next.config.js
git commit -m "Update CSP for production backend"
git push
```

Vercel will auto-deploy.

### 4.3 Test Full Application

1. **Visit Frontend**: `https://your-project.vercel.app`
2. **Sign Up**: Create a new account
3. **Verify**:
   - Check browser console (F12) - no errors
   - Account created successfully
4. **Log In**: Use credentials you just created
5. **Create Task**: Add a new task
6. **CRUD Operations**: Test Create, Read, Update, Delete
7. **Log Out**: Verify logout works
8. **Log In Again**: Verify persistence

### 4.4 Verify Database

Check that data is being saved:

```bash
# Connect to production database
psql "$DATABASE_URL"

# Check users
SELECT id, email, created_at FROM users;

# Check tasks
SELECT id, title, status, user_id FROM tasks LIMIT 10;

# Exit
\q
```

### 4.5 Test API Endpoints

Use Swagger UI to test API:
```
https://your-backend-url.railway.app/docs
```

1. Click "Authorize" button
2. Get JWT token:
   - Log in via frontend
   - Open browser DevTools → Application → Cookies
   - Copy `better-auth.session_token` value
3. Enter token in Swagger UI: `Bearer <token>`
4. Test endpoints (GET /api/tasks, POST /api/tasks, etc.)

### 4.6 Browser Console Check

Open browser console (F12) and check:
- [ ] No CORS errors
- [ ] No CSP violations
- [ ] No authentication errors
- [ ] API calls return 200 status codes

## Environment Variables Reference

### Backend (Railway)

| Variable | Value | Required | Notes |
|----------|-------|----------|-------|
| `DATABASE_URL` | `postgresql://...` | Yes | Neon PostgreSQL connection string |
| `JWT_SECRET` | `<32+ char random>` | Yes | MUST match frontend `BETTER_AUTH_SECRET` |
| `JWT_ALGORITHM` | `HS256` | Yes | Default algorithm |
| `CORS_ORIGINS` | `https://app.vercel.app` | Yes | Frontend URL(s), comma-separated |
| `ENVIRONMENT` | `production` | No | Environment name |

### Frontend (Vercel)

| Variable | Value | Required | Exposed to Browser | Notes |
|----------|-------|----------|-------------------|-------|
| `NEXT_PUBLIC_API_URL` | `https://api.railway.app` | Yes | Yes | Backend API URL (MUST be HTTPS) |
| `BETTER_AUTH_SECRET` | `<same as JWT_SECRET>` | Yes | No | MUST match backend `JWT_SECRET` |
| `BETTER_AUTH_URL` | `https://app.vercel.app` | Yes | No | Frontend URL |
| `DATABASE_URL` | `postgresql://...` | Yes | No | Same as backend |

## Security Checklist

Before going live, verify all security measures:

### Secrets & Authentication
- [ ] `JWT_SECRET` is randomly generated (32+ characters)
- [ ] `BETTER_AUTH_SECRET` matches `JWT_SECRET` exactly
- [ ] Secrets are different from development environment
- [ ] `.env` and `.env.local` NOT committed to git

### HTTPS & SSL
- [ ] Backend uses HTTPS (Railway provides automatically)
- [ ] Frontend uses HTTPS (Vercel provides automatically)
- [ ] Database connection uses `?sslmode=require`
- [ ] All API calls from frontend use HTTPS

### CORS & CSP
- [ ] `CORS_ORIGINS` restricted to frontend domain only
- [ ] No wildcard (`*`) in CORS origins
- [ ] CSP headers configured in `next.config.js`
- [ ] Backend API domain whitelisted in CSP `connect-src`

### Database
- [ ] Using production database (not dev/test)
- [ ] Database backups enabled (Neon auto-backup)
- [ ] Database connection pooling enabled (SQLAlchemy default)

### Application Security
- [ ] Rate limiting active (default: 100 req/hour per user)
- [ ] Security headers enabled (X-Frame-Options, X-Content-Type-Options, etc.)
- [ ] Input validation active (Pydantic models)
- [ ] Error messages don't expose sensitive info

### Monitoring
- [ ] Health check endpoint works (`/health`)
- [ ] Logging configured (Railway/Vercel dashboards)
- [ ] Error tracking setup (optional: Sentry)
- [ ] Uptime monitoring setup (optional: UptimeRobot)

## Troubleshooting

### Issue: "Cannot connect to backend API"

**Symptoms**: Frontend can't reach backend, API calls fail

**Check**:
```bash
# Test backend health
curl https://your-backend-url.railway.app/health

# Check browser console for CORS errors
```

**Solutions**:
1. Verify `NEXT_PUBLIC_API_URL` is correct and uses HTTPS
2. Check `CORS_ORIGINS` in backend includes frontend URL
3. Ensure backend is deployed and running (check Railway logs)
4. Test backend directly in browser: `https://backend-url/docs`

### Issue: "Authentication failed" / "Invalid token"

**Symptoms**: Can't log in, JWT validation fails

**Check**:
```bash
# Verify secrets match
# Backend Railway: Check JWT_SECRET value
# Frontend Vercel: Check BETTER_AUTH_SECRET value
```

**Solutions**:
1. Ensure `JWT_SECRET` (backend) = `BETTER_AUTH_SECRET` (frontend)
2. Secrets are case-sensitive - must match exactly
3. Regenerate secret and update both:
   ```bash
   openssl rand -base64 32
   ```
4. Redeploy both backend and frontend after updating

### Issue: CORS Errors

**Symptoms**: Browser console shows:
```
Access to fetch at 'https://backend...' from origin 'https://frontend...'
has been blocked by CORS policy
```

**Solutions**:
1. Add frontend URL to backend `CORS_ORIGINS`:
   ```env
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```
2. Use exact URL (include https://)
3. For multiple domains, comma-separate:
   ```env
   CORS_ORIGINS=https://app.vercel.app,https://custom-domain.com
   ```
4. Redeploy backend (Railway auto-redeploys on env var change)

### Issue: CSP Violations

**Symptoms**: Browser console shows:
```
Refused to connect to 'https://...' because it violates CSP directive
```

**Solutions**:
1. Update `next.config.js` CSP `connect-src`:
   ```javascript
   connect-src 'self' https://your-backend-url.railway.app;
   ```
2. Commit and push changes
3. Vercel will auto-deploy

### Issue: Database Connection Failed

**Symptoms**: Backend logs show database connection errors

**Check**:
```bash
# Test database connection
psql "$DATABASE_URL" -c "SELECT 1"
```

**Solutions**:
1. Verify `DATABASE_URL` is correct (check Neon dashboard)
2. Ensure URL includes `?sslmode=require`
3. Check Neon database is active (not paused on free tier)
4. Verify database exists:
   ```bash
   psql "$DATABASE_URL" -c "\l"
   ```

### Issue: Build Failures

**Backend (Railway)**:
```bash
# Check Railway logs for error messages
# Common issues:
# - Missing dependencies in pyproject.toml
# - Python version mismatch
# - Import errors
```

**Solutions**:
1. Verify `pyproject.toml` includes all dependencies
2. Check Python version (should be 3.13+)
3. Test build locally:
   ```bash
   cd backend
   pip install -e .
   ```

### Issue: Import Error - "attempted relative import beyond top-level package"

**Symptoms**: Railway build fails with:
```
ImportError: attempted relative import beyond top-level package
```

**Cause**: Mismatch between Railway root directory and import statements in code.

**Solution**:

Your imports in `backend/main.py` use absolute imports:
```python
from backend.auth.rate_limiter import RateLimitMiddleware
from backend.db import create_db_and_tables
from backend.routes import tasks
```

These require Railway to be configured as follows:

**Railway Settings**:
- **Root Directory**: Leave empty (or set to `/`)
- **Build Command**: `pip install -e ./backend`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

**Alternative**: If you want to use root directory `/backend`, you must:
1. Change imports to relative (remove `backend.` prefix)
2. Update start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Note: This creates inconsistency with local development

**Recommended**: Keep absolute imports and deploy the entire repository (see Section 2.2)

**Frontend (Vercel)**:
```bash
# Check Vercel build logs
# Common issues:
# - TypeScript errors
# - Missing environment variables
# - Import errors
```

**Solutions**:
1. Run type check locally:
   ```bash
   cd frontend
   npm run type-check
   ```
2. Test build locally:
   ```bash
   npm run build
   ```
3. Check all environment variables are set in Vercel

### Issue: "Rate limit exceeded"

**Symptoms**: API returns 429 status code

**Check**:
```bash
# Check backend rate limiting configuration
# Default: 100 requests/hour per user
```

**Solutions**:
1. This is expected security behavior
2. Wait for rate limit window to reset (check `Retry-After` header)
3. For testing, temporarily increase limits in `backend/auth/rate_limiter.py`
4. For production, consider upgrading rate limits based on usage

## Monitoring & Maintenance

### Health Checks

**Backend Health**:
```bash
curl https://your-backend-url.railway.app/health
```

**Frontend Health**:
```bash
curl -I https://your-frontend.vercel.app
```

### View Logs

**Railway (Backend)**:
1. Go to Railway dashboard
2. Select your service
3. Click "Deployments" tab
4. Click on latest deployment
5. View real-time logs

**Vercel (Frontend)**:
1. Go to Vercel dashboard
2. Select your project
3. Click "Deployments" tab
4. Click on deployment
5. Click "Runtime Logs"

### Monitor Performance

**Vercel Analytics** (Recommended):
1. Go to your project in Vercel
2. Click "Analytics" tab
3. View performance metrics (free on Hobby plan)

**Railway Metrics**:
1. Go to your service in Railway
2. Click "Metrics" tab
3. View CPU, memory, network usage

### Uptime Monitoring

Set up external monitoring with:
- **UptimeRobot**: https://uptimerobot.com (free tier)
- **Better Uptime**: https://betteruptime.com (free tier)

Monitor endpoints:
- Backend: `https://your-backend-url.railway.app/health`
- Frontend: `https://your-frontend.vercel.app`

### Database Backups

**Neon Automatic Backups**:
1. Go to Neon dashboard
2. Click your project
3. Go to "Backups" tab
4. Enable automatic backups (available on paid tiers)

**Manual Backup**:
```bash
# Create backup
pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql "$DATABASE_URL" < backup_20251217_120000.sql
```

### Updating Deployments

**Backend (Railway)**:
1. Push changes to GitHub
2. Railway auto-detects and deploys
3. Monitor deployment in Railway dashboard

**Frontend (Vercel)**:
1. Push changes to GitHub
2. Vercel auto-detects and deploys
3. Monitor deployment in Vercel dashboard

**Manual Redeploy**:
- Railway: Click "Redeploy" in deployments tab
- Vercel: Click "..." → "Redeploy" in deployments tab

### Rollback Deployment

**Railway**:
1. Go to "Deployments" tab
2. Find previous successful deployment
3. Click "..." → "Redeploy"

**Vercel**:
1. Go to "Deployments" tab
2. Find previous deployment
3. Click "..." → "Promote to Production"

## Cost Optimization

### Free Tier Limits

**Railway**:
- $5/month free credits
- Suitable for development and small projects
- Upgrade to $20/month for production

**Vercel**:
- Hobby plan: Free
- 100GB bandwidth per month
- Unlimited deployments
- Sufficient for small to medium projects

**Neon**:
- Free tier: 0.5GB storage
- Auto-suspend after inactivity
- Suitable for development
- Upgrade to $19/month for always-on production

### Monitor Usage

Check usage regularly:
- Railway: Dashboard → Billing
- Vercel: Dashboard → Usage
- Neon: Dashboard → Usage

## Next Steps

After successful deployment:

1. **Custom Domain**: Add custom domain to both frontend and backend
2. **Analytics**: Enable Vercel Analytics for performance monitoring
3. **Error Tracking**: Add Sentry for error tracking
4. **Performance**: Run Lighthouse audit and optimize
5. **SEO**: Add meta tags and sitemap
6. **Monitoring**: Set up uptime monitoring
7. **Backups**: Enable automatic database backups
8. **CI/CD**: Configure automated testing before deployment

## Additional Resources

### Documentation
- **Railway**: https://docs.railway.app
- **Vercel**: https://vercel.com/docs
- **Neon**: https://neon.tech/docs
- **Better-Auth**: https://www.better-auth.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Next.js**: https://nextjs.org/docs

### Project Documentation
- [Backend README](backend/README.md) - Local development setup
- [Frontend README](frontend/README.md) - Frontend configuration
- [Backend Deployment Guide](backend/DEPLOY.md) - Detailed backend deployment options
- [Frontend Deployment Guide](frontend/DEPLOY.md) - Detailed frontend deployment options
- [API Documentation](API_DOCUMENTATION.md) - API endpoints and examples

### Support
- Railway: Discord community (https://discord.gg/railway)
- Vercel: Discord community (https://vercel.com/discord)
- GitHub Issues: Report bugs and issues

## Summary

You've successfully deployed your full-stack application! 🎉

**What you've accomplished**:
- ✅ PostgreSQL database on Neon (cloud-hosted)
- ✅ FastAPI backend on Railway (with automatic HTTPS)
- ✅ Next.js frontend on Vercel (with edge network)
- ✅ Secure JWT authentication between frontend and backend
- ✅ CORS and CSP configured for security
- ✅ Production environment variables set
- ✅ Automatic deployments on git push

**Your URLs**:
- Frontend: `https://your-project.vercel.app`
- Backend API: `https://your-backend-url.railway.app`
- API Docs: `https://your-backend-url.railway.app/docs`

**Next deployment**: Just push to GitHub - both platforms auto-deploy!

```bash
git add .
git commit -m "Your changes"
git push
```

Happy deploying! 🚀
