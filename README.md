# AI-Based Personalized Learning System

An adaptive learning platform that **discovers how you learn best** while teaching you what you want to know. The system actively experiments with different teaching modalities, measures effectiveness, and continuously optimizes content delivery to match your unique cognitive patterns.

## 🌟 Key Features

- **Learning Style Discovery**: Doesn't assume—actively discovers through experimentation using multi-armed bandit algorithms
- **Adaptive Content Generation**: AI creates content in real-time tailored to your learning style
- **4 Teaching Modalities**:
  - Narrative/Story-based
  - Interactive/Hands-on
  - Socratic Dialogue
  - Visual/Diagram-based
- **Conversational AI Tutor**: Learn through dialogue, not passive consumption
- **Evidence-Based Adaptation**: Tracks retention and engagement to optimize delivery
- **Multi-AI Provider Support**: Claude (Anthropic), GPT-4 (OpenAI), Gemini (Google)

## 🏗️ Architecture

```
Frontend (React + Vite)
    ↓
Backend API (FastAPI)
    ↓
┌───────────────────────┬────────────────────────┬──────────────────┐
│ Learning Style Engine │ Content Delivery Engine│ AI Tutor Engine  │
│ (Thompson Sampling)   │ (Dynamic Generation)   │ (Conversational) │
└───────────────────────┴────────────────────────┴──────────────────┘
    ↓                   ↓                         ↓
SQLite Database    AI Providers         Engagement Tracking
```

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **npm or yarn**
- **API Keys** (at least one):
  - Anthropic Claude API key (recommended)
  - OpenAI API key (optional fallback)
  - Google Gemini API key (optional)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd /home/user/Placeholder3
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required in .env:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here  # Get from console.anthropic.com
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
```

### 3. Initialize Database and Seed Content

```bash
# Still in backend directory
python seed_data.py
```

This creates:
- Database schema
- Initial modules (Stock Fundamentals 101, P/E Ratio)

### 4. Start Backend Server

```bash
# From backend directory
python main.py
```

Backend will run on `http://localhost:8000`

### 5. Frontend Setup

Open a **new terminal**:

```bash
cd /home/user/Placeholder3/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:5173`

### 6. Create Your First User

1. Open http://localhost:5173 in your browser
2. Click "Create Account"
3. Enter username and password
4. Start learning!

## 🎓 How It Works

### Initial Learning Style Discovery

When you start your first lesson, the system will:

1. **Present the same concept in 4 different ways** (narrative, interactive, Socratic, visual)
2. **Track your engagement** (time spent, questions asked, interaction depth)
3. **Measure comprehension** through casual conversation (not quizzes!)
4. **Test retention** 24 hours later
5. **Build your learning profile** based on which methods work best for you

### Adaptive Learning Loop

```
┌─────────────────────────────────────────────────┐
│ 1. System selects best modality for YOU        │
│    (using Thompson Sampling algorithm)          │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│ 2. AI generates content in that modality        │
│    (Claude creates personalized lesson)         │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│ 3. You learn and interact                       │
│    (Ask questions, explore, engage)             │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│ 4. System measures effectiveness                │
│    (Engagement + Comprehension + Retention)     │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│ 5. Learning profile updated                     │
│    (Future content adapts automatically)        │
└─────────────────────────────────────────────────┘
```

## 📚 Available Modules

### Stock Fundamentals 101
**Difficulty**: Beginner | **Time**: ~15 minutes

Learn what stock fundamentals really are and why investors use them. No prior finance knowledge needed!

**Learning Objectives:**
- Explain what stock fundamentals are
- Identify key fundamental metrics
- Understand why fundamentals matter
- Connect company health to stock price

### Understanding P/E Ratio
**Difficulty**: Intermediate | **Time**: ~20 minutes
**Prerequisites**: Stock Fundamentals 101

Learn to calculate and interpret the P/E ratio, one of the most important valuation metrics.

**Learning Objectives:**
- Calculate P/E ratio from company data
- Interpret different P/E levels
- Understand when high P/E is justified
- Compare P/E across industries

## 🧠 Learning Modalities Explained

### 1. Narrative/Story-Based
Best for: People who learn through stories and real-world examples

**Example**: "Imagine you're thinking about buying your friend's pizza restaurant. You'd want to know: Is it profitable? Are sales growing?..."

### 2. Interactive/Hands-On
Best for: People who learn by doing

**Example**: "Let's look at two real companies. I'll show you their numbers, and you decide which is the better investment. Try changing the variables..."

### 3. Socratic Dialogue
Best for: People who learn by discovering concepts themselves

**Example**:
- "What do YOU think 'fundamentals' means?"
- "What would YOU want to know before buying a business?"
- Guides you to construct understanding

### 4. Visual/Diagram-Based
Best for: Visual learners who think in pictures

**Example**: "Think of a company like a human body. Fundamentals are vital signs: Revenue = Heartbeat, Profit = Energy level..."

## 🔍 Monitoring Your Learning Style

Visit the Progress page to see:

- **Best Modalities**: Which teaching methods work best for you
- **Retention Rates**: How well you remember from each modality
- **Engagement Patterns**: When you learn best, optimal session length
- **Cognitive Patterns**: Your learning preferences and tendencies

