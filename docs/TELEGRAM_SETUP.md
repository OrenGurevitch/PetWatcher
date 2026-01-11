# Telegram Notifications Setup - Security-Focused Guide

Complete, secure setup for Telegram notifications with clear explanations of what each piece means.

## ⚠️ Important Security Information

Before you start, understand what you're setting up:

### What Telegram WILL See
- ✅ Images of detections (sent to Telegram servers)
- ✅ Notification messages (text)
- ✅ When notifications are sent (timestamps)

### What Telegram WILL NOT See
- ❌ Your live camera feed (stays on your device)
- ❌ Non-detected images (not sent)
- ❌ Your training data
- ❌ Your local files
- ❌ Real-time monitoring (only gets notifications you send)

### What You're Creating
- A **bot** (like a separate account that sends you messages)
- A **bot token** (password for this bot - keep it secret!)
- A **chat ID** (your Telegram account number)

**If you're not comfortable with images being sent to Telegram servers, use offline mode only.**

---

## Step 1: Create Telegram Bot (2 minutes)

### 1.1 Open Telegram

Download and install:
- **Website:** https://telegram.org/apps
- **iPhone:** App Store → Search "Telegram"
- **Android:** Play Store → Search "Telegram"
- **Desktop:** Download from telegram.org
- **Web:** https://web.telegram.org/ (works in browser)

### 1.2 Find BotFather

BotFather is Telegram's official bot for creating other bots.

1. Open Telegram
2. Click search bar at top
3. Type: `@BotFather` (include the @)
4. Click on the account with the **blue checkmark** (verified)
5. Click "START" or send `/start`

**⚠️ Security Check:**
- Must have blue verified checkmark ✓
- Username is exactly `@BotFather`
- If you see a different account, it's fake!

### 1.3 Create New Bot

In your chat with BotFather, send:
```
/newbot
```

BotFather will ask you questions:

**Question 1: Bot name**
```
BotFather: Alright, a new bot. How are we going to call it?
You type: Pet Camera
```
*(This is the display name - can be anything)*

**Question 2: Bot username**
```
BotFather: Good. Now let's choose a username for your bot.
You type: mypetcamera_bot
```
*(Must end with `bot` or `_bot`, must be unique)*

**If username is taken:**
Try variations:
- `mypetcam123_bot`
- `homepetcamera_bot`
- `yourname_petcam_bot`

### 1.4 Save Your Bot Token

