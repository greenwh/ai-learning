# Module Creation Guide

Complete guide for creating your own learning modules without consuming API costs.

## 📋 Module Structure

A module consists of:

### Required Fields

```python
{
    "domain": str,              # Broad category (e.g., "Finance", "Science", "Technology")
    "subject": str,             # Specific subject (e.g., "Stock Market Investing")
    "topic": str,               # Specific topic (e.g., "Fundamental Analysis")
    "title": str,               # Full title of the module
    "description": str,         # What learners will get from this
    "prerequisites": [str],     # List of module IDs needed first (empty [] if none)
    "learning_objectives": [str], # List of specific learning goals
    "difficulty_level": int,    # 1-5 (1=Beginner, 5=Expert)
    "estimated_time": int,      # Time in minutes
    "content_config": {         # Configuration for content generation
        "modalities": {...},    # Settings for each teaching modality
        "key_concepts": [...],  # List of key concepts to cover
        "real_world_examples": [...] # Examples to use
    },
    "version": str              # Version number (e.g., "1.0")
}
```

## 📝 Module Template

Save this as a JSON file (e.g., `my_module.json`):

```json
{
    "domain": "Finance",
    "subject": "Stock Market Investing",
    "topic": "Fundamental Analysis",
    "title": "Understanding Stock Fundamentals",
    "description": "Learn what stock fundamentals are and how to use them for investment decisions.",
    "prerequisites": [],
    "learning_objectives": [
        "Explain what stock fundamentals are",
        "Identify key fundamental metrics",
        "Understand why fundamentals matter",
        "Apply fundamental analysis to real stocks"
    ],
    "difficulty_level": 1,
    "estimated_time": 15,
    "content_config": {
        "modalities": {
            "narrative_story": {
                "enabled": true,
                "theme": "real_investor_story"
            },
            "interactive_hands_on": {
                "enabled": true,
                "type": "hands_on_exercise",
                "data_source": "real_examples"
            },
            "socratic_dialogue": {
                "enabled": true,
                "starting_question": "What would you want to know before investing?"
            },
            "visual_diagrams": {
                "enabled": true,
                "metaphor": "simple_visual_analogy"
            }
        },
        "key_concepts": [
            "concept_1",
            "concept_2",
            "concept_3"
        ],
        "real_world_examples": [
            "Example 1",
            "Example 2"
        ]
    },
    "version": "1.0"
}
```

## 🎯 Field Explanations

### domain
Broad category of knowledge:
- Finance, Science, Technology, Arts, History, etc.

### subject
Specific subject within the domain:
- "Stock Market Investing" (within Finance)
- "Biology" (within Science)
- "Web Development" (within Technology)

### topic
Narrow topic within the subject:
- "Fundamental Analysis" (within Stock Market Investing)
- "Photosynthesis" (within Biology)
- "React Hooks" (within Web Development)

### title
Clear, descriptive title:
- "Stock Fundamentals 101: What They Are and Why They Matter"
- "Understanding Photosynthesis: How Plants Make Food"
- "React Hooks: A Beginner's Guide"

### description
2-3 sentences explaining what they'll learn:
- Focus on outcomes
- No jargon unless necessary
- Make it compelling

### prerequisites
List of module_id values (NOT titles) that must be completed first:
- `[]` - No prerequisites (beginner module)
- `["module_abc123"]` - Requires one module
- `["module_abc123", "module_def456"]` - Requires multiple

### learning_objectives
Specific, measurable goals (3-5 objectives):
- Start with action verbs: "Explain", "Calculate", "Identify", "Apply"
- Be specific: "Calculate the P/E ratio from company financials"
- Not vague: "Understand investing" ❌

**Good Examples:**
- "Explain what stock fundamentals are in your own words"
- "Calculate the P/E ratio from a company's data"
- "Identify red flags in a balance sheet"

**Bad Examples:**
- "Learn about stocks" ❌
- "Understand finance" ❌
- "Know stuff" ❌

### difficulty_level
1-5 scale:
- **1**: Complete beginner, no prior knowledge
- **2**: Some basics helpful but not required
- **3**: Intermediate, assumes foundational knowledge
- **4**: Advanced, requires solid understanding
- **5**: Expert level, specialized knowledge

