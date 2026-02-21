# 🚀 Deployment Guide — Halal Stock Screener

## Complete guide to hosting your screener online and sharing it with clients.

---

## ✅ OPTION 1: Streamlit Cloud (FREE — Recommended)

**Best for:** Sharing a public link with clients. Zero server cost. 5-minute setup.

### Step 1 — Create a GitHub Account
Go to [github.com](https://github.com) and sign up for a free account.

### Step 2 — Create a New Repository
1. Click **New Repository**
2. Name it: `halal-stock-screener`
3. Set it to **Public**
4. Click **Create Repository**

### Step 3 — Upload Your Files
Upload all 5 files to the repo:
```
halal-stock-screener/
├── app.py                ← Streamlit web app (main file)
├── halal_screener.py     ← Core screening logic
├── requirements.txt      ← Dependencies
├── my_watchlist.txt      ← Sample watchlist
└── README.md             ← Documentation
```

Either drag & drop in the GitHub web UI or use Git:
```bash
git init
git add .
git commit -m "Initial commit — Halal Stock Screener"
git remote add origin https://github.com/YOUR_USERNAME/halal-stock-screener.git
git push -u origin main
```

### Step 4 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select your repository: `halal-stock-screener`
5. Main file path: `app.py`
6. Click **Deploy!**

⏳ Deployment takes 2–3 minutes.

### Step 5 — Share with Clients
Your app will be live at:
```
https://YOUR_USERNAME-halal-stock-screener-app-XXXXX.streamlit.app
```

Share this URL with clients — they can screen any stocks instantly, no installation needed.

---

## ✅ OPTION 2: Railway (FREE tier, Custom Domain)

**Best for:** More control, custom domain (e.g. halal.yoursite.com)

### Step 1 — Create a Procfile
Create a file named `Procfile` (no extension) with:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Step 2 — Deploy on Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize & deploy
railway init
railway up
```

Then in the Railway dashboard, go to **Settings → Networking → Generate Domain**
to get your custom URL.

---

## ✅ OPTION 3: DigitalOcean Droplet ($6/month)

**Best for:** Production deployment with full control.

### Setup
```bash
# 1. Create Ubuntu 22.04 droplet on DigitalOcean

# 2. SSH into your server
ssh root@YOUR_SERVER_IP

# 3. Install Python and dependencies
apt update && apt install python3-pip -y
pip install streamlit yfinance pandas openpyxl tabulate colorama

# 4. Upload your files (from your local machine)
scp -r halal-stock-screener/ root@YOUR_SERVER_IP:/home/screener/

# 5. Run Streamlit as a background service
nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &

# 6. Access at: http://YOUR_SERVER_IP:8501
```

### Run 24/7 with systemd (production)
```bash
# Create service file
nano /etc/systemd/system/halal-screener.service
```

Paste this:
```ini
[Unit]
Description=Halal Stock Screener
After=network.target

[Service]
User=root
WorkingDirectory=/home/screener
ExecStart=/usr/local/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
systemctl daemon-reload
systemctl enable halal-screener
systemctl start halal-screener
systemctl status halal-screener
```

---

## ✅ OPTION 4: Local Machine (Personal Use Only)

Run it on your own PC/Mac:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Streamlit app
streamlit run app.py

# 3. Opens automatically at http://localhost:8501
```

---

## 🔒 Adding Password Protection (Optional)

To restrict access to paying clients only, add this to the TOP of `app.py`:

```python
import streamlit_authenticator as stauth
# pip install streamlit-authenticator

credentials = {
    "usernames": {
        "client1": {
            "name": "Client One",
            "password": stauth.Hasher(["password123"]).generate()[0]
        }
    }
}
authenticator = stauth.Authenticate(credentials, "halal_app", "auth_cookie", 30)
name, auth_status, username = authenticator.login("Login", "main")

if auth_status is False:
    st.error("Invalid credentials")
    st.stop()
elif auth_status is None:
    st.warning("Please enter your username and password")
    st.stop()
```

---

## 📧 Auto-Email Reports to Clients (Optional)

Add this function to `app.py` to email Excel reports:

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

def send_report_email(to_email: str, excel_bytes: bytes, ticker_list: str):
    """Send Excel screening report via email."""
    msg = MIMEMultipart()
    msg["From"]    = "your@gmail.com"
    msg["To"]      = to_email
    msg["Subject"] = f"🌙 Halal Stock Screening Report — {datetime.now().strftime('%Y-%m-%d')}"

    msg.attach(MIMEText(f"""
    Assalamu Alaykum,

    Please find attached your Halal Stock Screening Report for: {ticker_list}

    This report was generated using AAOIFI Shariah standards.

    ⚠️ For informational purposes only.

    JazakAllah Khair,
    Halal Stock Screener
    """, "plain"))

    # Attach Excel
    part = MIMEBase("application", "octet-stream")
    part.set_payload(excel_bytes)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename="halal_report.xlsx")
    msg.attach(part)

    # Send via Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("your@gmail.com", "YOUR_APP_PASSWORD")
        server.sendmail("your@gmail.com", to_email, msg.as_string())
```

> Note: Use a Gmail **App Password**, not your regular password.
> Settings → Security → 2-Step Verification → App Passwords

---

## 🗂 File Structure Summary

```
halal-stock-screener/
├── app.py                ← 🌐 Streamlit web app (run this)
├── halal_screener.py     ← 🧠 Core screening engine
├── requirements.txt      ← 📦 Python dependencies
├── my_watchlist.txt      ← 📋 Sample client watchlist
├── README.md             ← 📖 Documentation
├── DEPLOY.md             ← 🚀 This file
└── Procfile              ← ⚙️  For Railway deployment (optional)
```

---

## 💡 Pro Tips

- **Update ticker data** is fetched live from Yahoo Finance — no manual updates needed
- **Thresholds** can be adjusted in the sidebar by clients to match their preferred standard
- **Excel reports** are automatically color-coded (green/yellow/red)
- **Mobile friendly** — Streamlit apps work on phones and tablets
- **Rate limits** — Yahoo Finance may rate-limit if screening 30+ tickers. Add a small delay if needed.

---

*Built with QuantGPT | 🌙 May Allah bless your investments. Ameen.*
