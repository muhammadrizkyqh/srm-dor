# 📖 User Guide - SIRAMA Auto-KRS Bot

## What is this?

SIRAMA Auto-KRS Bot is an automated tool to help you enroll in courses (KRS) at Telkom University without manual clicking. Perfect for getting into popular classes before they fill up!

## Features

### 👥 Multi-Account Support
- Manage multiple SIRAMA accounts
- Help your friends by adding their accounts
- Each account has separate course targets

### 🎯 Smart Targeting
- Set priority for courses (1 = highest priority)
- Auto-enroll enabled courses get enrolled automatically
- Import multiple courses via CSV

### 🚀 Automated Enrollment
- One-click enrollment for all target courses
- Retry mechanism for failed attempts
- Real-time progress tracking

### 📊 Monitoring & Logs
- View enrollment history
- Success/failure statistics
- Export logs to CSV

## How to Use

### 1. Dashboard
Your home page showing:
- Number of accounts
- Total target courses
- Recent activity
- Quick action buttons

### 2. Manage Accounts

#### Add New Account
1. Go to **Manage Accounts** → **Add New Account**
2. Enter your NIM (10 digits)
3. Enter your SIRAMA password
4. Optionally add your name
5. Check "Test connection before saving"
6. Click **Add Account**

The bot will test your credentials before saving. If successful, your account is ready!

#### Edit Account
- Click **Edit** on any account
- Update name or password
- Click **Save Changes**

#### Test Connection
- Click **Test Connection** to verify credentials still work
- Useful to check if password changed

#### Activate/Deactivate
- Active accounts participate in auto-enrollment
- Deactivate temporarily to skip an account

### 3. Target Courses

#### Add Target Course
1. Select an account
2. Go to **Add New Target**
3. Enter **Course ID** (e.g., 18285)
4. Enter **Course Name** (e.g., Algoritma & Pemrograman)
5. Set **Priority** (lower number = higher priority)
6. Enable **Auto-enroll** checkbox
7. Click **Add Target**

#### Manage Targets
- **Enable/Disable Auto-Enroll** - Toggle automatic enrollment
- **Delete** - Remove course from targets
- **Bulk Actions** - Enable/disable all at once

#### Import from CSV
1. Prepare CSV file with columns:
   ```csv
   course_id,course_name,priority
   18285,Algoritma & Pemrograman,1
   18290,Basis Data,2
   18295,Jaringan Komputer,3
   ```
2. Upload CSV file
3. Preview and confirm
4. Click **Import Courses**

### 4. Auto-Enroll

#### Run Now
1. Select account
2. Enter **Enrollment Hash** (see below)
3. Configure retry settings
4. Click **Start Enrollment**
5. Watch progress in real-time!

#### Finding Enrollment Hash
**Method 1 - From HAR File:**
Look in your HAR file for POST requests to `/trans/api/transaction/`, the hash is in the URL.

**Method 2 - From Browser:**
1. Open SIRAMA in Chrome
2. Press F12 → Network tab
3. Manually enroll in any course
4. Find POST request to `transaction`
5. Copy hash from URL

Example URL:
```
https://service-v2.telkomuniversity.ac.id/trans/api/transaction/05d8af8b7a6a9b1a1a16be2841ec0152c8e6ec31
```
Hash: `05d8af8b7a6a9b1a1a16be2841ec0152c8e6ec31`

### 5. View Logs

#### Filter Logs
- **By Account** - See logs for specific account or all
- **By Status** - Filter success/failed only
- **Limit** - Number of logs to show

#### Statistics
- Total attempts
- Success rate
- Failed attempts
- Add vs Drop actions

#### Export
- Download logs as CSV
- Keep records for future reference

## Tips & Tricks

### 🎯 Course Priority Strategy
- Priority 1: Must-have courses (limited seats)
- Priority 2-3: Important but not critical
- Priority 4-5: Optional/backup courses

### ⚡ Enrollment Timing
- Run enrollment right when registration opens
- Have enrollment hash ready beforehand
- Test connection before registration period

### 🔐 Security
- Use strong password for your app account
- Don't share your encryption key
- Regularly update SIRAMA password

### 📊 Monitoring
- Check logs after each enrollment
- Review failed attempts
- Update targets based on results

## Common Questions

**Q: Will this get me banned?**
A: The bot uses the same API as the official website. Use responsibly and don't spam requests.

**Q: Can I run this on multiple computers?**
A: Yes! Your data is stored in Supabase cloud, accessible from anywhere.

**Q: What if enrollment fails?**
A: Check the logs for error messages. Common issues:
- Wrong course ID
- Class already full
- Registration period closed
- Invalid enrollment hash

**Q: Can I schedule enrollment?**
A: Scheduled enrollment is coming soon! For now, use "Run Now" manually.

**Q: How many accounts can I add?**
A: Unlimited! Help your friends by managing their accounts too.

## Troubleshooting

### Enrollment keeps failing
- Verify course ID is correct
- Check if registration is open
- Update enrollment hash
- Test connection to SIRAMA

### Account shows inactive
- Click "Activate" button
- Test connection to verify credentials
- Update password if changed

### Can't find enrollment hash
- Make sure you're looking at POST requests (not GET)
- Check Network tab is recording
- Try in incognito mode to avoid cache

## Support

Need help? Things to check:
1. Read SETUP.md for installation issues
2. Check logs for error messages
3. Verify SIRAMA is accessible
4. Test your credentials manually

Remember: This tool makes enrollment easier, but **always verify your schedule** in SIRAMA after enrollment!