### estimated_time
Realistic time in minutes:
- Beginner: 10-20 minutes
- Intermediate: 15-30 minutes
- Advanced: 20-40 minutes

### content_config
Configuration for how content is generated:

```json
{
    "modalities": {
        "narrative_story": {
            "enabled": true,
            "theme": "Description of story approach"
        },
        "interactive_hands_on": {
            "enabled": true,
            "type": "Type of interaction",
            "data_source": "Where examples come from"
        },
        "socratic_dialogue": {
            "enabled": true,
            "starting_question": "Opening question to get them thinking"
        },
        "visual_diagrams": {
            "enabled": true,
            "metaphor": "Visual analogy to use"
        }
    },
    "key_concepts": [
        "concept_id_1",
        "concept_id_2",
        "concept_id_3"
    ],
    "real_world_examples": [
        "Example 1 description",
        "Example 2 description"
    ]
}
```

**Modality Themes:**
- **narrative_story**: "pizza_restaurant_analogy", "investor_journey", "historical_event"
- **interactive_hands_on**: "company_comparison", "calculation_exercise", "real_data_analysis"
- **socratic_dialogue**: Opening question that gets them thinking
- **visual_diagrams**: "company_as_human_body", "flow_chart", "comparison_table"

**Key Concepts:**
Use underscores, lowercase, descriptive:
- "p_e_ratio"
- "revenue_vs_profit"
- "debt_to_equity"

## 🛠️ Creating Modules Without API Costs

### Option 1: Use Your Own AI to Generate Content

The system uses AI during the learning session to generate content. The `content_config` is just **metadata** that guides content generation. You don't need to write the actual lesson content!

When a user starts a learning session:
1. System reads the `content_config`
2. Uses AI to generate content based on the modality
3. Uses your `key_concepts` and `real_world_examples` as context

**You're just defining the structure, not writing lessons!**

### Option 2: Create JSON Files

Create module JSON files and import them:

```bash
# Create your module JSON
nano my_module.json

# Import it
cd backend
source venv/bin/activate
python module_creator.py import my_module.json
```

### Option 3: Use the Web UI (Coming Soon)

Module creation UI where you fill in a form instead of JSON.

## 📦 Module Creator Script

I've created a helper script: `backend/module_creator.py`

### Usage:

```bash
cd backend
source venv/bin/activate

# Create from JSON file
python module_creator.py import path/to/module.json

# Create from interactive prompts
python module_creator.py create

# List all modules
python module_creator.py list

# Export a module
python module_creator.py export MODULE_ID
```

## 💡 Using Your AI Subscription

### Where API Costs Come From

API calls happen at:
1. **Learning session start**: Generates personalized lesson content
2. **AI tutor chat**: When users ask questions
3. **Comprehension checks**: Generating and evaluating answers
4. **Retention tests**: Creating and evaluating recall questions

### How to Minimize Costs

#### 1. Pre-Generate Static Content (Advanced)

You can add pre-written content to `content_config`:

```json
"content_config": {
    "modalities": {
        "narrative_story": {
            "enabled": true,
            "theme": "pizza_restaurant_analogy",
            "pre_generated_content": "Your pre-written lesson here..."
        }
    }
}
```

If `pre_generated_content` exists, system uses it instead of calling AI.

#### 2. Use Your AI to Generate Lessons

Use your AI subscription (ChatGPT, Claude, etc.) to create content, then add to module:

```python
# Example workflow:

# 1. You use your AI subscription:
# "Create a lesson about stock fundamentals using a story about a pizza restaurant"

# 2. Copy the generated content

# 3. Add to module:
module.content_config["modalities"]["narrative_story"]["pre_generated_content"] = """
[Paste your AI-generated content here]
"""
```

#### 3. Use Cheaper AI Models

Update `.env` to use cheaper models:

```bash
# Use GPT-4o-mini instead of Claude (much cheaper)
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini

# Or use Gemini Flash (free tier available)
GOOGLE_API_KEY=your-key
GEMINI_MODEL=gemini-2.0-flash-exp
```

## 📊 Complete Example

Here's a complete, real module you can use as a template:

