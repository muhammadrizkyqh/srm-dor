# 🚀 Setup Guide

## Prerequisites

- Python 3.10 or higher
- Supabase account (free tier works!)
- SIRAMA account credentials

## Step-by-Step Setup

### 1. Clone & Install

```bash
cd sirama-dor
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Create new project
3. Wait for project to be ready
4. Copy your **Project URL** and **anon/public key**

### 3. Setup Database Tables

In Supabase SQL Editor, run:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: accounts
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    nim TEXT NOT NULL,
    password_encrypted TEXT NOT NULL,
    name TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, nim)
);

-- Table: course_targets
CREATE TABLE course_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    course_id TEXT NOT NULL,
    course_name TEXT,
    priority INTEGER DEFAULT 1,
    auto_enroll BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, course_id)
);

-- Table: enrollment_logs
CREATE TABLE enrollment_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    action TEXT CHECK (action IN ('add', 'drop')),
    course_id TEXT,
    course_name TEXT,
    status TEXT CHECK (status IN ('success', 'failed')),
    message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_accounts_nim ON accounts(nim);
CREATE INDEX idx_course_targets_account_id ON course_targets(account_id);
CREATE INDEX idx_course_targets_priority ON course_targets(account_id, priority);
CREATE INDEX idx_enrollment_logs_account_id ON enrollment_logs(account_id);
CREATE INDEX idx_enrollment_logs_created_at ON enrollment_logs(created_at DESC);

-- Row Level Security (RLS)
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollment_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for accounts
CREATE POLICY "Users can view own accounts"
    ON accounts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own accounts"
    ON accounts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own accounts"
    ON accounts FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own accounts"
    ON accounts FOR DELETE
    USING (auth.uid() = user_id);

-- RLS Policies for course_targets
CREATE POLICY "Users can view own course targets"
    ON course_targets FOR SELECT
    USING (account_id IN (SELECT id FROM accounts WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert own course targets"
    ON course_targets FOR INSERT
    WITH CHECK (account_id IN (SELECT id FROM accounts WHERE user_id = auth.uid()));

CREATE POLICY "Users can update own course targets"
    ON course_targets FOR UPDATE
    USING (account_id IN (SELECT id FROM accounts WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete own course targets"
    ON course_targets FOR DELETE
    USING (account_id IN (SELECT id FROM accounts WHERE user_id = auth.uid()));

-- RLS Policies for enrollment_logs
CREATE POLICY "Users can view own enrollment logs"
    ON enrollment_logs FOR SELECT
    USING (account_id IN (SELECT id FROM accounts WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert own enrollment logs"
    ON enrollment_logs FOR INSERT
    WITH CHECK (account_id IN (SELECT id FROM accounts WHERE user_id = auth.uid()));
```

### 4. Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output (something like: `abcDEF123_random_key_here==`)

### 5. Create .env File

Copy `.env.example` to `.env`:

```bash
copy .env.example .env  # Windows
```

Edit `.env` and fill in your credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your_anon_key_here

# Encryption Key
ENCRYPTION_KEY=your_generated_encryption_key_here==

# App Configuration
DEBUG=True
```

### 6. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## First Time Usage

1. **Register** - Create your account
2. **Add SIRAMA Account** - Add your NIM and password
3. **Set Target Courses** - Select courses you want to enroll
4. **Test Connection** - Verify credentials work
5. **Run Enrollment** - Execute automated enrollment!

## Finding the Enrollment Hash

The enrollment hash is required for adding courses. To find it:

1. Open SIRAMA in Chrome
2. Open DevTools (F12) → Network tab
3. Manually add a course in SIRAMA
4. Look for POST request to `/trans/api/transaction/...`
5. Copy the hash from the URL

Example: `https://service-v2.telkomuniversity.ac.id/trans/api/transaction/05d8af8b7a6a9b1a1a16be2841ec0152c8e6ec31`

The hash is: `05d8af8b7a6a9b1a1a16be2841ec0152c8e6ec31`

## Troubleshooting

### "Configuration Error"
- Make sure `.env` file exists
- Check all values are filled in
- Restart the application

### "Login Failed"
- Verify your SIRAMA credentials
- Check if SIRAMA website is accessible
- Try logging in manually on SIRAMA first

### "Enrollment Failed"
- Make sure you have the correct enrollment hash
- Check if registration period is open
- Verify the course ID is correct

### "Database Error"
- Check Supabase project is active
- Verify database tables are created
- Check RLS policies are enabled

## Security Notes

- **Never commit `.env` file** - It contains sensitive credentials
- Passwords are encrypted using Fernet (symmetric encryption)
- Keep your encryption key safe
- Use strong passwords for your app account

## Need Help?

Check the HAR file (`sirama.har`) for API endpoint examples and request/response formats.
