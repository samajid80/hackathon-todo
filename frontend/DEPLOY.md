# Frontend Deployment Guide

Comprehensive guide for deploying the Hackathon Todo Next.js frontend to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Options](#deployment-options)
  - [Option A: Vercel (Recommended)](#option-a-vercel-recommended)
  - [Option B: Netlify](#option-b-netlify)
  - [Option C: Self-Hosted (VPS)](#option-c-self-hosted-vps)
- [Environment Variables](#environment-variables)
- [Build and Optimization](#build-and-optimization)
- [Security Checklist](#security-checklist)
- [Monitoring and Analytics](#monitoring-and-analytics)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

1. **Node.js 24+** installed (for local builds)
2. **Backend API deployed** and accessible via HTTPS
3. **Git repository** with frontend code
4. **Domain name** (optional, for custom domain)
5. **Better-Auth configured** with production database

## Environment Setup

### 1. Prepare Production Environment Variables

Create production environment variables (set in deployment platform):

```env
# Backend API URL (MUST be HTTPS in production)
NEXT_PUBLIC_API_URL=https://api.your-domain.com

# Better Auth Secret (MUST match backend JWT_SECRET)
# Generate with: openssl rand -base64 32
BETTER_AUTH_SECRET=<same-as-backend-JWT_SECRET>

# Better Auth URL (Your frontend URL)
BETTER_AUTH_URL=https://your-domain.com

# Database URL for Better Auth (same as backend)
DATABASE_URL=postgresql://user:password@prod-host.neon.tech/dbname?sslmode=require
```

### 2. Verify Secret Match

**CRITICAL**: The `BETTER_AUTH_SECRET` MUST match backend `JWT_SECRET` exactly!

```bash
# Generate once and use in BOTH frontend and backend
openssl rand -base64 32
```

## Deployment Options

### Option A: Vercel (Recommended)

Vercel is the recommended platform for Next.js deployment with zero-config setup.

#### Step 1: Sign Up

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Install Vercel GitHub app

#### Step 2: Import Project

1. Click "Add New Project"
2. Import your GitHub repository
3. Select frontend directory (if monorepo)

#### Step 3: Configure Build Settings

Vercel auto-detects Next.js, but verify:

- **Framework Preset**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`
- **Node Version**: 24.x (set in project settings)

#### Step 4: Environment Variables

In Vercel dashboard → Settings → Environment Variables:

Add all production variables:
```
NEXT_PUBLIC_API_URL=https://api.your-domain.com
BETTER_AUTH_SECRET=<your-generated-secret>
BETTER_AUTH_URL=https://your-domain.vercel.app
DATABASE_URL=<neon-production-url>
```

**Important**:
- Variables starting with `NEXT_PUBLIC_` are exposed to the browser
- Other variables are server-side only

#### Step 5: Deploy

1. Click "Deploy"
2. Vercel builds and deploys automatically
3. Get deployment URL: `https://your-project.vercel.app`

#### Step 6: Custom Domain (Optional)

1. Go to Settings → Domains
2. Add your custom domain
3. Update DNS records:
   - **A Record**: Point to Vercel's IP
   - **CNAME**: Point to `cname.vercel-dns.com`
4. SSL certificate issued automatically

#### Step 7: Update Environment Variables

After custom domain is added:
```env
BETTER_AUTH_URL=https://your-domain.com
```

Redeploy for changes to take effect.

**Vercel Pricing**:
- **Hobby (Free)**: Perfect for personal projects
- **Pro ($20/month)**: Unlimited projects, team collaboration
- **Enterprise**: Custom pricing

---

### Option B: Netlify

Netlify offers similar features to Vercel with generous free tier.

#### Step 1: Sign Up

1. Go to [netlify.com](https://netlify.com)
2. Sign up with GitHub
3. Grant repository access

#### Step 2: Create New Site

1. Click "Add new site" → "Import an existing project"
2. Select GitHub repository
3. Choose branch to deploy (e.g., `main`)

#### Step 3: Build Settings

- **Build Command**: `npm run build`
- **Publish Directory**: `.next`
- **Base Directory**: `frontend` (if monorepo)

#### Step 4: Environment Variables

In Site Settings → Environment → Environment Variables:

Add production variables:
```
NEXT_PUBLIC_API_URL=https://api.your-domain.com
BETTER_AUTH_SECRET=<your-generated-secret>
BETTER_AUTH_URL=https://your-site.netlify.app
DATABASE_URL=<neon-production-url>
```

#### Step 5: Deploy

1. Click "Deploy site"
2. Netlify builds and deploys
3. Get URL: `https://your-site.netlify.app`

#### Step 6: Custom Domain

1. Go to Domain Settings
2. Add custom domain
3. Update DNS:
   - **CNAME**: Point to `your-site.netlify.app`
4. SSL certificate auto-issued

**Netlify Pricing**:
- **Free**: 100GB bandwidth, 300 build minutes
- **Pro ($19/month)**: Unlimited bandwidth, team features

---

### Option C: Self-Hosted (VPS)

Deploy on your own Ubuntu 22.04+ server.

#### Step 1: Server Setup

SSH into your server:
```bash
ssh user@your-server-ip
```

Update system:
```bash
sudo apt update && sudo apt upgrade -y
```

Install Node.js 24:
```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install nodejs -y
node -v  # Verify: v24.x
npm -v
```

Install PM2 (process manager):
```bash
sudo npm install -g pm2
```

#### Step 2: Clone Repository

```bash
cd /opt
sudo mkdir -p /opt/hackathon-todo
sudo chown $USER:$USER /opt/hackathon-todo
git clone https://github.com/your-repo/frontend.git /opt/hackathon-todo/frontend
cd /opt/hackathon-todo/frontend
```

#### Step 3: Install Dependencies

```bash
npm install
```

#### Step 4: Configure Environment Variables

Create production `.env.local`:
```bash
nano /opt/hackathon-todo/frontend/.env.local
```

Add production variables:
```env
NEXT_PUBLIC_API_URL=https://api.your-domain.com
BETTER_AUTH_SECRET=<your-generated-secret>
BETTER_AUTH_URL=https://your-frontend-domain.com
DATABASE_URL=postgresql://user:password@prod-host.neon.tech/dbname?sslmode=require
```

#### Step 5: Build Application

```bash
npm run build
```

Verify build output:
```bash
ls -la .next
```

#### Step 6: Start with PM2

```bash
pm2 start npm --name "hackathon-todo-frontend" -- start
pm2 save
pm2 startup  # Follow instructions to enable on boot
```

Check status:
```bash
pm2 status
pm2 logs hackathon-todo-frontend
```

#### Step 7: Configure Nginx

Create Nginx config:
```bash
sudo nano /etc/nginx/sites-available/hackathon-todo-frontend
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-frontend-domain.com www.your-frontend-domain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files caching
    location /_next/static {
        proxy_pass http://127.0.0.1:3000;
        proxy_cache_valid 200 60m;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # Image optimization
    location /_next/image {
        proxy_pass http://127.0.0.1:3000;
        proxy_cache_valid 200 60m;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/hackathon-todo-frontend /etc/nginx/sites-enabled/
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
sudo certbot --nginx -d your-frontend-domain.com -d www.your-frontend-domain.com
```

Verify auto-renewal:
```bash
sudo certbot renew --dry-run
```

#### Step 9: Update CSP for Production

Edit `next.config.js` and update CSP `connect-src`:
```javascript
connect-src 'self' https://api.your-domain.com;
```

Rebuild and restart:
```bash
npm run build
pm2 restart hackathon-todo-frontend
```

---

## Environment Variables

### Required Variables

| Variable | Example | Exposed to Browser | Description |
|----------|---------|-------------------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://api.example.com` | Yes | Backend API URL (MUST be HTTPS) |
| `BETTER_AUTH_SECRET` | `<openssl-generated>` | No | JWT secret (MUST match backend) |
| `DATABASE_URL` | `postgresql://...` | No | Neon PostgreSQL connection |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BETTER_AUTH_URL` | Auto-detected | Frontend URL for callbacks |
| `NODE_ENV` | `production` | Node environment |

### Setting Environment Variables

**Vercel/Netlify**: Use dashboard environment variables section

**Self-Hosted**: Add to `/opt/hackathon-todo/frontend/.env.local`

---

## Build and Optimization

### Local Build Test

Before deploying, test production build locally:

```bash
# Build
npm run build

# Start production server
npm start

# Test in browser
open http://localhost:3000
```

### Build Output Analysis

Check bundle sizes:
```bash
npm run build
```

Look for warnings:
- Large pages (>250KB)
- Unused dependencies
- Build errors

### Optimization Tips

1. **Image Optimization**:
   - Use Next.js `<Image>` component
   - Enable image optimization in `next.config.js`

2. **Code Splitting**:
   - Use dynamic imports for large components
   - Leverage Next.js automatic code splitting

3. **Caching**:
   - Static assets cached automatically by Next.js
   - API responses cached by browser (per backend headers)

4. **Performance Monitoring**:
   - Use Vercel Analytics (free on Vercel)
   - Use Google Lighthouse for audits

---

## Security Checklist

Before going live, verify:

- [ ] **NEXT_PUBLIC_API_URL uses HTTPS** (not HTTP)
- [ ] **BETTER_AUTH_SECRET matches backend JWT_SECRET** exactly
- [ ] **DATABASE_URL uses production database** (not dev/test)
- [ ] **CSP headers configured** in `next.config.js`
- [ ] **API domain whitelisted** in CSP `connect-src`
- [ ] **.env.local NOT committed** to git (check `.gitignore`)
- [ ] **Security headers enabled** (X-Frame-Options, etc.)
- [ ] **HTTPS enabled** (SSL certificate installed)
- [ ] **No secrets in client-side code** (only `NEXT_PUBLIC_*` exposed)
- [ ] **Build completes without errors**
- [ ] **All API calls use HTTPS**
- [ ] **Error boundaries implemented** for production errors

### Update CSP for Production

In `next.config.js`, update `connect-src` directive:

```javascript
const cspHeader = `
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://api.your-domain.com;  // UPDATE THIS
  object-src 'none';
  frame-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
`;
```

---

## Monitoring and Analytics

### Vercel Analytics (Recommended)

If using Vercel, enable analytics:

1. Go to Analytics tab in dashboard
2. Click "Enable Analytics"
3. View real-time performance metrics

### Google Analytics (Optional)

Add to `app/layout.tsx`:

```typescript
import Script from 'next/script';

export default function RootLayout({ children }) {
  return (
    <html>
      <head>
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'GA_MEASUREMENT_ID');
          `}
        </Script>
      </head>
      <body>{children}</body>
    </html>
  );
}
```

### Error Tracking with Sentry (Optional)

```bash
npm install @sentry/nextjs
```

Initialize:
```bash
npx @sentry/wizard -i nextjs
```

### Uptime Monitoring

Monitor frontend availability:
- **UptimeRobot**: Free tier available
- **Pingdom**: Paid service
- **Better Uptime**: Free tier available

Monitor URL: `https://your-domain.com`

---

## Troubleshooting

### Issue: Build fails

**Check logs**:
```bash
npm run build
```

**Common causes**:
- TypeScript errors
- Missing dependencies
- Environment variables not set
- Import errors

**Solution**:
```bash
# Check TypeScript
npm run type-check

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check environment variables
cat .env.local
```

### Issue: "Cannot connect to backend API"

**Symptoms**: API calls fail in production

**Check**:
1. `NEXT_PUBLIC_API_URL` is HTTPS (not HTTP)
2. Backend is deployed and accessible
3. CORS is configured on backend

**Test backend**:
```bash
curl https://api.your-domain.com/health
```

**Solution**:
- Update `NEXT_PUBLIC_API_URL` to correct backend URL
- Add frontend domain to backend `CORS_ORIGINS`
- Redeploy frontend after env var change

### Issue: Authentication not working

**Symptoms**: Users can't log in

**Check**:
1. `BETTER_AUTH_SECRET` matches backend `JWT_SECRET`
2. Secrets are case-sensitive and exact match

**Solution**:
```bash
# Generate new secret
openssl rand -base64 32

# Update BOTH:
# - Frontend: BETTER_AUTH_SECRET
# - Backend: JWT_SECRET

# Redeploy both frontend and backend
```

### Issue: CSP violations in browser console

**Symptoms**: Resources blocked by CSP

**Check browser console**:
```
Refused to connect to 'https://...' because it violates the following Content Security Policy directive: "connect-src 'self'"
```

**Solution**:
1. Identify blocked resource domain
2. Update CSP in `next.config.js`
3. Add domain to appropriate directive (`connect-src`, `script-src`, etc.)
4. Rebuild and redeploy

### Issue: Environment variables not loading

**Symptoms**: `process.env.NEXT_PUBLIC_API_URL` is undefined

**Common causes**:
- Variable name doesn't start with `NEXT_PUBLIC_`
- Server not restarted after env change
- `.env.local` not in correct directory

**Solution**:
```bash
# Check file exists
ls -la .env.local

# Verify variable names
cat .env.local | grep NEXT_PUBLIC

# Restart dev server
npm run dev

# For production, rebuild
npm run build
```

### Issue: Slow page loads

**Check**:
1. Bundle size (run `npm run build`)
2. API response times
3. Image optimization

**Solution**:
- Enable Next.js image optimization
- Use dynamic imports for large components
- Enable caching headers
- Optimize images (use WebP format)
- Consider CDN for static assets

### Issue: PM2 service crashes (Self-Hosted)

**Check logs**:
```bash
pm2 logs hackathon-todo-frontend
```

**Common causes**:
- Port 3000 already in use
- Out of memory
- Environment variables missing

**Solution**:
```bash
# Restart service
pm2 restart hackathon-todo-frontend

# Check status
pm2 status

# Change port if needed
pm2 start npm --name "hackathon-todo-frontend" -- start -- -p 3001
```

---

## Post-Deployment

### Test Deployment

1. **Visit deployed URL**: `https://your-domain.com`
2. **Test authentication**: Sign up and log in
3. **Create tasks**: Test all CRUD operations
4. **Check browser console**: No errors
5. **Test on mobile**: Responsive design works
6. **Check CSP**: No violations in console

### Update Backend CORS

Add frontend domain to backend `CORS_ORIGINS`:
```env
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

Redeploy backend.

### Performance Audit

Run Lighthouse audit:
1. Open Chrome DevTools
2. Go to Lighthouse tab
3. Run audit (Performance, Accessibility, SEO)
4. Fix any issues

Target scores:
- Performance: 90+
- Accessibility: 95+
- SEO: 95+
- Best Practices: 95+

### Monitor for Errors

Check for errors in:
- Browser console (client-side errors)
- Vercel/deployment logs (server-side errors)
- Backend API logs (API errors)

---

## Continuous Deployment

### Automatic Deploys (Vercel/Netlify)

Both platforms support automatic deployment:

1. **Push to Git**: Push code to `main` branch
2. **Auto-build**: Platform detects changes and builds
3. **Auto-deploy**: Deployed automatically on success
4. **Rollback**: Revert to previous deployment if needed

### Preview Deployments

**Vercel/Netlify**: Create preview for every pull request

1. Create feature branch
2. Push to GitHub
3. Platform builds preview
4. Test preview URL
5. Merge when ready

---

## Scaling Considerations

### CDN

**Vercel**: Automatic edge network (CDN) included

**Netlify**: Automatic CDN included

**Self-Hosted**: Use Cloudflare for CDN

### Load Balancing

For high traffic, use multiple frontend instances behind load balancer.

---

## Support

For deployment issues:
- Check [Troubleshooting](#troubleshooting) section
- Review build logs
- Test locally first: `npm run build && npm start`
- Check [Frontend README](README.md) for configuration

## Additional Resources

- **Next.js Deployment**: https://nextjs.org/docs/deployment
- **Vercel Docs**: https://vercel.com/docs
- **Netlify Docs**: https://docs.netlify.com
- **PM2 Docs**: https://pm2.keymetrics.io/docs/usage/quick-start/
- **CSP Generator**: https://report-uri.com/home/generate
