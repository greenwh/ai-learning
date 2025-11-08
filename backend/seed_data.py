"""
Seed database with initial content
Creates the first module: Stock Fundamentals 101
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal, init_db
from backend.database.models import Module


def create_stock_fundamentals_module():
    """Create the first learning module: Stock Fundamentals 101"""

    module = Module(
        domain="Finance",
        subject="Stock Market Investing",
        topic="Fundamental Analysis",
        title="Stock Fundamentals 101: What They Are and Why They Matter",
        description=(
            "Learn what stock fundamentals really are and why investors use them. "
            "This lesson teaches you the 'health metrics' of a business that help you "
            "decide if a stock is worth buying. No prior finance knowledge needed!"
        ),
        prerequisites=[],
        learning_objectives=[
            "Explain what stock fundamentals are in your own words",
            "Identify the key fundamental metrics investors look at",
            "Understand why fundamentals matter for investment decisions",
            "Recognize the connection between a company's health and its stock price"
        ],
        difficulty_level=1,  # Beginner
        estimated_time=15,  # 15 minutes
        content_config={
            "modalities": {
                "narrative_story": {
                    "enabled": True,
                    "theme": "pizza_restaurant_analogy"
                },
                "interactive_hands_on": {
                    "enabled": True,
                    "type": "company_comparison",
                    "data_source": "real_examples"
                },
                "socratic_dialogue": {
                    "enabled": True,
                    "starting_question": "What would YOU want to know before buying a business?"
                },
                "visual_diagrams": {
                    "enabled": True,
                    "metaphor": "company_as_human_body"
                }
            },
            "key_concepts": [
                "fundamentals_definition",
                "revenue_and_profit",
                "debt_and_assets",
                "growth_metrics",
                "comparison_to_peers"
            ],
            "real_world_examples": [
                "Apple Inc.",
                "Local business comparison",
                "Warren Buffett's approach"
            ]
        },
        version="1.0"
    )

    return module


def create_pe_ratio_module():
    """Create the second module: Understanding P/E Ratio"""

    module = Module(
        domain="Finance",
        subject="Stock Market Investing",
        topic="Fundamental Analysis",
        title="Understanding the Price-to-Earnings (P/E) Ratio",
        description=(
            "Learn how to calculate and interpret the P/E ratio, one of the most "
            "important metrics for valuing stocks. Discover when a high P/E might "
            "actually be good, and when a low P/E could be a red flag."
        ),
        prerequisites=["fundamentals_101"],  # Requires completing the first module
        learning_objectives=[
            "Calculate the P/E ratio from a company's data",
            "Interpret what different P/E levels mean",
            "Understand when a high P/E might be justified",
            "Compare P/E ratios across different industries",
            "Use P/E ratio as part of investment analysis"
        ],
        difficulty_level=2,  # Intermediate
        estimated_time=20,  # 20 minutes
        content_config={
            "modalities": {
                "narrative_story": {
                    "enabled": True,
                    "theme": "investor_sarah_choosing_stocks"
                },
                "interactive_hands_on": {
                    "enabled": True,
                    "type": "pe_calculator",
                    "data_source": "real_stock_data"
                },
                "socratic_dialogue": {
                    "enabled": True,
                    "starting_question": "What helps you judge if something is expensive?"
                },
                "visual_diagrams": {
                    "enabled": True,
                    "type": "comparative_chart"
                }
            },
            "key_concepts": [
                "pe_ratio_formula",
                "earnings_per_share",
                "price_interpretation",
                "growth_premium",
                "industry_comparisons",
                "value_vs_growth"
            ],
            "real_world_examples": [
                "Apple vs Microsoft P/E comparison",
                "Tech vs Traditional industry P/Es",
                "Historical P/E changes"
            ]
        },
        version="1.0"
    )

    return module


def seed_database():
    """Seed the database with initial modules"""
    init_db()

    db = SessionLocal()

    try:
        # Check if modules already exist
        existing = db.query(Module).filter(
            Module.title.like("%Stock Fundamentals 101%")
        ).first()

        if existing:
            print("⚠️  Modules already exist. Skipping seed.")
            return

        # Create modules
        print("📚 Creating learning modules...")

        module1 = create_stock_fundamentals_module()
        db.add(module1)

        module2 = create_pe_ratio_module()
        db.add(module2)

        db.commit()

        print("✅ Created module: Stock Fundamentals 101")
        print("✅ Created module: Understanding P/E Ratio")
        print(f"\n📊 Module IDs:")
        print(f"  - Fundamentals 101: {module1.module_id}")
        print(f"  - P/E Ratio: {module2.module_id}")
        print("\n🎉 Database seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
