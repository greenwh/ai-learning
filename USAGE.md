# How to Use the AI Personalized Learning System

## 🎯 Overview

This system lets you learn **anything you want** through a personalized, AI-driven experience. Just type what you want to learn, and the system will:

1. **Assess your current knowledge** through conversation
2. **Discover how you learn best** (narrative, interactive, Socratic, or visual)
3. **Generate personalized content** tailored to both WHAT you know and HOW you learn

## 🚀 Getting Started

### Step 1: Start the System

```bash
./start.sh
```

Or manually:
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Open http://localhost:5173

### Step 2: Create Your Account

- Click "Register"
- Enter username and password
- That's it! (Email is optional)

## 📚 The Learning Process

### 1. Choose What to Learn

On the dashboard, type **anything** you want to learn:

**Examples:**
- "stock fundamentals"
- "Warren Buffett's investing philosophy"
- "how do bonds work"
- "P/E ratio explained"
- "value investing strategies"

No need to pick from a list - just describe what you want to know!

### 2. Knowledge Assessment (3 Questions)

The AI will ask you 3 conversational questions to understand:
- What you already know
- Where you're confused
- Where to start your learning

**This is NOT a test!** Be honest. If you don't know something, say so. The AI will adapt the lesson to your level.

**Example Assessment:**

```
AI: What do you already know about stock fundamentals?
You: Not much, I've heard the term but don't really know what it means.

AI: Have you ever thought about what you'd want to know before buying a piece of a business?
You: I guess I'd want to know if it makes money and if it's growing.

AI: Great start! If you saw two companies, both making profit, how might you decide which is the better investment?
You: Maybe which one is growing faster? Or has less debt?
```

### 3. Assessment Results

After 3 questions, you'll see:

```
✅ Your Current Level: 2/5 (Beginner)

📝 Summary: You understand the basic concept of evaluating businesses
    but haven't learned the specific metrics investors use.

🎯 What You'll Learn:
  ✓ What stock fundamentals are and why they matter
  ✓ Key metrics: Revenue, Profit, Debt, Assets
  ✓ How to read basic financial health indicators
  ✓ The connection between business health and stock price

🚀 Starting Point: We'll begin with what fundamentals are,
   using real company examples you can relate to.
```

### 4. Personalized Lesson

Click "Start My Personalized Lesson" and the AI will generate content in one of 4 teaching styles:

#### 📖 Narrative/Story-Based
*Good for: People who learn through stories and real-world examples*

```
Imagine you're thinking about buying your friend's pizza restaurant...

Last month it made $10,000 in revenue but spent $12,000 on ingredients
and rent. That's a problem - it's losing $2,000/month!

Meanwhile, your other friend's coffee shop made $8,000 and only spent
$5,000. That's $3,000 in profit. Even though it has lower revenue,
it's the healthier business.

This is exactly what stock fundamentals tell you...
```

#### 🎮 Interactive/Hands-On
*Good for: People who learn by doing*

```
Here are two real companies. YOU decide which is the better investment:

Company A (TechCorp):
- Revenue: $100M (grew 50% last year)
- Profit: -$10M (losing money)
- Debt: $200M
- Cash: $50M

Company B (StableCo):
- Revenue: $80M (grew 5% last year)
- Profit: $15M (making money)
- Debt: $20M
- Cash: $30M

Which would you invest in? Why?...
```

#### 💭 Socratic Dialogue
*Good for: People who learn by discovering concepts themselves*

```
Before I tell you what fundamentals are, let me ask you something:

If you were going to buy a business - like actually buy 100% of it -
what would you want to know about it first?

[You answer]

Exactly! Now, what if you could only own 1% of that business. Would you
still want to know those same things?

[You answer]

That's the insight! When you buy stock, you're buying a tiny piece of
a business. So the questions you'd ask about buying the whole business
are the SAME questions you should ask about the stock...
```

#### 📊 Visual/Diagram-Based
*Good for: Visual learners who think in pictures*

```
Picture a company like a human body:

     Head (Leadership)
        ↓
    Heartbeat = Revenue (blood flowing in)
        ↓
    Energy Level = Profit (what's left after burning calories)
        ↓
    Weight = Debt (extra weight slowing you down)
        ↓
    Savings = Cash (emergency fund)

A healthy company is like a healthy person:
- Strong heartbeat (steady revenue)
- High energy (consistent profit)
- Light weight (manageable debt)
- Good savings (cash reserves)

Let me show you how to check these "vital signs"...
```

### 5. The AI Will Adapt

After 3-4 lessons, check your Progress page to see:

```
Your Learning Style:

Interactive Hands-On:     ████████████████░░░░  85% effective
Narrative Stories:        ████████████░░░░░░░░  65% effective
Visual Diagrams:          ███████████░░░░░░░░░  60% effective
Socratic Dialogue:        ████████░░░░░░░░░░░░  45% effective

📊 Recommendations:
✓ You learn best through interactive exercises (85% retention)
✓ Real-world examples work better for you than abstract theory
✓ Ideal session length: 15 minutes
✓ Best learning time: 7-9 PM
```