BotFather will respond with:
```
Done! Congratulations on your new bot!

You will find it at t.me/mypetcamera_bot

You can now add a description...

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456789

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

**🔴 CRITICAL - Bot Token:**

The long string `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456789` is your **bot token**.

**What is it?**
- Like a password for your bot
- Anyone with this token can send messages as your bot
- Anyone with this token can send images to your Telegram

**What to do:**
1. Copy it immediately
2. Paste it into a secure note on your device (not in a public place)
3. **NEVER share it publicly**
4. **NEVER commit it to GitHub** (we'll put it in config.json which is ignored by git)
5. **NEVER post it in Discord/forums/screenshots**

**If someone gets your token, they can:**
- Send messages to your Telegram
- Send images to your Telegram
- Spam you

**They CANNOT:**
- Access your Telegram account
- Read your messages
- Access your camera
- Access your computer

**If you accidentally expose it:**
- Go to @BotFather
- Send `/mybots`
- Select your bot
- Select "API Token"
- Select "Revoke current token"
- Get new token

---

## Step 2: Get Your Chat ID (1 minute)

### 2.1 Find Your Bot

1. In Telegram search bar, type your bot username (e.g., `@mypetcamera_bot`)
2. Click on your bot
3. Click "START" button at bottom
4. Send any message (e.g., "hello")

**Why:** The bot needs to receive a message from you first to get your chat ID.

### 2.2 Get Chat ID

**Method 1: Using Browser (Easiest)**

1. Open your web browser (Chrome, Firefox, Safari, etc.)
2. Copy this URL and replace `YOUR_BOT_TOKEN` with your actual bot token:
```
https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
```

**Example:**
If your token is `1234567890:ABCdefGHI`, the URL would be:
```
https://api.telegram.org/bot1234567890:ABCdefGHI/getUpdates
```

3. Paste it in your browser and press Enter

**You'll see JSON data like this:**
```json
{
  "ok": true,
  "result": [{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "from": {
        "id": 987654321,        ← This is your chat ID!
        "first_name": "John",
        "username": "john_doe"
      },
      "chat": {
        "id": 987654321,        ← Or use this one
        "first_name": "John",
        "username": "john_doe",
        "type": "private"
      },
      "text": "hello"
    }
  }]
}
```

4. Find the number after `"chat": { "id":`
5. Copy that number (e.g., `987654321`)

**If you see `"result": []` (empty):**
- You didn't send a message to your bot yet
- Go back to Step 2.1 and send a message
- Refresh the browser page

**🟡 MODERATE - Chat ID:**

**What is it?**
- Your Telegram account number
- Used to identify where to send messages

**Privacy level:**
- Less sensitive than bot token
- Identifies your Telegram account
- Can't be used to send you messages without the bot token
- Not a secret, but don't broadcast it unnecessarily

**Who can find your chat ID:**
- Anyone you message on Telegram can potentially see it
- It's tied to your Telegram account

---

## Step 3: Configure Safely (2 minutes)

### 3.1 Create Config File

1. Open your project folder: `pet-camera/`
2. Create a new file called `config.json` (exactly this name, case-sensitive)
3. Copy this template:

```json
{
  "notifications": {
    "enabled": true,
    "cooldown_seconds": 300,
    "persistence_frames": 5,
    "save_images": true,
    "max_images": 100,
    "platforms": {
      "telegram": {
        "enabled": true,
        "bot_token": "PASTE_YOUR_BOT_TOKEN_HERE",
        "chat_id": "PASTE_YOUR_CHAT_ID_HERE"
      }
    }
  }
}
```

4. Replace `PASTE_YOUR_BOT_TOKEN_HERE` with your bot token from Step 1.4
5. Replace `PASTE_YOUR_CHAT_ID_HERE` with your chat ID from Step 2.2

**Example filled in:**
```json
{
  "notifications": {
    "enabled": true,
    "cooldown_seconds": 300,
    "persistence_frames": 5,
    "save_images": true,
    "max_images": 100,
    "platforms": {
      "telegram": {
        "enabled": true,
        "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
        "chat_id": "987654321"
      }
    }
  }
}
```

**🔴 CRITICAL - Protect This File:**

Your `config.json` contains your bot token!

**DO:**
- ✅ Save it only on your computer
- ✅ Make sure it's in `.gitignore` (it already is)
- ✅ Keep it in the project folder

**DON'T:**
- ❌ Never commit to GitHub
- ❌ Never share in screenshots
- ❌ Never post online
- ❌ Never email it

**Verify it's ignored by git:**
```bash
cat .gitignore | grep config.json
```

You should see: `config.json`

This means git will ignore it (won't push to GitHub). ✅

### 3.2 Install Required Package

```bash
pip install aiohttp
```

This installs the library needed to send HTTP requests to Telegram.

**Security note:** This is an official, widely-used Python package. It's safe.

---

## Step 4: Test Safely (2 minutes)

### 4.1 First Test - Verify Configuration

Before running the full camera, verify your configuration:

```bash
python3 -c "import json; config = json.load(open('config.json')); print('✅ Config loaded'); print(f'Bot token: {config[\"notifications\"][\"platforms\"][\"telegram\"][\"bot_token\"][:20]}...'); print(f'Chat ID: {config[\"notifications\"][\"platforms\"][\"telegram\"][\"chat_id\"]}')"
```

**Expected output:**
```
✅ Config loaded
Bot token: 1234567890:ABCdefGHI...
Chat ID: 987654321
```

**If you see an error:**
- Check `config.json` syntax (commas, quotes, brackets)
- Use a JSON validator: https://jsonlint.com/
- Make sure the file is named exactly `config.json`

### 4.2 Test Notification (Optional Manual Test)

Create a test file `test_telegram.py`:

```python
import asyncio
import aiohttp

async def test_telegram():
    # Replace with your values
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    CHAT_ID = "YOUR_CHAT_ID_HERE"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': '🧪 Test message from pet camera setup'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                print("✅ Success! Check your Telegram")
            else:
                print(f"❌ Error: {await response.text()}")

asyncio.run(test_telegram())
```

Run:
```bash
python3 test_telegram.py
```

**If successful:** You'll get a message in Telegram from your bot! ✅

**Delete test file after:**
```bash
rm test_telegram.py
```

### 4.3 Run Camera with Notifications

```bash
python3 camera.py
```

When a pet is detected for 5 consecutive frames, you'll get a Telegram notification!

---

## Understanding What Happens

### When Detection Occurs:

1. **Local (on your device):**
   - Camera captures frame
   - Model detects pet
   - Image is saved to `snapshots/` folder (local)

2. **Sent to Telegram:**
   - Image file is read from disk
   - HTTP request is sent to Telegram API
   - Image is uploaded to Telegram servers
   - Telegram delivers notification to your phone

3. **What Telegram stores:**
   - The image (on their servers)
   - The message text
   - Timestamp
   - This stays in your chat forever (unless you delete it)

### Privacy Considerations:

**Images sent to Telegram are NOT end-to-end encrypted.**

This means:
- Telegram can technically see the images
- Images are encrypted in transit (HTTPS)
- Images are stored on Telegram servers
- You can delete images from chat (removes from servers)

**If this concerns you:**
- Option 1: Only use text notifications (disable images)
- Option 2: Use console notifications only (local)
- Option 3: Self-host notification system
- Option 4: Accept this tradeoff for convenience

**Your live camera feed NEVER goes to Telegram** - only snapshots you send.

---

## Security Best Practices

### 1. Bot Token Protection

**Store Safely:**
```bash
# Good - In config.json (ignored by git)
config.json

# Bad - In code
bot_token = "123456789:ABC..."  # Don't do this

# Bad - In environment variable in public
export BOT_TOKEN="123456789:ABC..."  # Don't post this
```

**Check git status:**
```bash
git status --ignored
```

You should see `config.json` in ignored files.

### 2. Limit Bot Permissions

Your bot can ONLY:
- Send messages to chats where it's been started
- Send messages to you (after you messaged it first)

Your bot CANNOT:
- Read your other Telegram messages
- Access your contacts
- Join groups without your permission
- Do anything outside of what your code tells it

### 3. Revoke Access Anytime

**If you want to stop the bot:**

1. Go to @BotFather
2. Send `/mybots`
3. Select your bot
4. Select "Delete Bot"
5. Confirm

**This will:**
- Delete the bot completely
- Invalidate the token
- Stop all notifications

**This will NOT:**
- Delete your Telegram account
- Delete past messages (delete those manually)
- Affect any other bots

### 4. Monitor Usage

Check your bot's activity:

1. Go to @BotFather
2. Send `/mybots`
3. Select your bot
4. See info about recent activity

**Look for:**
- Unexpected message counts
- Activity when you're not using it
- Unknown IP addresses (if available)

---

## Common Security Questions

### Q: Can someone hack my Telegram if they get my bot token?

**A:** No. They can only:
- Send messages to **you** via the bot
- Send images to **you** via the bot

They cannot:
- Access your Telegram account
- Read your messages
- Message other people
- Access your contacts

**Worst case:** Spam notifications. Revoke token and create new bot.

### Q: What if I accidentally post my token on GitHub?

**A:** Act immediately:

1. Revoke the token in @BotFather (see Step 3.1 Security)
2. Remove from GitHub:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch config.json" \
     --prune-empty --tag-name-filter cat -- --all
   git push origin --force --all
   ```
3. Create new bot token
4. Update config.json

**Prevention:**
- Never `git add config.json`
- Always check `git status` before commit
- Use `.gitignore` (already configured)

### Q: Can Telegram read my images?

**A:** Technically yes. Images are stored on Telegram servers (not end-to-end encrypted). Telegram's privacy policy applies.

**In practice:**
- Telegram encrypts data in transit
- Images are tied to your private bot chat
- Telegram states they don't scan private messages
- But technically they could if they wanted to

**If concerned:** Use offline mode only.

### Q: What happens if I delete messages in Telegram?

**A:** Deleting messages from your chat removes them from Telegram servers. They're gone.

### Q: Can I see what my bot is doing?

**A:** Yes, check the console output when camera runs:
```
🔔 Sending notification: Fluffy detected
✅ Notification sent successfully
```

---

## Troubleshooting

### Error: "401 Unauthorized"

**Cause:** Wrong bot token

**Fix:**
1. Go to @BotFather
2. Send `/mybots`
3. Select your bot
4. Select "API Token"
5. Copy the token again
6. Update `config.json`

### Error: "400 Bad Request: chat not found"

**Cause:** Wrong chat ID or didn't message bot first

**Fix:**
1. Open Telegram, find your bot
2. Send "hello" to the bot
3. Refresh the `/getUpdates` URL in your browser
4. Copy the chat ID again
5. Update `config.json`

### Not Getting Notifications

**Check:**
1. Is `config.json` in the same folder as `camera.py`?
2. Did you run `pip install aiohttp`?
3. Check console for error messages
4. Try manual test (Step 4.2)

### Too Many Notifications

**Fix:** Edit `config.json`:
```json
{
  "cooldown_seconds": 600,    // 10 minutes instead of 5
  "persistence_frames": 10    // More confident detection
}
```

---

## Alternative: Disable Telegram (Privacy Mode)

If you don't trust Telegram or want to keep everything local:

**Option 1: Console Only**

Don't create `config.json`. The camera will just print detections to console.

**Option 2: Local Snapshots Only**

Set in `config.json`:
```json
{
  "notifications": {
    "enabled": false,    // No Telegram
    "save_images": true  // Save locally only
  }
}
```

Images saved to `snapshots/` folder, never sent anywhere.

**Option 3: Different Platform**

Use Discord, custom webhook, or email instead. See `NOTIFICATIONS_GUIDE.md`.

---

## Summary

### What You Created:
- ✅ A bot (separate account for sending notifications)
- ✅ Bot token (password for bot - keep secret)
- ✅ Chat ID (your Telegram account number)

### What Gets Sent to Telegram:
- Detection snapshots (images)
- Detection messages (text)

### What Stays Local:
- Live camera feed
- All other images
- Training data
- Your model

### How to Stay Safe:
- ✅ Never share bot token
- ✅ Keep `config.json` local (don't commit to git)
- ✅ Delete bot anytime in @BotFather
- ✅ Use long cooldown (fewer notifications)
- ✅ Delete old messages in Telegram to remove images

**You're now set up securely!** 🔒

If you have concerns about privacy, remember: you can always run in offline mode and skip notifications entirely.
