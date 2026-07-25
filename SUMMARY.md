# StarlyProxy v3.0 - Summary

## 📊 پروژه در یک نگاه

**StarlyProxy v3.0** یک سیستم مدیریت پروکسی حرفه‌ای و چند instance است که به شما امکان می‌دهد:

✅ **چندین پروکسی همزمان** را روی یک سرور مدیریت کنید  
✅ **Paqet و GFK** را به صورت یکپارچه استفاده کنید  
✅ از **پنل وب زیبا** یا **CLI قدرتمند** برای مدیریت استفاده کنید  
✅ **آمار و لاگ** جامع داشته باشید  
✅ **Auto-restart** و monitoring خودکار داشته باشید  

---

## 🏗️ معماری

```
┌─────────────────────────────────────────────────────┐
│                  StarlyProxy v3.0                    │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐│
│  │   Web Panel  │  │     CLI      │  │    API     ││
│  │  (Flask UI)  │  │  (Terminal)  │  │  (REST)    ││
│  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘│
│         │                  │                 │       │
│         └──────────────────┴─────────────────┘       │
│                            │                         │
│                  ┌─────────▼─────────┐               │
│                  │ InstanceManager   │               │
│                  │ (Core Controller) │               │
│                  └─────────┬─────────┘               │
│                            │                         │
│          ┌─────────────────┼─────────────────┐       │
│          │                 │                 │       │
│   ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼─────┐│
│   │   Config    │   │  Database   │   │   Utils    ││
│   │  Manager    │   │   (SQLite)  │   │  (Network) ││
│   └─────────────┘   └─────────────┘   └────────────┘│
│                                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │            Proxy Layer                         │  │
│  │  ┌──────────────────┐  ┌──────────────────┐   │  │
│  │  │  Paqet Wrapper   │  │   GFK Wrapper    │   │  │
│  │  │  (KCP/Raw TCP)   │  │  (QUIC/VIO TCP)  │   │  │
│  │  └──────────────────┘  └──────────────────┘   │  │
│  └───────────────────────────────────────────────┘  │
│                                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │         Instance Processes                     │  │
│  │  [Instance-1] [Instance-2] ... [Instance-N]   │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 📁 ساختار فایل‌ها (خلاصه)

```
StarlyProxy/
├── core/                      # ❤️ هسته اصلی
│   ├── config.py             # مدیریت تنظیمات
│   ├── database.py           # SQLite manager
│   ├── instance_manager.py   # کنترلر اصلی
│   ├── runner.py             # Process runner
│   └── utils.py              # توابع کمکی
│
├── proxy/                     # 🔌 لایه پروکسی
│   ├── paqet_wrapper.py      # Paqet integration
│   ├── gfk_wrapper.py        # GFK integration
│   └── gfk/                  # کد GFK اصلی
│
├── panel/                     # 🌐 پنل وب
│   ├── app.py                # Flask app
│   └── templates/            # HTML صفحات
│
├── cli/                       # 💻 رابط خط فرمان
│   └── starlyproxy-cli.py    # CLI اصلی
│
├── scripts/                   # 🛠️ ابزارهای کمکی
│   ├── health_check.sh       # Health monitoring
│   └── backup.sh             # Backup tool
│
├── install.sh                 # 📦 نصب‌کننده
├── requirements.txt           # 📋 وابستگی‌ها
├── README.md                  # 📖 راهنما
├── CHANGELOG.md               # 📝 تغییرات
└── LICENSE                    # ⚖️ لایسنس
```

---

## 🎯 کاربردها

### 1️⃣ دور زدن فیلترینگ
```bash
# سرور در کشور آزاد
starlyproxy add main paqet client 1.2.3.4:8443 "key"
starlyproxy start main
# → پروکسی در 127.0.0.1:1080
```

### 2️⃣ Load Balancing
```bash
# چند سرور برای توزیع بار
starlyproxy add eu-1 paqet client 45.67.89.1:8443 "key1"
starlyproxy add eu-2 paqet client 45.67.89.2:8443 "key2"
starlyproxy add us-1 paqet client 12.34.56.7:8443 "key3"
starlyproxy start all
# → 3 پروکسی: 1080, 1081, 1082
```

### 3️⃣ Failover / Backup
```bash
# اصلی + بکاپ
starlyproxy add primary paqet client 1.2.3.4:8443 "key-main"
starlyproxy add backup gfk client 5.6.7.8:8443 "key-backup"
starlyproxy start all
# اگر primary مسدود شد → سوییچ به backup
```

### 4️⃣ راه‌اندازی سرور
```bash
# VPS خارج از ایران
starlyproxy add server-main paqet server 0.0.0.0:8443 "shared-key"
starlyproxy start server-main
# کلاینت‌ها به YOUR_IP:8443 وصل می‌شوند
```

---

## 📊 مقایسه با نسخه قبل

| ویژگی | v2.0 | v3.0 |
|-------|------|------|
| **Multi-instance** | محدود (script جداگانه) | ✅ نامحدود (یکپارچه) |
| **Web Panel** | ❌ | ✅ Dashboard کامل |
| **CLI** | bash scripts | ✅ Python CLI حرفه‌ای |
| **Database** | ❌ | ✅ SQLite |
| **Logging** | file ساده | ✅ Structured logs |
| **Stats** | ❌ | ✅ Monitoring جامع |
| **API** | ❌ | ✅ REST API |
| **Auto-restart** | دستی | ✅ خودکار |
| **Health check** | ❌ | ✅ Built-in |
| **Backup** | دستی | ✅ Script خودکار |

---

## 🚀 Quick Start (30 ثانیه)

```bash
# 1. نصب
curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/install.sh | sudo bash