**Future lessons will prioritize Interactive + Narrative styles for you!**

### 6. Ask the AI Tutor

During any lesson, you can ask questions:

```
You: What's the difference between revenue and profit?

AI Tutor: Great question! Revenue is ALL the money coming in the door.
Profit is what's LEFT after you pay all the bills.

Think of it like your paycheck vs your savings:
- Revenue = Your gross salary ($5,000/month)
- Expenses = Rent, food, car ($4,200/month)
- Profit = What you can save ($800/month)

A company can have HUGE revenue but still lose money if expenses are
too high. That's why profit matters more than revenue...
```

## 🎯 Learning Different Subjects

The system works for **any subject**. Here's how it adapts:

### Finance Example
```
Subject: "Warren Buffett's investment strategy"

Assessment discovers:
- You know basics of stocks
- Don't know about value investing
- Want to learn practical application

Lesson generated:
- Story of how Buffett bought Coca-Cola
- Interactive analysis of "undervalued" companies
- Practical framework you can use
```

### Non-Finance Example
```
Subject: "How does photosynthesis work"

Assessment discovers:
- Remember it from school but fuzzy on details
- Visual learner
- Want practical understanding

Lesson generated:
- Visual diagram of the process
- Step-by-step with pictures
- Real-world applications (why plants need light)
```

## 📈 Tips for Best Results

### 1. Be Specific in Your Subject
❌ "investing"
✅ "how to analyze if a stock is overpriced"

❌ "finance"
✅ "understanding debt-to-equity ratio"

### 2. Be Honest in Assessments
- Don't pretend to know more than you do
- Don't pretend to know less than you do
- The AI will adapt to your real level

### 3. Complete Multiple Sessions
- First 1-2 sessions: System is exploring different methods
- Sessions 3-4: System starts to understand your style
- Sessions 5+: Fully optimized to how YOU learn

### 4. Ask Questions During Lessons
- The AI tutor is there to help
- Questions improve engagement tracking
- System learns you're curious

### 5. Finish Sessions
- Click "Complete Lesson" when done
- This helps the system learn what works
- Provides feedback for future optimization

## 🔄 The Adaptation Loop

```
Session 1: Try Narrative style → 70% engagement
Session 2: Try Interactive style → 90% engagement
Session 3: Try Socratic style → 60% engagement
Session 4: Try Visual style → 75% engagement

System learns: Interactive (90%) > Visual (75%) > Narrative (70%) > Socratic (60%)

Future sessions:
- 50% chance: Interactive (your best)
- 25% chance: Visual (your second best)
- 15% chance: Narrative
- 10% chance: Socratic (still exploring)
```

## 🎓 Advanced Features

### Force a Specific Modality

If you want to try a specific teaching style, you can request it in your subject:

```
"Explain stock fundamentals using stories"  → Forces Narrative
"Teach me about P/E ratio with examples I can try" → Forces Interactive
"Help me discover what market cap means" → Forces Socratic
"Show me visually how dividends work" → Forces Visual
```

### Learn Related Topics

The system can build on what you've learned:

```
Session 1: "stock fundamentals" (Level 2 → 4)
Session 2: "P/E ratio" (starts at Level 4, builds to 5)
Session 3: "reading balance sheets" (starts at Level 4)
```

### Track Specific Concepts

The system tracks individual concepts:

```
Concepts Mastered:
✓ What fundamentals are (100%)
✓ Revenue vs Profit (95%)
✓ Debt metrics (85%)
⚠ P/E ratio calculation (60%) - needs review
```

## 🛠️ Troubleshooting

### "Error starting assessment"
- Check backend is running (`python main.py`)
- Verify API key in `backend/.env`
- Check backend logs for errors

### "Content generation slow"
- First generation: 5-10 seconds (AI thinking)
- Subsequent: 2-3 seconds
- This is normal!

### "Assessment seems stuck"
- Check browser console for errors
- Refresh page and try again
- Check backend logs

### "No progress showing"
- Complete at least 1 full session
- Click "Complete Lesson"
- Check `/api/progress/{user_id}/overview` endpoint

## 📊 Understanding Your Data

All data is in: `backend/data/learning_system.db`

You can inspect it with any SQLite viewer:

```bash
sqlite3 backend/data/learning_system.db

# See your sessions
SELECT * FROM learning_sessions;

# See your learning profile
SELECT * FROM learning_profiles;

# See engagement signals
SELECT * FROM engagement_signals;
```

## 🎉 That's It!

The system learns as you learn. The more sessions you complete, the better it gets at teaching YOU specifically.

Happy learning! 🚀
