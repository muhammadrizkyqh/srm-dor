# 🎓 SIRAMA Auto-KRS Bot

Aplikasi otomatis untuk pengambilan KRS (Kartu Rencana Studi) di SIRAMA Telkom University dengan dukungan multi-account management.

## ✨ Features

- 🔐 **Multi-Account Management** - Kelola multiple akun SIRAMA sekaligus
- 🎯 **Smart Course Targeting** - Set prioritas matkul yang ingin diambil
- ⚡ **Auto-Enrollment** - Otomatis ambil KRS sesuai jadwal
- 📊 **Real-time Monitoring** - Lihat logs dan status enrollment
- 🔒 **Secure** - Password terenkripsi di database
- ⏰ **Scheduled Tasks** - Jalankan otomatis di waktu yang ditentukan

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.10+
- **Database**: Supabase (PostgreSQL)
- **Scheduler**: APScheduler

## 📦 Installation

1. Clone repository:
```bash
git clone <your-repo-url>
cd sirama-dor
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment variables:
```bash
copy .env.example .env
# Edit .env dengan credentials Supabase Anda
```

5. Generate encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 🗄️ Database Setup

Run these SQL commands in Supabase SQL Editor:

```sql
-- Table: accounts
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    nim TEXT NOT NULL,
    password_encrypted TEXT NOT NULL,
    name TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: course_targets
CREATE TABLE course_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    course_id TEXT NOT NULL,
    course_name TEXT,
    priority INTEGER DEFAULT 1,
    auto_enroll BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
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
CREATE INDEX idx_course_targets_account_id ON course_targets(account_id);
CREATE INDEX idx_enrollment_logs_account_id ON enrollment_logs(account_id);
CREATE INDEX idx_enrollment_logs_created_at ON enrollment_logs(created_at DESC);
```

## 🚀 Usage

Run the application:
```bash
streamlit run app.py
```

Open browser at `http://localhost:8501`

## 📝 How It Works

1. **Register/Login** - Buat akun menggunakan Supabase Auth
2. **Add SIRAMA Account** - Tambahkan NIM dan password SIRAMA
3. **Set Target Courses** - Pilih matkul yang ingin diambil dengan priority
4. **Schedule/Run** - Jalankan manual atau schedule untuk auto-run
5. **Monitor** - Lihat hasil enrollment di dashboard logs

## 🔒 Security

- Password SIRAMA dienkripsi menggunakan Fernet (symmetric encryption)
- Session management via Supabase Auth
- Environment variables untuk sensitive data

## 📄 License

MIT License

## 👨‍💻 Developer

Developed with ❤️ for Telkom University students
