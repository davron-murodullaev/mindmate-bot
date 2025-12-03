#!/usr/bin/env python3
"""
Simple Bot Tester - Test your MindMate bot locally
Run this on your computer to test the bot
"""

import requests
import json

BOT_TOKEN = "8321854805:AAFdYxXdxplJ1PAWsgzlm6klnL7T-k6cjjs"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def test_bot_info():
    """Test 1: Check if bot is running"""
    print("🤖 TEST 1: Bot Info")
    print("-" * 50)

    response = requests.get(f"{API_URL}/getMe")
    data = response.json()

    if data['ok']:
        bot_info = data['result']
        print(f"✅ Bot is ONLINE!")
        print(f"   Name: {bot_info['first_name']}")
        print(f"   Username: @{bot_info['username']}")
        print(f"   ID: {bot_info['id']}")
    else:
        print(f"❌ Bot is OFFLINE")
        print(f"   Error: {data}")

    return data['ok']

def test_webhook():
    """Test 2: Check webhook status"""
    print("\n📡 TEST 2: Webhook Info")
    print("-" * 50)

    response = requests.get(f"{API_URL}/getWebhookInfo")
    data = response.json()

    if data['ok']:
        webhook = data['result']
        if webhook.get('url'):
            print(f"✅ Webhook is SET")
            print(f"   URL: {webhook['url']}")
            print(f"   Pending updates: {webhook.get('pending_update_count', 0)}")
            if webhook.get('last_error_message'):
                print(f"   ⚠️  Last error: {webhook['last_error_message']}")
        else:
            print(f"⚠️  Webhook is NOT set (using polling?)")
    else:
        print(f"❌ Error getting webhook info")

    return data['ok']

def test_recent_updates():
    """Test 3: Get recent updates"""
    print("\n📬 TEST 3: Recent Updates")
    print("-" * 50)

    response = requests.get(f"{API_URL}/getUpdates?limit=5")
    data = response.json()

    if data['ok']:
        updates = data['result']
        if updates:
            print(f"✅ Found {len(updates)} recent updates")
            for update in updates[-3:]:  # Show last 3
                if 'message' in update:
                    msg = update['message']
                    user = msg.get('from', {})
                    text = msg.get('text', '[No text]')
                    print(f"   - {user.get('first_name', 'Unknown')}: {text[:50]}")
        else:
            print(f"📭 No recent updates (bot hasn't received messages yet)")
    else:
        print(f"❌ Error getting updates")

    return data['ok']

def get_chat_id():
    """Helper: Get your chat ID to send test messages"""
    print("\n👤 Getting your Chat ID...")
    print("-" * 50)

    response = requests.get(f"{API_URL}/getUpdates?limit=1&offset=-1")
    data = response.json()

    if data['ok'] and data['result']:
        update = data['result'][0]
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            user_name = update['message']['from'].get('first_name', 'User')
            print(f"✅ Your Chat ID: {chat_id}")
            print(f"   Name: {user_name}")
            return chat_id

    print("⚠️  No recent messages found.")
    print("   Send /start to the bot first, then run this script again.")
    return None

def send_test_message(chat_id):
    """Test 4: Send a test message"""
    if not chat_id:
        print("\n⚠️  Skipping message test (no chat_id)")
        return False

    print(f"\n✉️  TEST 4: Sending Test Message")
    print("-" * 50)

    message = "🤖 Test message from test_bot_locally.py\n\nBot is working! ✅"

    response = requests.post(f"{API_URL}/sendMessage", data={
        'chat_id': chat_id,
        'text': message
    })

    data = response.json()

    if data['ok']:
        print(f"✅ Message sent successfully!")
    else:
        print(f"❌ Failed to send message: {data}")

    return data['ok']

def main():
    print("=" * 50)
    print("🚀 MINDMATE BOT TESTER")
    print("=" * 50)

    # Run tests
    bot_ok = test_bot_info()

    if not bot_ok:
        print("\n❌ Bot is not accessible. Check your token!")
        return

    webhook_ok = test_webhook()
    updates_ok = test_recent_updates()

    # Optional: Send test message
    chat_id = get_chat_id()
    if chat_id:
        print("\n❓ Do you want to send a test message? (yes/no)")
        answer = input("   > ").strip().lower()
        if answer in ['yes', 'y', 'ha', 'да']:
            send_test_message(chat_id)

    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"   Bot Status: {'✅ ONLINE' if bot_ok else '❌ OFFLINE'}")
    print(f"   Webhook: {'✅ SET' if webhook_ok else '⚠️  NOT SET'}")
    print(f"   Updates: {'✅ WORKING' if updates_ok else '❌ ERROR'}")
    print("=" * 50)

    if bot_ok and updates_ok:
        print("\n✅ Bot is working properly!")
        print("   Now test in Telegram: Send /start to the bot")
    else:
        print("\n⚠️  Some issues detected. Check Render.com logs.")

if __name__ == "__main__":
    main()