```json
{
    "domain": "Finance",
    "subject": "Stock Market Investing",
    "topic": "Dividend Investing",
    "title": "Understanding Dividends: Passive Income from Stocks",
    "description": "Learn what dividends are, how they work, and how to build passive income through dividend investing. Perfect for beginners interested in income-generating investments.",
    "prerequisites": [],
    "learning_objectives": [
        "Explain what dividends are and how they work",
        "Calculate dividend yield from stock data",
        "Identify good dividend-paying stocks",
        "Understand the difference between dividend growth and high yield",
        "Recognize risks in dividend investing"
    ],
    "difficulty_level": 1,
    "estimated_time": 20,
    "content_config": {
        "modalities": {
            "narrative_story": {
                "enabled": true,
                "theme": "retiree_building_passive_income",
                "context": "Story of someone building income through dividends"
            },
            "interactive_hands_on": {
                "enabled": true,
                "type": "dividend_calculator",
                "data_source": "real_dividend_stocks",
                "context": "Calculate actual dividend income from real companies"
            },
            "socratic_dialogue": {
                "enabled": true,
                "starting_question": "If you owned 100 shares of a company, how might you make money besides selling them?"
            },
            "visual_diagrams": {
                "enabled": true,
                "metaphor": "fruit_tree_analogy",
                "context": "Dividends as fruit from a tree you own"
            }
        },
        "key_concepts": [
            "dividend_definition",
            "dividend_yield",
            "dividend_growth",
            "payout_ratio",
            "dividend_aristocrats",
            "ex_dividend_date",
            "dividend_reinvestment"
        ],
        "real_world_examples": [
            "Coca-Cola (50+ years of dividend increases)",
            "Johnson & Johnson (dividend aristocrat)",
            "High yield vs growth comparison"
        ]
    },
    "version": "1.0"
}
```

## 🎓 Best Practices

### 1. Start Simple
- Create beginner modules first
- No prerequisites
- Clear, simple objectives
- 15-20 minute duration

### 2. Build Progressively
- Each module builds on previous ones
- Use `prerequisites` to create learning paths
- Gradually increase difficulty

### 3. Be Specific
- Narrow topics work better than broad ones
- "Understanding P/E Ratio" > "Understanding Stock Valuation"
- Students can complete focused modules faster

### 4. Real Examples
- Always include real-world examples
- Use current, recognizable companies
- Make it practical

### 5. Test Your Modules
- Create a test user
- Go through the module yourself
- Refine based on experience

## 🔧 Advanced: Module Collections

Create themed collections:

```
Finance Basics Series:
├── Module 1: Stock Fundamentals (no prerequisites)
├── Module 2: P/E Ratio (requires Module 1)
├── Module 3: Dividends (requires Module 1)
├── Module 4: Balance Sheets (requires Modules 1, 2, 3)
└── Module 5: Complete Analysis (requires all previous)
```

## 📚 Example Domains & Subjects

### Finance
- Stock Market Investing
- Personal Finance
- Cryptocurrency
- Real Estate

### Technology
- Web Development
- Data Science
- Cybersecurity
- AI/Machine Learning

### Science
- Biology
- Chemistry
- Physics
- Astronomy

### Business
- Marketing
- Entrepreneurship
- Project Management
- Sales

### Arts
- Photography
- Music Theory
- Drawing
- Writing

## 🚀 Quick Start Checklist

- [ ] Read this guide thoroughly
- [ ] Copy the JSON template
- [ ] Fill in your module details
- [ ] Keep it simple (beginner level first)
- [ ] Add 3-5 clear learning objectives
- [ ] Include real-world examples
- [ ] Save as JSON file
- [ ] Import using module_creator.py
- [ ] Test the module yourself
- [ ] Refine and iterate

## 💰 Cost Comparison

**With Pre-Generated Content:**
- $0.00 per learning session (you generate content once with your AI)

**With Dynamic Generation:**
- ~$0.01-0.05 per learning session (depending on model)
- GPT-4o-mini: ~$0.01/session
- Claude Sonnet: ~$0.03/session
- Gemini Flash: Free tier available

**Recommendation:**
For modules you'll use repeatedly, consider pre-generating content with your AI subscription to eliminate per-session costs.

---

**Need help? Check the complete example modules in `backend/seed_data.py`**
