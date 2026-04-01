# AgentRoute Oracle - Deployment Guide

## Quick Deployment (5 minutes)

### Option 1: Deploy to Render.com (Recommended - Free tier available)

**Step 1: Create Render Account**
1. Go to https://render.com
2. Sign up with GitHub account
3. Verify email

**Step 2: Connect GitHub Repository**
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Select "Build and deploy from a Git repository"
4. Click "Connect account" and authorize GitHub
5. Select the `agentroute-oracle` repository

**Step 3: Configure Service**
1. **Name:** `agentroute-oracle`
2. **Runtime:** Python 3
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Plan:** Free (or Starter for better performance)
6. **Region:** Choose closest to you

**Step 4: Set Environment Variables**
In Render dashboard, add these environment variables:
```
SERVICE_NAME=AgentRoute Oracle
ENVIRONMENT=production
LOG_LEVEL=INFO
BASE_PRICE_SATS=10
MAX_PRICE_SATS=30
DYNAMIC_PRICING_ENABLED=true
MACAROON_KEY=prod-key-$(date +%s)
PREIMAGE_KEY=prod-preimage-$(date +%s)
```

**Step 5: Deploy**
1. Click "Create Web Service"
2. Wait for build to complete (~2-3 minutes)
3. Get your service URL: `https://agentroute-oracle.onrender.com`

**Step 6: Verify Deployment**
```bash
curl https://agentroute-oracle.onrender.com/health
```

---

### Option 2: Deploy to Fly.io

**Step 1: Install Fly CLI**
```bash
curl -L https://fly.io/install.sh | sh
```

**Step 2: Login to Fly**
```bash
fly auth login
```

**Step 3: Initialize Fly App**
```bash
cd /home/ubuntu/agentroute-oracle
fly launch
```

Follow prompts:
- App name: `agentroute-oracle`
- Region: Choose closest to you
- Postgres: No
- Redis: No

**Step 4: Deploy**
```bash
fly deploy
```

**Step 5: Get Your URL**
```bash
fly open
```

---

### Option 3: Deploy to Railway.app

**Step 1: Create Railway Account**
1. Go to https://railway.app
2. Sign up with GitHub

**Step 2: Create New Project**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Select `agentroute-oracle`

**Step 3: Configure**
1. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Add environment variables (same as Render)
3. Deploy

---

## Post-Deployment Steps

### 1. Test Your Live Service

```bash
# Replace with your actual URL
API_URL="https://agentroute-oracle.onrender.com"

# Test health check
curl $API_URL/health

# Test capabilities (agent discovery)
curl $API_URL/capabilities

# Test unauthenticated request (should return 402)
curl -X POST $API_URL/route \
  -H "Content-Type: application/json" \
  -d '{"amount_sats": 5000, "destination_pubkey": "03abc", "max_fee_rate": 0.1}'

# Test authenticated request
curl -X POST $API_URL/route \
  -H "Content-Type: application/json" \
  -H "Authorization: L402 dGVzdC1tYWNhcm9vbg== test-preimage" \
  -d '{"amount_sats": 5000, "destination_pubkey": "03abc", "max_fee_rate": 0.1}'
```

### 2. List on Agent Directories

#### ClawHub (https://clawhub.xyz)
1. Go to https://clawhub.xyz/add-service
2. Fill in:
   - **Name:** AgentRoute Oracle
   - **URL:** `https://agentroute-oracle.onrender.com`
   - **Description:** Lightning Network routing optimization service for AI agents
   - **Capabilities URL:** `https://agentroute-oracle.onrender.com/capabilities`
   - **OpenAPI URL:** `https://agentroute-oracle.onrender.com/openapi.json`
3. Submit

#### apinow.fun (https://apinow.fun)
1. Go to https://apinow.fun/submit
2. Provide service endpoint and metadata
3. Submit

### 3. Announce on X/Twitter

**Sample Post:**
```
🚀 AgentRoute Oracle is LIVE on Lightning ⚡

The first routing oracle for AI agents. Get optimal routes, pay in sats per query.

✅ L402-protected API
✅ Real-time routing data
✅ Passive recurring revenue

Integrate now: https://agentroute-oracle.onrender.com/capabilities

#AgentCommerce #L402 #Bitcoin #Lightning
```

### 4. Monitor Your Service

**Check Logs (Render):**
1. Go to https://dashboard.render.com
2. Select your service
3. Click "Logs" tab
4. View real-time logs

**Check Logs (Fly):**
```bash
fly logs
```

**Monitor Stats:**
```bash
curl https://agentroute-oracle.onrender.com/stats
```

---

## Custom Domain Setup (Optional)

### Add Custom Domain to Render

1. Go to your service in Render dashboard
2. Click "Settings" → "Custom Domains"
3. Add your domain (e.g., `api.agentroute.oracle`)
4. Update DNS records as shown

### Add Custom Domain to Fly

```bash
fly certs add api.agentroute.oracle
```

---

## Scaling & Performance

### Free Tier Limitations
- Render Free: 0.5 CPU, 512MB RAM, auto-sleeps after 15 min inactivity
- Fly Free: 3 shared-cpu-1x 256MB VMs

### Upgrade for Production
- **Render Starter:** $7/month - Always on, 1 CPU, 512MB RAM
- **Fly Starter:** $5/month - Dedicated CPU, 256MB RAM

### Load Testing
```bash
# Test with 100 concurrent requests
ab -n 100 -c 10 https://agentroute-oracle.onrender.com/health
```

---

## Troubleshooting

### Service Won't Start
**Check logs:**
```bash
# Render
curl https://dashboard.render.com/services/agentroute-oracle/logs

# Fly
fly logs
```

**Common issues:**
- Missing dependencies: Check `requirements.txt`
- Port binding: Ensure using `$PORT` environment variable
- Python version: Ensure Python 3.11+

### 402 Payment Required Not Working
- Check L402Handler in `main.py`
- Verify Authorization header format: `L402 <macaroon> <preimage>`
- Check logs for validation errors

### High Response Times
- Check CPU usage in dashboard
- Consider upgrading plan
- Optimize routing algorithm

### Service Sleeping (Render Free Tier)
- Upgrade to Starter plan
- Or set up external ping service to keep it awake

---

## Monitoring & Revenue Tracking

### Real-Time Stats
```bash
curl https://agentroute-oracle.onrender.com/stats
```

Response includes:
- `total_queries` - Number of queries processed
- `total_sats_earned` - Total satoshis earned
- `average_query_price_sats` - Average price per query
- `network_health` - Service health status

### Set Up Monitoring (Optional)
1. Use Render's built-in monitoring
2. Set up alerts for errors
3. Monitor uptime percentage

---

## Next Steps

1. ✅ Deploy service
2. ✅ Test all endpoints
3. ✅ List on agent directories
4. ✅ Announce on X
5. ⏭️ Integrate real LND node
6. ⏭️ Add revenue dashboard
7. ⏭️ Optimize routing algorithm

---

## Support

- **Documentation:** https://docs.agentroute.oracle
- **GitHub Issues:** https://github.com/agentroute/oracle/issues
- **Twitter:** https://x.com/agentroute

---

**Ready to earn sats? Deploy now!** 🚀⚡
