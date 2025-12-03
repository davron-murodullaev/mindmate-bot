"""
Premium & Monetization System
Freemium model with usage limits and subscription management
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# === SUBSCRIPTION TIERS ===

SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "ai_requests_daily": 10,
        "pdf_monthly": 3,
        "images_monthly": 0,
        "ppt_monthly": 2,
        "features": ["basic_chat", "mood", "journal", "meditation", "fitness"]
    },
    "premium": {
        "name": "Premium",
        "price": 4.99,
        "ai_requests_daily": 100,
        "pdf_monthly": 50,
        "images_monthly": 30,
        "ppt_monthly": 20,
        "features": ["all", "priority_support", "advanced_analytics"]
    },
    "pro": {
        "name": "Professional",
        "price": 14.99,
        "ai_requests_daily": -1,  # Unlimited
        "pdf_monthly": -1,
        "images_monthly": 100,
        "ppt_monthly": -1,
        "features": ["all", "priority_support", "advanced_analytics", "api_access", "team_features"]
    }
}

# === DATABASE FUNCTIONS ===

def init_premium_tables(conn):
    """Premium uchun jadvallar yaratish"""
    cur = conn.cursor()

    # Subscriptions table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id BIGINT PRIMARY KEY,
            tier TEXT DEFAULT 'free',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            auto_renew BOOLEAN DEFAULT FALSE,
            payment_method TEXT,
            last_payment_date TIMESTAMP
        )
    ''')

    # Usage tracking
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usage_stats (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            feature TEXT,
            count INTEGER DEFAULT 1,
            date DATE DEFAULT CURRENT_DATE,
            CONSTRAINT unique_user_feature_date UNIQUE (user_id, feature, date)
        )
    ''')

    # Referrals
    cur.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id SERIAL PRIMARY KEY,
            referrer_id BIGINT,
            referred_id BIGINT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reward_given BOOLEAN DEFAULT FALSE
        )
    ''')

    # Transactions
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount DECIMAL(10,2),
            currency TEXT DEFAULT 'USD',
            tier TEXT,
            status TEXT,
            payment_method TEXT,
            transaction_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    cur.close()
    logger.info("✅ Premium tables initialized")


def get_user_subscription(conn, user_id):
    """Foydalanuvchi obunasini olish"""
    cur = conn.cursor()
    cur.execute('''
        SELECT tier, expires_at FROM subscriptions
        WHERE user_id = %s
    ''', (user_id,))
    row = cur.fetchone()
    cur.close()

    if not row:
        # Default: free tier
        return {"tier": "free", "expires_at": None}

    tier, expires_at = row

    # Check if expired
    if expires_at and expires_at < datetime.now():
        # Downgrade to free
        update_subscription(conn, user_id, "free", None)
        return {"tier": "free", "expires_at": None}

    return {"tier": tier, "expires_at": expires_at}


def update_subscription(conn, user_id, tier, duration_days=30):
    """Obunani yangilash"""
    cur = conn.cursor()

    if tier == "free":
        expires_at = None
    else:
        expires_at = datetime.now() + timedelta(days=duration_days)

    cur.execute('''
        INSERT INTO subscriptions (user_id, tier, expires_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            tier = %s,
            expires_at = %s,
            last_payment_date = NOW()
    ''', (user_id, tier, expires_at, tier, expires_at))

    conn.commit()
    cur.close()


def check_usage_limit(conn, user_id, feature):
    """Limitni tekshirish"""
    subscription = get_user_subscription(conn, user_id)
    tier = subscription["tier"]
    limits = SUBSCRIPTION_TIERS[tier]

    # Get feature limit
    if feature == "ai_request":
        limit = limits["ai_requests_daily"]
    elif feature == "pdf":
        limit = limits["pdf_monthly"]
    elif feature == "image":
        limit = limits["images_monthly"]
    elif feature == "ppt":
        limit = limits["ppt_monthly"]
    else:
        return True  # No limit for this feature

    # Unlimited (-1)
    if limit == -1:
        return True

    # Get current usage
    cur = conn.cursor()

    if "daily" in str(limits.get(f"{feature}s_daily", "")):
        # Daily limit
        cur.execute('''
            SELECT COALESCE(SUM(count), 0) FROM usage_stats
            WHERE user_id = %s AND feature = %s AND date = CURRENT_DATE
        ''', (user_id, feature))
    else:
        # Monthly limit
        cur.execute('''
            SELECT COALESCE(SUM(count), 0) FROM usage_stats
            WHERE user_id = %s AND feature = %s
            AND date >= DATE_TRUNC('month', CURRENT_DATE)
        ''', (user_id, feature))

    current_usage = cur.fetchone()[0]
    cur.close()

    return current_usage < limit


def increment_usage(conn, user_id, feature):
    """Foydalanishni hisoblash"""
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO usage_stats (user_id, feature, count)
        VALUES (%s, %s, 1)
        ON CONFLICT (user_id, feature, date) DO UPDATE SET
            count = usage_stats.count + 1
    ''', (user_id, feature))
    conn.commit()
    cur.close()


def get_usage_stats(conn, user_id):
    """Foydalanuvchi statistikasi"""
    subscription = get_user_subscription(conn, user_id)
    tier = subscription["tier"]
    limits = SUBSCRIPTION_TIERS[tier]

    cur = conn.cursor()

    # Today's AI requests
    cur.execute('''
        SELECT COALESCE(SUM(count), 0) FROM usage_stats
        WHERE user_id = %s AND feature = 'ai_request' AND date = CURRENT_DATE
    ''', (user_id,))
    ai_used_today = cur.fetchone()[0]

    # This month's PDFs
    cur.execute('''
        SELECT COALESCE(SUM(count), 0) FROM usage_stats
        WHERE user_id = %s AND feature = 'pdf'
        AND date >= DATE_TRUNC('month', CURRENT_DATE)
    ''', (user_id,))
    pdf_used_month = cur.fetchone()[0]

    # This month's images
    cur.execute('''
        SELECT COALESCE(SUM(count), 0) FROM usage_stats
        WHERE user_id = %s AND feature = 'image'
        AND date >= DATE_TRUNC('month', CURRENT_DATE)
    ''', (user_id,))
    images_used_month = cur.fetchone()[0]

    cur.close()

    return {
        "tier": tier,
        "ai_used_today": ai_used_today,
        "ai_limit_daily": limits["ai_requests_daily"],
        "pdf_used_month": pdf_used_month,
        "pdf_limit_month": limits["pdf_monthly"],
        "images_used_month": images_used_month,
        "images_limit_month": limits["images_monthly"],
        "expires_at": subscription["expires_at"]
    }


# === REFERRAL SYSTEM ===

def create_referral(conn, referrer_id, referred_id):
    """Referral yaratish"""
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO referrals (referrer_id, referred_id)
            VALUES (%s, %s)
        ''', (referrer_id, referred_id))
        conn.commit()

        # Reward: +5 free AI requests
        cur.execute('''
            INSERT INTO usage_stats (user_id, feature, count, date)
            VALUES (%s, 'ai_request_bonus', -5, CURRENT_DATE)
            ON CONFLICT (user_id, feature, date) DO UPDATE SET
                count = usage_stats.count - 5
        ''', (referrer_id,))
        conn.commit()

        # Check if user reached milestone for premium bonus (10, 20, 30... referrals)
        cur.execute('SELECT COUNT(*) FROM referrals WHERE referrer_id = %s', (referrer_id,))
        ref_count = cur.fetchone()[0]

        # Grant 7 days premium for every 10 referrals
        if ref_count > 0 and ref_count % 10 == 0:
            # Grant 7 days premium
            from datetime import datetime, timedelta
            cur.execute('''
                SELECT tier, expires_at FROM subscriptions WHERE user_id = %s
            ''', (referrer_id,))
            result = cur.fetchone()

            if result and result[0] in ['premium', 'pro']:
                # User already has premium/pro - extend it by 7 days
                expires_at = result[1]
                if expires_at and expires_at > datetime.now():
                    new_expiry = expires_at + timedelta(days=7)
                else:
                    new_expiry = datetime.now() + timedelta(days=7)

                cur.execute('''
                    UPDATE subscriptions
                    SET expires_at = %s
                    WHERE user_id = %s
                ''', (new_expiry, referrer_id))
            else:
                # User doesn't have premium - grant 7 days premium
                new_expiry = datetime.now() + timedelta(days=7)
                cur.execute('''
                    INSERT INTO subscriptions (user_id, tier, expires_at)
                    VALUES (%s, 'premium', %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        tier = 'premium',
                        expires_at = %s
                ''', (referrer_id, new_expiry, new_expiry))
            conn.commit()

        cur.close()
        return True
    except Exception as e:
        print(f"Error in create_referral: {e}")
        cur.close()
        return False


def get_referral_stats(conn, user_id):
    """Referral statistikasi"""
    cur = conn.cursor()
    cur.execute('''
        SELECT COUNT(*) FROM referrals WHERE referrer_id = %s
    ''', (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    return count


def get_referral_code(user_id):
    """Referral kod yaratish"""
    return f"MM{user_id}"


def parse_referral_code(code):
    """Referral kodni parse qilish"""
    if code.startswith("MM"):
        try:
            return int(code[2:])
        except:
            return None
    return None


# === PREMIUM TEXTS ===

def get_premium_texts(lang="uz"):
    """Premium uchun matnlar"""
    return {
        "uz": {
            "limit_reached": "⚠️ **Limit tugadi!**\n\nSiz bugun {feature} uchun limitga yetdingiz.\n\n🌟 Premium'ga o'ting va cheksiz foydalaning!",
            "upgrade_now": "🌟 Premium'ga o'tish",
            "premium_features": """💎 **Premium Imkoniyatlar**

