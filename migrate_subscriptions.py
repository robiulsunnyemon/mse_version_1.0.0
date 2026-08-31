import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text

# Add parent directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.db import engine

def run_migration():
    print("🚀 Starting production database migration for subscription fields...")
    queries = [
        "ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS is_subscribed BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS subscription_expiry TIMESTAMP NULL;",
        "ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS subscription_product_id VARCHAR NULL;",
        "ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS subscription_purchase_token VARCHAR NULL;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_subscribed BOOLEAN DEFAULT FALSE;",
    ]

    try:
        with engine.connect() as conn:
            for query in queries:
                print(f"Executing: {query}")
                conn.execute(text(query))
            conn.commit()
        print("✅ Migration completed successfully! No existing data was altered or deleted.")
    except Exception as e:
        print(f"❌ Migration error: {e}")

if __name__ == "__main__":
    run_migration()
