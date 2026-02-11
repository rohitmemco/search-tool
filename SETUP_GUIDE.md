# PriceNexus Local Setup Guide

This guide will help you run the PriceNexus application on your local machine.

## Prerequisites

Before starting, ensure you have installed:
- **Python 3.9+** - [Download here](https://www.python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **MongoDB** - [Download here](https://www.mongodb.com/try/download/community)

## Step 1: Install MongoDB

1. Download and install MongoDB Community Edition
2. Start MongoDB service:
   - **Windows**: MongoDB should start automatically as a service
   - **Mac/Linux**: Run `mongosh` to start MongoDB

Verify MongoDB is running by opening a terminal and typing:
```bash
mongosh
```

If it connects, MongoDB is running! Type `exit` to close.

## Step 2: Setup API Keys

You need to get API keys for the application to work:

### Required APIs:
1. **SerpAPI** (for product search) - [Get free key here](https://serpapi.com/users/sign_up)
   - Free tier: 100 searches/month
   
2. **Emergent LLM API** (for AI features) - [Get key here](https://emergentagi.com/)
   - Used for intelligent product detection

3. **Foursquare API** (for local stores) - [Get free key here](https://foursquare.com/developers/signup)
   - Free tier: 100,000 calls/month

### Configure API Keys:

1. Open `backend/.env` file
2. Replace the placeholder values with your actual API keys:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=pricenexus

SERPAPI_API_KEY=your_actual_serpapi_key
FOURSQUARE_API_KEY=your_actual_foursquare_key
EMERGENT_LLM_KEY=your_actual_emergent_key
```

## Step 3: Setup Backend (Python/FastAPI)

Open a terminal in the project root directory:

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python server.py
```

Or using uvicorn directly:
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

The backend should start at: **http://localhost:8000**

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Setup Frontend (React)

Open a **NEW terminal** window (keep the backend running):

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies (first time only)
npm install

# Start the development server
npm start
```

The frontend should automatically open in your browser at: **http://localhost:3000**

## Step 5: Test the Application

1. Open your browser to http://localhost:3000
2. Type a product name in the search bar (e.g., "iPhone 15")
3. Click Search
4. You should see price results!

## Troubleshooting

### Backend Won't Start

**Error: "ImportError: No module named 'fastapi'"**
- Solution: Run `pip install -r requirements.txt` in the backend directory

**Error: "MongoDB connection failed"**
- Solution: Make sure MongoDB is running. Start it with:
  - Windows: Open Services → Start MongoDB
  - Mac: `brew services start mongodb-community`
  - Linux: `sudo systemctl start mongod`

**Error: "SerpAPI quota exceeded"**
- Solution: The app will work with estimated prices when API quota is reached

### Frontend Won't Start

**Error: "command not found: npm"**
- Solution: Install Node.js from https://nodejs.org/

**Error: "Port 3000 is already in use"**
- Solution: Kill the process using port 3000 or use a different port:
  ```bash
  PORT=3001 npm start
  ```

**Error: "Failed to compile"**
- Solution: Delete `node_modules` folder and reinstall:
  ```bash
  rm -rf node_modules
  npm install
  ```

### MongoDB Issues

**Error: "Connection refused on port 27017"**
- Solution: Start MongoDB service:
  - Windows: Services → MongoDB → Start
  - Mac: `brew services start mongodb-community`
  - Linux: `sudo systemctl start mongod`

**MongoDB not installed**
- Download from: https://www.mongodb.com/try/download/community
- Or use Docker: `docker run -d -p 27017:27017 mongo`

## Running Without API Keys (Limited Mode)

If you don't have API keys yet, the app will work with:
- Estimated prices (category-based)
- Mock vendor data
- Basic search functionality

To enable full features, you need:
- ✅ SerpAPI key - For real Google Shopping prices
- ✅ Emergent LLM key - For AI product detection
- ⚠️  Foursquare key - Optional, for local store search

## Quick Start Script

Save this as `start.bat` (Windows) or `start.sh` (Mac/Linux):

**Windows (start.bat):**
```batch
@echo off
echo Starting MongoDB...
net start MongoDB

echo Starting Backend...
start cmd /k "cd backend && python server.py"

timeout /t 5

echo Starting Frontend...
cd frontend
npm start
```

**Mac/Linux (start.sh):**
```bash
#!/bin/bash
echo "Starting MongoDB..."
brew services start mongodb-community

echo "Starting Backend..."
cd backend
python server.py &

sleep 5

echo "Starting Frontend..."
cd frontend
npm start
```

Make it executable:
```bash
chmod +x start.sh
./start.sh
```

## Development Tips

- Backend changes automatically reload (with uvicorn --reload)
- Frontend has hot-reload enabled by default
- Check browser console (F12) for frontend errors
- Check terminal for backend errors
- MongoDB data is stored in `/data/db` (Windows) or `~/data/db` (Mac/Linux)

## Production Deployment

For production deployment, see:
- Backend: Use gunicorn or uvicorn with proper SSL
- Frontend: Build with `npm run build` and serve with nginx
- Database: Use MongoDB Atlas for cloud hosting
- APIs: Upgrade to paid tiers for higher limits

## Support

If you still can't get it running:
1. Check the error message carefully
2. Search for the error on Google/Stack Overflow
3. Make sure all prerequisites are installed
4. Verify API keys are correct in `.env` file
5. Check that MongoDB is running

## URLs Summary

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: mongodb://localhost:27017

## Next Steps

Once running:
1. Try searching for products
2. Explore the filters and sorting options
3. Test the bulk upload feature
4. Check the price comparison charts
5. Export results to Excel

Happy coding! 🚀