🚀 **Premium** - $4.99/oy:
• 100 ta AI so'rov/kun
• 50 ta PDF/oy
• 30 ta rasm (DALL-E)/oy
• 20 ta prezentatsiya/oy
• Barcha AI vositalar
• Ustuvor qo'llab-quvvatlash

⭐ **Professional** - $14.99/oy:
• ♾️ Cheksiz AI so'rovlar
• ♾️ Cheksiz PDF
• 100 ta rasm/oy
• ♾️ Cheksiz prezentatsiya
• API kirish
• Jamoa imkoniyatlari
• Advanced analytics

Qaysi birini tanlamoqchisiz?""",
            "subscribe_success": "✅ **Tabriklaymiz!**\n\nSiz {tier} obunasini faollashtirdingiz!\n\nEndi barcha imkoniyatlardan foydalaning! 🎉",
            "usage_stats": """📊 **Foydalanish Statistikasi**

💎 Obuna: {tier}
🤖 AI so'rovlar: {ai_used}/{ai_limit} (bugun)
📄 PDF: {pdf_used}/{pdf_limit} (bu oy)
🎨 Rasmlar: {img_used}/{img_limit} (bu oy)

{expires_text}""",
            "referral_info": """🎁 **Do'stlaringizni taklif qiling!**

Sizning kod: `{code}`