Example insights:
```
You learn best through:
✓ Interactive exercises (92% retention)
✓ Real-world examples (85% retention)
✓ Concepts explained with analogies

You struggle with:
⚠ Abstract theory without examples
⚠ Long content (attention drops after 12min)

Recommendations:
- Best learning time: 7-9 PM
- Ideal session length: 15 minutes
- Review concepts on Tuesday
```

## 🛠️ API Endpoints

### Authentication
```
POST   /api/auth/register     # Create new user
POST   /api/auth/login        # Login
GET    /api/auth/users/:username
```

### Learning Sessions
```
POST   /api/sessions/start                    # Start learning session
POST   /api/sessions/:id/engagement           # Track engagement
POST   /api/sessions/:id/complete             # Complete session
```

### AI Tutor Chat
```
POST   /api/chat/:session_id/message                  # Ask question
GET    /api/chat/:session_id/comprehension-check      # Get check
POST   /api/chat/:session_id/comprehension-check      # Evaluate answer
```

### Content & Progress
```
GET    /api/content/modules                   # List modules
GET    /api/content/modules/:id               # Get module
GET    /api/progress/:user_id/overview        # Get progress
```

## 🧪 Testing the System

### Manual Test Flow

1. **Create Account**: Register a new user
2. **Start First Module**: "Stock Fundamentals 101"
3. **Experience All Modalities**: System will try different teaching methods
4. **Ask Questions**: Use the AI tutor chat
5. **Complete Comprehension Check**: Answer the casual question
6. **Complete Session**: Submit your experience
7. **Check Progress**: See which modality worked best
8. **Start Second Session**: Notice the system adapts to your style

### Test with API

```bash
# Create user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# List modules
curl http://localhost:8000/api/content/modules

# Start session
curl -X POST "http://localhost:8000/api/sessions/start?user_id=USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"module_id":"MODULE_ID"}'
```

## 📂 Project Structure

```
Placeholder3/
├── backend/
│   ├── api/
│   │   ├── routes/         # API endpoints
│   │   └── models.py       # Pydantic models
│   ├── ai/
│   │   ├── provider_manager.py    # Multi-AI support
│   │   └── content_templates.py   # Modality templates
│   ├── learning_engine/
│   │   ├── style_engine.py        # Thompson Sampling
│   │   ├── content_delivery.py    # Dynamic generation
│   │   └── tutor_engine.py        # Conversational AI
│   ├── database/
│   │   ├── models.py       # SQLAlchemy models
│   │   └── connection.py   # DB setup
│   ├── main.py             # FastAPI app
│   └── seed_data.py        # Initial content
│
├── frontend/
│   ├── src/
│   │   ├── pages/          # React pages
│   │   ├── components/     # Reusable components
│   │   ├── services/       # API client
│   │   ├── store/          # Zustand state
│   │   └── App.tsx
│   └── package.json
│
└── learning_system_arch.md  # Full architecture doc
```

## 🔐 Security & Privacy

- **Local-First**: All data stored locally in encrypted SQLite database
- **Optional Cloud Sync**: You control what syncs
- **No PII Required**: Only username needed
- **Encrypted at Rest**: SQLCipher encryption
- **HTTPS in Production**: All API calls encrypted

## 🎯 Roadmap

### Phase 1 (Current): MVP Core
- ✅ Learning style discovery engine
- ✅ 4 modality templates
- ✅ Multi-AI provider support
- ✅ Basic UI
- ✅ 2 finance modules

### Phase 2: Enhanced Intelligence
- [ ] Spaced repetition system
- [ ] 24-hour retention testing
- [ ] Advanced pattern recognition
- [ ] Emotion detection

### Phase 3: Content Expansion
- [ ] Complete finance curriculum (10+ modules)
- [ ] New domains (D&D lore, programming, history)
- [ ] User-requested topics
- [ ] Community content

### Phase 4: Advanced Features
- [ ] Tauri desktop app
- [ ] Mobile PWA
- [ ] Gamification system
- [ ] Social learning features

## 🤝 Contributing

This is a personal learning system, but the architecture is designed to be extensible.

### Adding New Modules

Edit `backend/seed_data.py`:

```python
def create_your_module():
    return Module(
        domain="YourDomain",
        title="Your Module Title",
        learning_objectives=[...],
        # ... etc
    )
```

### Adding New Modalities

Edit `backend/ai/content_templates.py`:

```python
def _your_modality_template(concept, learning_objective, user_context):
    return """Your template..."""
```

## 📄 License

MIT License - Feel free to learn from and adapt this code!

## 🙏 Acknowledgments

- **Inspired by**: Warren Buffett's teaching philosophy
- **AI Providers**: Anthropic Claude, OpenAI, Google Gemini
- **Architecture**: Multi-armed bandit algorithms for personalization

## 💡 Philosophy

> "Tell me and I forget, teach me and I may remember, involve me and I learn."
> — Benjamin Franklin

This system embodies that philosophy by:
- **Discovering** your unique learning style through experimentation
- **Adapting** content to match how YOU learn best
- **Involving** you through conversation and interaction
- **Measuring** actual learning outcomes, not just completion

## 📞 Support

For questions or issues:
1. Check the architecture document: `learning_system_arch.md`
2. Review API docs: http://localhost:8000/docs (when backend is running)
3. Check database: `backend/data/learning_system.db`

## 🚀 Getting Started - Quick Commands

```bash
# Terminal 1: Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Then add your API key
python seed_data.py
python main.py

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Open browser: http://localhost:5173
```

Happy Learning! 🎓
