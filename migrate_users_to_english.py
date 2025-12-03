#!/usr/bin/env python3
"""
Migration Script: Update all users from 'uz' to 'en' language
This script updates existing users who have 'uz' (Uzbek) language to 'en' (English)
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_users():
    """Migrate all users with 'uz' language to 'en'"""
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables!")
        return

    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        # Check how many users have 'uz' language
        cur.execute("SELECT COUNT(*) FROM users WHERE language = 'uz'")
        uz_count = cur.fetchone()[0]

        print(f"📊 Found {uz_count} users with 'uz' language")

        if uz_count == 0:
            print("✅ No users to migrate!")
            cur.close()
            conn.close()
            return

        # Update all users from 'uz' to 'en'
        cur.execute("UPDATE users SET language = 'en' WHERE language = 'uz'")
        updated = cur.rowcount
        conn.commit()

        print(f"✅ Successfully migrated {updated} users from 'uz' to 'en'")

        # Verify
        cur.execute("SELECT COUNT(*) FROM users WHERE language = 'en'")
        en_count = cur.fetchone()[0]
        print(f"📊 Total users with 'en' language: {en_count}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error during migration: {e}")

if __name__ == "__main__":
    print("🔄 Starting migration: 'uz' → 'en'")
    print("-" * 50)
    migrate_users()
    print("-" * 50)
    print("✅ Migration complete!")