Har bir do'stingiz uchun:
• +5 bonus AI so'rov
• Do'stingiz +3 bonus AI so'rov

Siz {count} ta do'st taklif qildingiz! 🎉

/start {code} - ulashish""",
        },
        "en": {
            "limit_reached": "⚠️ **Limit Reached!**\n\nYou've reached your {feature} limit for today.\n\n🌟 Upgrade to Premium for unlimited access!",
            "upgrade_now": "🌟 Upgrade to Premium",
            "premium_features": """💎 **Premium Features**

🚀 **Premium** - $4.99/month:
• 100 AI requests/day
• 50 PDFs/month
• 30 images (DALL-E)/month
• 20 presentations/month
• All AI tools
• Priority support

⭐ **Professional** - $14.99/month:
• ♾️ Unlimited AI requests
• ♾️ Unlimited PDFs
• 100 images/month
• ♾️ Unlimited presentations
• API access
• Team features
• Advanced analytics

Which one would you like?""",
            "subscribe_success": "✅ **Congratulations!**\n\nYou've activated {tier} subscription!\n\nEnjoy all the features! 🎉",
            "usage_stats": """📊 **Usage Statistics**

💎 Subscription: {tier}
🤖 AI requests: {ai_used}/{ai_limit} (today)
📄 PDFs: {pdf_used}/{pdf_limit} (this month)
🎨 Images: {img_used}/{img_limit} (this month)

{expires_text}""",
            "referral_info": """🎁 **Invite Friends!**

Your code: `{code}`

For each friend:
• +5 bonus AI requests for you
• +3 bonus AI requests for them

You've invited {count} friends! 🎉

/start {code} - share""",
        }
    }.get(lang, {})
