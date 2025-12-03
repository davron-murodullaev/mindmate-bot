#!/usr/bin/env python3
"""Test database connection and check user languages"""

import psycopg2

DATABASE_URL = "postgresql://mindmate_db_l6n0_user:9IjW2Qu8t1WeaQVoSPVvCrfdQP6fKEg1@dpg-d4kc472dbo4c73csoa10-a.oregon-postgres.render.com/mindmate_db_l6n0"

try:
    print("🔌 Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # Check current language distribution
    print("\n📊 CURRENT LANGUAGE DISTRIBUTION:")
    print("-" * 50)
    cur.execute("SELECT language, COUNT(*) as count FROM users GROUP BY language ORDER BY count DESC")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} users")

    # Check total users
    print("\n👥 TOTAL USERS:")
    print("-" * 50)
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    print(f"  Total: {total} users")

    # Show sample users (first 5)
    print("\n👤 SAMPLE USERS (first 5):")
    print("-" * 50)
    cur.execute("SELECT user_id, username, full_name, language FROM users LIMIT 5")
    for row in cur.fetchall():
        print(f"  ID: {row[0]}, @{row[1]}, {row[2]}, Lang: {row[3]}")

    # Check if migration is needed
    cur.execute("SELECT COUNT(*) FROM users WHERE language = 'uz'")
    uz_count = cur.fetchone()[0]

    if uz_count > 0:
        print(f"\n⚠️  WARNING: {uz_count} users still have 'uz' language!")
        print("   Run migration to update them to 'en'")
    else:
        print("\n✅ All users are on English or Russian!")

    cur.close()
    conn.close()
    print("\n✅ Database check complete!")

except Exception as e:
    print(f"\n❌ Error: {e}")