# 2. پنل وب
sudo systemctl start starlyproxy-panel
# → http://YOUR_IP:5000

# 3. افزودن instance
sudo starlyproxy add my-proxy paqet client 1.2.3.4:8443 "SecretKey"

# 4. شروع
sudo starlyproxy start my-proxy

# ✅ پروکسی در 127.0.0.1:1080 آماده است!
```

---

## 🎓 Learning Path

**مبتدی:**
1. نصب با `install.sh`
2. استفاده از پنل وب
3. یک instance اضافه کنید

**متوسط:**
4. آشنایی با CLI
5. چند instance همزمان
6. بررسی logs و stats

**پیشرفته:**
7. استفاده از API
8. راه‌اندازی سرور
9. Automation با scripts

---

## 💡 نکات مهم

⚠️ **همیشه از کلید قوی استفاده کنید** (حداقل 16 کاراکتر)  
⚠️ **آی‌پی VPS را خصوصی نگه دارید**  
⚠️ **به‌روز نگه دارید** (`git pull` در `/opt/starlyproxy`)  
⚠️ **Backup بگیرید** (`scripts/backup.sh`)  
⚠️ **Firewall را تنظیم کنید** (فقط پورت‌های لازم)  

---

## 🆘 پشتیبانی

**مشکل دارید?**
1. راهنمای [Troubleshooting](README.md#troubleshooting) را بخوانید
2. لاگ‌ها را چک کنید: `starlyproxy logs <name>`
3. Issue در GitHub باز کنید
4. به ایمیل پشتیبانی بنویسید: artin@starly.me

---

## 📈 آمار پروژه

- **خطوط کد:** ~3,500+ lines Python
- **ماژول‌ها:** 15+ modules
- **فایل‌های HTML:** 5 templates
- **Scripts:** 10+ helper scripts
- **زمان توسعه:** بازنویسی کامل در 1 روز
- **Commit count:** Fresh v3.0 release

---

## 🙏 تشکر

ممنون از:
- **SamNet-dev** - paqctl base
- **hanselime** - Paqet protocol
- **GFW-knocker** - GFK technique
- **Community** - feedback & testing
- **You** - برای استفاده! ⭐

---

**ساخته شده با ❤️ برای آزادی اینترنت**

**STaRly (Artin) - 2026**
