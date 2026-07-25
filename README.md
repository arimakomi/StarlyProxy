# StarlyProxy v3.0

<div align="center">

```
   _____ _             _         ____                       
  / ____| |           | |       |  _ \                      
 | (___ | |_ __ _ _ __| |_   _  | |_) | __ _ __  _ __ __ __ 
  \___ \| __/ _` | '__| | | | | |  _ < / _` |\ \/ / '__|\/ /
  ____) | || (_| | |  | | |_| | | |_) | (_| | >  <| |    >  < 
 |_____/ \__\__,_|_|  |_|\__, | |____/ \__,_|/_/\_\_|   /_/\_\
                          __/ |
                         |___/
```

**مدیریت پیشرفته و یکپارچه پروکسی چند instance**

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/arimakomi/StarlyProxy/releases)
[![License](https://img.shields.io/badge/license-AGPL--3.0-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org)

[فارسی](#persian) | [English](#english)

---

</div>

<a id="persian"></a>

## 🎯 ویژگی‌های جدید v3.0

**StarlyProxy v3.0** یک بازنویسی کامل و حرفه‌ای است که قابلیت‌های زیر را ارائه می‌دهد:

### 🚀 مدیریت چند Instance
- **نامحدود instance همزمان** روی یک سرور
- مدیریت مستقل هر instance با config جداگانه
- پورت‌های SOCKS خودکار و بدون تداخل
- پشتیبانی از Paqet و GFK به صورت همزمان

### 🎨 پنل وب زیبا و کاربرپسند
- Dashboard زنده با نمایش real-time
- مدیریت کامل instance ها از مرورگر
- نمودارها و آمار استفاده
- نمایش لاگ‌ها و monitoring

### ⚡ CLI قدرتمند
- دستورات ساده و فارسی
- مدیریت سریع از terminal
- اسکریپت‌نویسی و automation

### 💾 مدیریت هوشمند
- SQLite database برای ذخیره configs
- Auto-restart برای پایداری
- Logging جامع و قابل جستجو
- Stats و monitoring منابع

---

## 📋 فهرست مطالب

- [پیش‌نیازها](#prerequisites)
- [نصب سریع](#quick-install)
- [راه‌اندازی اولیه](#getting-started)
- [استفاده از CLI](#cli-usage)
- [استفاده از پنل وب](#web-panel)
- [مثال‌های کاربردی](#examples)
- [ساختار پروژه](#structure)
- [API Documentation](#api)
- [عیب‌یابی](#troubleshooting)

---

<a id="prerequisites"></a>

## ⚙️ پیش‌نیازها

### سرور (VPS)
- لینوکس (Ubuntu 20.04+، Debian 10+، CentOS 8+)
- Python 3.7 یا بالاتر
- حداقل 512MB RAM
- دسترسی root

### کلاینت
- ویندوز 10+، macOS 10.14+، یا لینوکس
- Python 3.7+ (برای GFK)
- دسترسی Administrator/root

---

<a id="quick-install"></a>

## 🚀 نصب سریع (یک خط!)

### سرور

```bash
curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/install.sh | sudo bash
```

این اسکریپت:
- تمام وابستگی‌ها را نصب می‌کند
- StarlyProxy را دانلود و راه‌اندازی می‌کند
- CLI را در سیستم فعال می‌کند
- پنل وب را به عنوان سرویس systemd می‌سازد

---

<a id="getting-started"></a>

## 🎬 راه‌اندازی اولیه

### 1️⃣ شروع پنل وب

```bash
sudo systemctl start starlyproxy-panel
sudo systemctl enable starlyproxy-panel  # فعال‌سازی خودکار
```

پنل وب در آدرس زیر در دسترس خواهد بود:
```
http://YOUR_SERVER_IP:5000
```

### 2️⃣ افزودن اولین Instance (CLI)

```bash
# مثال: افزودن یک Paqet client
sudo starlyproxy add my-proxy paqet client 1.2.3.4:8443 "MySecretKey2024"

# مثال: افزودن یک GFK client
sudo starlyproxy add gfk-iran gfk client 5.6.7.8:8443 "AnotherSecureKey"
```

### 3️⃣ شروع Instance

```bash
sudo starlyproxy start my-proxy
```

### 4️⃣ بررسی وضعیت

```bash
sudo starlyproxy status my-proxy
```

---

<a id="cli-usage"></a>

## 💻 راهنمای کامل CLI

### لیست کردن Instance ها

```bash
starlyproxy list
```

خروجی:
```
نام                  نوع      حالت     وضعیت      پورت SOCKS    سرور
====================================================================================
my-proxy             paqet    client   running    1080          1.2.3.4:8443
gfk-iran             gfk      client   stopped    1081          5.6.7.8:8443
```

### افزودن Instance جدید

```bash
starlyproxy add <name> <type> <mode> <server> <key> [options]
```

**پارامترها:**
- `name`: نام یکتا (فقط حروف، اعداد، خط تیره)
- `type`: `paqet` یا `gfk`
- `mode`: `client` یا `server`
- `server`: آدرس سرور به فرمت `IP:PORT`
- `key`: کلید رمزنگاری (حداقل 16 کاراکتر)

**گزینه‌های اضافی:**
- `--profile <name>`: پروفایل عملکرد (`standard`، `high-loss`، `cdn`، `gaming`)
- `--no-auto-restart`: غیرفعال کردن ریستارت خودکار

**مثال‌ها:**

```bash
# Client ساده
starlyproxy add germany paqet client 45.67.89.10:8443 "MyKey123456789"

# Client با پروفایل gaming
starlyproxy add game-server paqet client 12.34.56.78:8443 "GameKey" --profile gaming

# GFK برای سانسور سنگین
starlyproxy add iran-bypass gfk client 98.76.54.32:8443 "SecurePass2024"
```

### کنترل Instance ها

```bash
# شروع
starlyproxy start <name>
starlyproxy start all          # شروع همه

# توقف
starlyproxy stop <name>
starlyproxy stop all           # توقف همه
starlyproxy stop <name> -f     # توقف اجباری

# ریستارت
starlyproxy restart <name>
```

### نمایش وضعیت

```bash
starlyproxy status <name>
```

خروجی:
```
==================================================
📊 وضعیت Instance: my-proxy
==================================================
نوع: paqet
حالت: client
وضعیت: running
پورت SOCKS: 1080
سرور: 1.2.3.4:8443
PID: 12345
CPU: 2.3%
Memory: 45.2 MB
Uptime: 2h 15m 30s
==================================================
```

### نمایش لاگ‌ها

```bash
starlyproxy logs <name>           # لاگ یک instance
starlyproxy logs                  # لاگ همه
starlyproxy logs <name> -n 200    # 200 خط آخر
```

### حذف Instance

```bash
starlyproxy delete <name>         # با تایید
starlyproxy delete <name> -y      # بدون تایید
```

---

<a id="web-panel"></a>

## 🌐 پنل وب

### دسترسی

پنل وب در آدرس `http://SERVER_IP:5000` در دسترس است.

### صفحات

#### 1. داشبورد (`/`)
- نمای کلی تمام instance ها
- آمار سریع (تعداد کل، در حال اجرا، متوقف)
- اطلاعات سیستم
- لیست instance های اخیر

#### 2. مدیریت Instance ها (`/instances`)
- جدول کامل تمام instance ها
- دکمه‌های سریع: Start, Stop, Restart, Delete
- فیلتر و جستجو
- لینک به صفحه جزئیات

#### 3. افزودن Instance (`/add`)
- فرم ساده و راهنمای کامل
- Validation خودکار
- انتخاب پروفایل عملکرد

#### 4. جزئیات Instance (`/instance/<name>`)
- اطلاعات کامل instance
- نمایش منابع (CPU, Memory, Uptime)
- لاگ‌های real-time
- نمودار آمار 24 ساعت
- کنترل‌های مدیریتی

### API Endpoints

تمام عملیات از طریق REST API نیز قابل دسترسی هستند:

```bash
# لیست instance ها
GET /api/instances

# وضعیت یک instance
GET /api/instance/<name>/status

# شروع
POST /api/instance/<name>/start

# توقف
POST /api/instance/<name>/stop
POST /api/instance/<name>/stop  {"force": true}

# ریستارت
POST /api/instance/<name>/restart

# حذف
DELETE /api/instance/<name>/delete

# لاگ‌ها
GET /api/instance/<name>/logs?limit=100

# آمار
GET /api/instance/<name>/stats?hours=24

# اطلاعات سیستم
GET /api/system
```

**مثال با curl:**

```bash
# لیست
curl http://localhost:5000/api/instances

# شروع instance
curl -X POST http://localhost:5000/api/instance/my-proxy/start

# دریافت لاگ‌ها
curl http://localhost:5000/api/instance/my-proxy/logs?limit=50
```

---

<a id="examples"></a>

## 📚 مثال‌های کاربردی

### سناریو 1: یک Client ساده

```bash
# نصب
curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/install.sh | sudo bash

# شروع پنل
sudo systemctl start starlyproxy-panel

# افزودن instance
sudo starlyproxy add main-proxy paqet client 1.2.3.4:8443 "MySecretKey"

# شروع
sudo starlyproxy start main-proxy

# بررسی
sudo starlyproxy status main-proxy
```

حالا پروکسی SOCKS5 شما در `127.0.0.1:1080` فعال است!

### سناریو 2: چند سرور برای Load Balancing

```bash
# سرور آلمان
sudo starlyproxy add germany paqet client 45.67.89.10:8443 "KeyGermany"

# سرور فرانسه
sudo starlyproxy add france paqet client 12.34.56.78:8443 "KeyFrance"

# سرور هلند
sudo starlyproxy add netherlands paqet client 98.76.54.32:8443 "KeyNetherlands"

# شروع همه
sudo starlyproxy start all
```

حالا سه پروکسی دارید:
- Germany: `127.0.0.1:1080`
- France: `127.0.0.1:1081`
- Netherlands: `127.0.0.1:1082`

### سناریو 3: Main + Backup

```bash
# اصلی (سرعت بالا)
sudo starlyproxy add main paqet client 1.2.3.4:8443 "MainKey" --profile cdn

# بکاپ (پایدار)
sudo starlyproxy add backup gfk client 5.6.7.8:8443 "BackupKey" --profile standard

# شروع هر دو
sudo starlyproxy start all
```

از main استفاده کنید، اگر مسدود شد به backup سوییچ کنید.

### سناریو 4: راه‌اندازی سرور

```bash
# نصب روی VPS
curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/install.sh | sudo bash

# ساخت instance سرور
sudo starlyproxy add server-main paqet server 0.0.0.0:8443 "SharedKeyForClients"

# شروع
sudo starlyproxy start server-main

# بررسی
sudo starlyproxy status server-main
sudo starlyproxy logs server-main
```

حالا کلاینت‌ها می‌توانند به `YOUR_VPS_IP:8443` متصل شوند.

---

<a id="structure"></a>

## 📁 ساختار پروژه

```
StarlyProxy/
├── core/                      # هسته اصلی
│   ├── __init__.py
│   ├── config.py             # مدیریت پیکربندی
│   ├── database.py           # SQLite manager
│   ├── instance_manager.py   # مدیریت instance ها
│   └── utils.py              # توابع کمکی
│
├── proxy/                     # موتورهای پروکسی
│   ├── paqet/                # Paqet wrapper
│   └── gfk/                  # GFW-Knocker
│       ├── client/
│       │   ├── mainclient.py
│       │   ├── quic_client.py
│       │   └── vio_client.py
│       └── server/
│           ├── mainserver.py
│           ├── quic_server.py
│           └── vio_server.py
│
├── panel/                     # پنل وب Flask
│   ├── app.py                # Application اصلی
│   ├── templates/            # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── instances.html
│   │   ├── instance_detail.html
│   │   └── add_instance.html
│   └── static/               # CSS, JS, assets
│
├── cli/                       # Command Line Interface
│   └── starlyproxy-cli.py    # CLI اصلی
│
├── scripts/                   # اسکریپت‌های کمکی
│   ├── health_check.sh
│   └── backup.sh
│
├── install.sh                 # نصب‌کننده خودکار
├── requirements.txt           # وابستگی‌های Python
├── README.md                  # این فایل
└── LICENSE                    # AGPL-3.0
```

---

<a id="api"></a>

## 🔌 API Documentation

### Base URL

```
http://YOUR_SERVER:5000/api
```

### Authentication

فعلاً نیاز به احراز هویت نیست. در نسخه‌های بعدی API token اضافه خواهد شد.

### Endpoints

#### GET `/instances`

لیست تمام instance ها.

**Response:**
```json
[
  {
    "name": "my-proxy",
    "type": "paqet",
    "mode": "client",
    "status": "running",
    "socks_port": 1080,
    "server_address": "1.2.3.4:8443",
    "pid": 12345
  }
]
```

#### GET `/instance/<name>/status`

وضعیت کامل یک instance.

**Response:**
```json
{
  "name": "my-proxy",
  "type": "paqet",
  "mode": "client",
  "actual_status": "running",
  "socks_port": 1080,
  "server_address": "1.2.3.4:8443",
  "pid": 12345,
  "cpu_percent": 2.3,
  "memory_mb": 45.2,
  "uptime": 8130
}
```

#### POST `/instance/<name>/start`

شروع instance.

**Response:**
```json
{
  "success": true,
  "message": "Instance my-proxy started"
}
```

#### POST `/instance/<name>/stop`

توقف instance.

**Body (optional):**
```json
{
  "force": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Instance my-proxy stopped"
}
```

#### POST `/instance/<name>/restart`

ریستارت instance.

**Response:**
```json
{
  "success": true,
  "message": "Instance my-proxy restarted"
}
```

#### DELETE `/instance/<name>/delete`

حذف instance.

**Response:**
```json
{
  "success": true,
  "message": "Instance my-proxy deleted"
}
```

#### GET `/instance/<name>/logs?limit=100`

دریافت لاگ‌ها.

**Query Parameters:**
- `limit`: تعداد خطوط (پیش‌فرض: 100)

**Response:**
```json
[
  {
    "id": 123,
    "instance_name": "my-proxy",
    "level": "INFO",
    "message": "Connection established",
    "timestamp": "2026-07-25 10:30:00"
  }
]
```

#### GET `/instance/<name>/stats?hours=24`

آمار استفاده.

**Query Parameters:**
- `hours`: بازه زمانی (پیش‌فرض: 24)

**Response:**
```json
[
  {
    "id": 456,
    "instance_name": "my-proxy",
    "timestamp": "2026-07-25 10:00:00",
    "bytes_sent": 1024000,
    "bytes_received": 2048000,
    "connections": 15
  }
]
```

#### GET `/system`

اطلاعات سیستم.

**Response:**
```json
{
  "os": "Linux",
  "os_version": "5.15.0",
  "hostname": "myserver",
  "cpu_count": 4,
  "memory_total_gb": 8.0,
  "python_version": "3.10.5"
}
```

---

<a id="troubleshooting"></a>

## 🔧 عیب‌یابی

### مشکل: پورت 5000 قبلاً استفاده شده

**راه‌حل:**
```bash
# تغییر پورت پنل وب
sudo nano /etc/systemd/system/starlyproxy-panel.service
# خط ExecStart را تغییر دهید و --port 8080 اضافه کنید
sudo systemctl daemon-reload
sudo systemctl restart starlyproxy-panel
```

### مشکل: Instance شروع نمی‌شود

**بررسی:**
```bash
# لاگ‌ها را چک کنید
sudo starlyproxy logs <name>

# دسترسی root را بررسی کنید
whoami  # باید root باشد

# وابستگی‌ها را بررسی کنید
python3 -m pip list | grep -E 'scapy|aioquic|flask'
```

### مشکل: "Permission denied" در لینوکس

**راه‌حل:**
```bash
# با sudo اجرا کنید
sudo starlyproxy start <name>

# یا صلاحیت دهید
sudo chmod +x /usr/local/bin/starlyproxy
```

### مشکل: پورت SOCKS به درخواست پاسخ نمی‌دهد

**بررسی:**
```bash
# وضعیت instance
sudo starlyproxy status <name>

# چک کنید process واقعاً در حال اجراست
ps aux | grep <instance-name>

# تست پورت
nc -zv 127.0.0.1 1080
```

### مشکل: Gateway MAC پیدا نمی‌شود

**راه‌حل:**
```bash
# یک بار به gateway پینگ بزنید
ping -c 1 $(ip route | grep default | awk '{print $3}')

# سپس ARP را چک کنید
ip neigh show

# یا دستی در config وارد کنید
```

### مشکل: Instance بعد از reboot خاموش می‌شود

**راه‌حل:**
```bash
# Auto-restart را فعال کنید
# در config instance، auto_restart: true قرار دهید
```

---

## 🤝 مشارکت

این پروژه Open Source است و از مشارکت شما استقبال می‌کنیم!

1. Fork کنید
2. یک branch جدید بسازید (`git checkout -b feature/AmazingFeature`)
3. تغییرات را commit کنید (`git commit -m 'Add some AmazingFeature'`)
4. Push کنید (`git push origin feature/AmazingFeature`)
5. یک Pull Request باز کنید

---

## 📄 لایسنس

این پروژه تحت لایسنس **AGPL-3.0** منتشر شده است.

برای جزئیات بیشتر فایل [LICENSE](./LICENSE) را مطالعه کنید.

---

## 🙏 قدردانی

StarlyProxy بر پایه پروژه‌های عالی زیر ساخته شده:

- [paqctl](https://github.com/SamNet-dev/paqctl) - مدیریت Paqet
- [paqet](https://github.com/hanselime/paqet) - KCP over raw TCP
- [gfw_resist_tcp_proxy](https://github.com/GFW-knocker/gfw_resist_tcp_proxy) - GFW bypass
- [aioquic](https://github.com/aiortc/aioquic) - QUIC implementation
- [scapy](https://scapy.net/) - Packet manipulation

---

## 💬 پشتیبانی

- 🐛 گزارش باگ: [GitHub Issues](https://github.com/arimakomi/StarlyProxy/issues)
- 💡 پیشنهادات: [GitHub Discussions](https://github.com/arimakomi/StarlyProxy/discussions)
- 📧 ایمیل: artin@starly.me

---

<div align="center">

**ساخته شده با ❤️ توسط [STaRly (Artin)](https://github.com/arimakomi)**

⭐ اگر این پروژه برایتان مفید بود، یک ستاره بدهید!

</div>
