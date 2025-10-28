# Copy Trading Monitor - Deployment Guide

## Local Development
```bash
./start_ui.sh
# Access at http://localhost:5000
```

## Hosting Options

### 1. Heroku (Recommended for beginners)
- Free tier available
- Easy deployment
- Built-in environment variable management

**Deploy to Heroku:**
```bash
# Install Heroku CLI first
heroku create your-app-name
heroku config:set API_KEY=your_api_key
heroku config:set CLIENT_ID=your_client_id
heroku config:set PASSWORD=your_password
heroku config:set TOTP_SECRET=your_totp_secret
heroku config:set SECRET_KEY=your_secret_key
git push heroku main
```

### 2. Railway
- Modern platform
- Great for Python apps
- Easy GitHub integration

**Deploy to Railway:**
1. Connect your GitHub repo to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on git push

### 3. Render
- Free tier available
- Great performance
- Simple deployment

**Deploy to Render:**
1. Connect GitHub repo
2. Choose "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python web_ui.py`
5. Add environment variables

### 4. DigitalOcean App Platform
- Reliable hosting
- Easy scaling
- Good documentation

### 5. Docker (Any cloud provider)
```bash
# Build image
docker build -t copy-trading-monitor .

# Run locally
docker run -p 5000:5000 --env-file .env copy-trading-monitor
```

## Environment Variables Required
- `API_KEY`: Your SmartAPI key
- `CLIENT_ID`: Your client ID
- `PASSWORD`: Your password
- `TOTP_SECRET`: Your TOTP secret
- `SECRET_KEY`: Your secret key
- `PORT`: (Optional) Port number (default: 5000)

## Security Notes
- Never commit `.env` file to git
- Use platform-specific environment variable management
- Consider using a private repository for sensitive trading logic