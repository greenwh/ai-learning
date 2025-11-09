# Quick Start Guide

## Prerequisites Check

Before starting, make sure you have:

- [ ] Python 3.10 or higher
- [ ] Node.js 18 or higher
- [ ] At least one AI provider API key:
  - **Anthropic** (recommended): https://console.anthropic.com
  - **OpenAI** (optional): https://platform.openai.com
  - **Google Gemini** (optional): https://makersuite.google.com
  - **xAI** (optional): https://x.ai

## 5-Minute Setup

### Step 1: Add Your API Key(s)

Edit `backend/.env` and add at least one provider's API key:

```bash
# At least one required (Anthropic recommended)
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Optional - add for automatic fallback and provider diversity
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_MODEL=gpt-4o-mini

# GOOGLE_API_KEY=your-key-here
# GEMINI_MODEL=gemini-2.0-flash-exp

# XAI_API_KEY=your-key-here
# XAI_MODEL=grok-3
```

**Note**: System has robust compatibility handling for all models. See [MULTI_MODEL_COMPATIBILITY_GUIDE.md](MULTI_MODEL_COMPATIBILITY_GUIDE.md) for model-specific details.

### Step 2: Run the Start Script

```bash
./start.sh
```

This script will:
- Create Python virtual environment
- Install all dependencies
- Initialize and seed the database
- Start both backend and frontend servers

### Step 3: Open Your Browser

Go to: http://localhost:5173

### Step 4: Create Your Account

1. Click "Create Account"
2. Enter a username and password
3. Click "Register"

### Step 5: Start Learning!

1. You'll see "Stock Fundamentals 101" module
2. Click "Start Learning"
3. The AI will generate a lesson in one of 4 modalities
4. Interact with the content, ask questions
5. Complete the comprehension check
6. Submit your session

### Step 6: See the Magic

After 3-4 sessions, check your Progress page to see:
- Which teaching method works best for YOU
- Your retention rates by modality
- Personalized learning recommendations

## What to Expect on Your First Session

1. **Content Generation**: Takes 3-5 seconds while AI creates your lesson
2. **Modality**: First session is random (system is discovering your style)
3. **AI Tutor**: Ask questions anytime during the lesson
4. **Comprehension Check**: A casual question, not a test
5. **Feedback**: System learns from your engagement

## Troubleshooting

### Backend won't start
- Check if port 8000 is available: `lsof -i :8000`
- Verify your API key in `backend/.env`
- Check Python version: `python3 --version` (need 3.10+)

### Frontend won't start
- Check if port 5173 is available: `lsof -i :5173`
- Delete `node_modules` and run `npm install` again
- Check Node version: `node --version` (need 18+)

### No modules showing up
- Run the seed script: `cd backend && python seed_data.py`
- Check database was created: `ls backend/data/`

### AI errors
- Verify API key is correct in `backend/.env`
- Check you have credits in your Anthropic account
- Look at backend logs for specific error messages

## Manual Setup (Alternative)

If the start script doesn't work, here's the manual process:

### Terminal 1 - Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed_data.py
python main.py
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Next Steps

Once running:

1. **Explore Modules**: Check out Stock Fundamentals 101 and P/E Ratio
2. **Try Different Modalities**: Force a specific modality in session start
3. **Ask Questions**: Use the AI tutor to go deeper
4. **Check Progress**: See how the system learns about YOU
5. **Read Architecture**: Check `learning_system_arch.md` for details

## Testing the API

With backend running, visit:
- http://localhost:8000 - Health check
- http://localhost:8000/docs - Interactive API documentation

## Customization

### Add Your Own Module

Edit `backend/seed_data.py` and add:

```python
def create_my_module():
    return Module(
        domain="YourDomain",
        subject="YourSubject",
        topic="YourTopic",
        title="Your Module Title",
        description="What you'll learn",
        learning_objectives=[
            "Objective 1",
            "Objective 2",
        ],
        difficulty_level=1,
        estimated_time=15,
        content_config={...}
    )
```

Then run: `python seed_data.py`

### Configure AI Providers

The system supports multiple AI providers with automatic fallback:

**Supported Providers:**
- **Anthropic Claude**: Most reliable, recommended for primary use
- **OpenAI GPT**: All models (GPT-3.5, GPT-4, GPT-5, O1/O3 series)
- **Google Gemini**: All Gemini models
- **xAI Grok**: All Grok models

**Configuration:**
Add any/all provider keys to `backend/.env` for automatic fallback.

**Model Compatibility:**
System automatically handles model-specific quirks (temperature restrictions, token parameter variations, response formats). See [MULTI_MODEL_COMPATIBILITY_GUIDE.md](MULTI_MODEL_COMPATIBILITY_GUIDE.md) for details.

## Understanding Your Learning Data

All your data is stored locally in:
`backend/data/learning_system.db`

This is a SQLite database you can inspect with any SQLite viewer.

### Key Tables:
- `users` - Your account
- `learning_profiles` - Your learning style data
- `learning_sessions` - Each lesson you complete
- `modules` - Available content
- `engagement_signals` - How you interact

## Privacy

- Everything runs locally
- No data sent to cloud (except AI API calls)
- You own your learning data
- Can export/backup the SQLite database

## Performance Tips

- First content generation: 3-5 seconds
- Subsequent sessions: 2-3 seconds
- Chat responses: 1-2 seconds
- Database queries: <100ms

## Support

If you get stuck:
1. Check logs in the terminal
2. Review `README.md` for detailed docs
3. Check `learning_system_arch.md` for architecture
4. Look at API docs at http://localhost:8000/docs

Happy Learning! 🎓
