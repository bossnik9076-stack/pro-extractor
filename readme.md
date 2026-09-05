

# ⚡ HOW IT WORKS

<p align="center">

📄 TXT FILE

⬇️

🤖 TELEGRAM BOT

⬇️

⚙️ PROCESSING

⬇️

✅ RESULT

</p>

---

# ✨ FEATURES

| 🚀 Feature | ⚡ Description |
|---|---|
| 📄 TXT Processing | Process TXT files through Telegram |
| 🤖 Telegram Bot | Simple Telegram interface |
| ⚡ Fast Processing | Designed for quick processing |
| 📱 Termux Ready | Run directly on Android |
| 🐍 Python Powered | Built with Python |
| 🧩 Modular Architecture | Organized project structure |
| 🌐 Flask Server | Web server support |
| 🔧 Custom Configuration | Flexible configuration |
| 🚀 Easy Setup | Simple installation process |

---

# 📱 TERMUX INSTALLATION

### 🟢 STEP 01 — UPDATE TERMUX

    pkg update -y && pkg upgrade -y

### 🟢 STEP 02 — INSTALL REQUIRED PACKAGES

    pkg install python git rust clang make pkg-config openssl libffi -y

### 🟢 STEP 03 — CLONE REPOSITORY

    git clone https://github.com/princepiamotox/Extractor_Pro_x.git

### 🟢 STEP 04 — ENTER PROJECT

    cd Extractor_Pro_x

### 🟢 STEP 05 — UPGRADE PYTHON TOOLS

    pip install --upgrade pip setuptools wheel

### 🟢 STEP 06 — INSTALL MATURIN

    pip install maturin

### 🟢 STEP 07 — INSTALL DEPENDENCIES

    pip install -r requirements.txt

### 🚀 STEP 08 — START BOT

    python -m Extractor

---

# ⚙️ CONFIGURATION

Before starting the bot, configure your required settings.

    API_ID
    API_HASH
    BOT_TOKEN
    BOT_USERNAME
    OWNER_ID
    CHANNEL_ID
    CHANNEL_ID2
    MONGO_URL
    PREMIUM_LOGS
    THUMB_URL

Configure these values according to your own Telegram bot setup.

---

# 🔐 SECURITY

## ⚠️ KEEP YOUR CREDENTIALS PRIVATE

Never publish real credentials inside a public GitHub repository.

Protect:

    🔑 API_ID
    🔐 API_HASH
    🤖 BOT_TOKEN
    🗄️ MONGO_URL

### 🚨 IMPORTANT

If your credentials have already been exposed:

**ROTATE / REVOKE THEM IMMEDIATELY.**

For production environments, use environment variables or a secure secrets manager instead of hard-coding credentials.

---

# 🧩 PROJECT STRUCTURE

    Extractor_Pro_x/
    │
    ├── 🤖 Extractor/
    │   ├── core/
    │   ├── html_converter/
    │   ├── modules/
    │   ├── thumbs/
    │   ├── __init__.py
    │   └── __main__.py
    │
    ├── 🌐 app.py
    ├── ⚙️ config.py
    ├── 🚀 run.py
    ├── 🖥️ server.py
    ├── 🔐 secure.py
    │
    ├── 📦 requirements.txt
    ├── 🐳 Dockerfile
    ├── 🚂 Procfile
    ├── ⚙️ heroku.yml
    └── 📖 README.md

---

# 🛠️ TROUBLESHOOTING

## ❌ MAIN.PY NOT FOUND?

Do not use:

    python main.py

Use:

    python -m Extractor

---

## ❌ PYDANTIC-CORE / MATURIN ERROR?

Install the required build packages:

    pkg install rust clang make pkg-config openssl libffi -y

Upgrade Python tools:

    pip install --upgrade pip setuptools wheel

Install Maturin:

    pip install maturin

Install dependencies:

    pip install -r requirements.txt

Then start the bot:

    python -m Extractor

---



---

# ❤️ SUPPORT THE PROJECT

If you find this project useful:

⭐ Star the repository

🍴 Fork the repository

📢 Share the project

📺 Subscribe to CoreTech AI

<p align="center">
<b>Every ⭐ helps support future projects!</b>
</p>

---

# 📜 DISCLAIMER

This project is provided for **educational and development purposes**.

Use the bot responsibly and ensure that your implementation complies with:

- Telegram Terms & Policies
- Applicable laws
- Third-party service policies
- Copyright requirements
- Privacy requirements

The developer is not responsible for misuse of this project.

---

<p align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=140&color=0:7B2CFF,50:0066FF,100:00F5FF&section=footer&animation=fadeIn" width="100%">

</p>

<p align="center">

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=18&duration=3000&pause=1000&color=00E5FF&center=true&vCenter=true&width=650&lines=⚡+EXTRACTOR+PRO+X;🐍+Python+%2B+Pyrogram;🚀+Built+for+Learning+%26+Development;❤️+Powered+by+CoreTech+AI">

</p>

<p align="center">
<b>⚡ EXTRACTOR PRO X • CORETECH AI ⚡</b>
</p>
