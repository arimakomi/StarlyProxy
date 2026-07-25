```
   _____ _             _         ____                       
  / ____| |           | |       |  _ \                      
 | (___ | |_ __ _ _ __| |_   _  | |_) | __ _ __  _ __ __ __ 
  \___ \| __/ _` | '__| | | | | |  _ < / _` |\ \/ / '__|\ \/ /
  ____) | || (_| | |  | | |_| | | |_) | (_| | >  <| |    >  < 
 |_____/ \__\__,_|_|  |_|\__, | |____/ \__,_|/_/\_\_|   /_/\_\
                          __/ |
                         |___/
```

<div align="center">

**StarlyProxy** — مدیریت شخصی‌سازی‌شده پروکسی برای دور زدن فایروال

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/arimakomi/StarlyProxy/releases)
[![License](https://img.shields.io/badge/license-AGPL--3.0-green.svg)](./LICENSE)
[![Server](https://img.shields.io/badge/server-Linux-lightgrey.svg)](#)
[![Client](https://img.shields.io/badge/client-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#)
[![Multi--Server](https://img.shields.io/badge/multi--server-supported-orange.svg)](./MULTI-SERVER.md)

[English version below](#english)

</div>

---

# نسخه فارسی

## این چیست؟

**StarlyProxy** ابزار شخصی من برای مدیریت پروکسی‌های دور زدن فایروال است. این پروژه بر پایه‌ی موتور اثبات‌شده‌ی [paqctl](https://github.com/SamNet-dev/paqctl) ساخته شده و باهاش شخصی‌سازی شده — یعنی نصب‌کننده و منطق اصلی همون paqctl قابل‌اعتماده، ولی روش استفاده، مدیریت چندسروری، مستندات، و برندینگ کاملاً مال StarlyProxy‌ه.

با StarlyProxy می‌تونی به سروری خارج از شبکه محدود (مثلاً پشت فایروال بزرگ) وصل بشی و آزادانه به اینترنت دسترسی داشته باشی. کامپوننت **سرور** رو روی یک VPS نصب می‌کنی و **کلاینت** رو روی ویندوز/مک/لینوکس خودت اجرا می‌کنی.

## ویژگی‌های کلیدی

- **دو روش دور زدن فایروال**: Paqet (ساده، سریع) و GFW-Knocker (پیشرفته، برای سانسور سنگین)
- **چند سرور هم‌زمان**: با ابزار [مدیریت چندسروری](./MULTI-SERVER.md) هرچقدر سرور بخوای، هم‌زمان و مستقل از هم
- **تشخیص خودکار شبکه**: اینترفیس، آی‌پی محلی و مک گیت‌وی خودکار پیدا می‌شن
- **پروفایل‌های عملکرد آماده**: استاندارد، ضدپکت‌لاس، پرسرعت/CDN، کم‌تاخیر/گیمینگ
- **حالت توربوی سیستم‌عامل**: فعال‌سازی یک‌کلیکی TCP BBR و افزایش بافر شبکه
- **واچ‌داگ خودکار**: پایش و ریکاوری بدون قطعی سرویس
- **مدیریت کامل از CLI**: نصب، وضعیت، لاگ، بن/آنبن آی‌پی، چرخش کلید، بکاپ/بازیابی

## دو روش

| | **Paqet** | **GFW-Knocker (GFK)** |
|---|---|---|
| **سختی** | آسان ⭐ | پیشرفته ⭐⭐⭐ |
| **مناسب برای** | اکثر شرایط | سانسور سنگین (GFW) |
| **پروکسی شما** | `127.0.0.1:1080` | `127.0.0.1:14000` |
| **تکنولوژی** | KCP روی raw socket | TCP نقض‌شده + تونل QUIC |
| **نیاز سرور** | فقط باینری paqet | GFK + Xray |

> **نکته:** می‌تونی هر دو رو هم‌زمان نصب کنی و یکی رو به‌عنوان بکاپ نگه داری — از پورت‌های متفاوتی استفاده می‌کنن.

### کدوم رو انتخاب کنم؟

اگه شبکه‌ت سانسور سنگین داره (مثل ایران یا فایروال بزرگ چین)، اول **GFK** رو امتحان کن. در غیر این‌صورت **Paqet** برای اکثر شرایط کافیه و سریع‌تر و ساده‌تره.

## معماری

**Paqet (ساده):**
```
[مرورگر] --> [Paqet Client] --KCP/Raw TCP--> [Paqet Server] --SOCKS5--> [اینترنت]
              127.0.0.1:1080                  your.vps.ip
```

**GFW-Knocker (پیشرفته):**
```
[مرورگر] --> [GFK Client] --TCP نقض‌شده--> [GFK Server] --> [Xray] --> [اینترنت]
              (VIO+QUIC)                     (تونل QUIC)     (SOCKS5)
              127.0.0.1:14000                 your.vps.ip
```

## شروع سریع

### ۱. راه‌اندازی سرور (روی VPS لینوکس)

```bash
curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/paqctl.sh | sudo bash
sudo paqctl menu
```

بعد از راه‌اندازی، اطلاعات اتصال (آی‌پی، پورت، کلید) رو بگیر:

```bash
sudo paqctl info
```

> اسم دستور همچنان `paqctl` می‌مونه — StarlyProxy روی همین موتور نصب‌شده کار می‌کنه، فقط برندینگ و لایه مدیریتی بالاترش (مثل مدیریت چندسروری) مال StarlyProxy‌ه.

### ۲. راه‌اندازی کلاینت

<details>
<summary><strong>🪟 ویندوز</strong></summary>

**روش آسان:**
1. برو به [https://github.com/arimakomi/StarlyProxy](https://github.com/arimakomi/StarlyProxy) → **Code** → **Download ZIP**
2. پوشه `windows` رو باز کن
3. روی `Paqet-Client.bat` راست‌کلیک → **Run as administrator**
4. اطلاعات سرور (آدرس + کلید) رو وارد کن → **Connect**

**روش پیشرفته (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/windows/paqet-client.ps1 | iex
```
اگه خطای اجرای اسکریپت دیدی:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

مرورگر: SOCKS5 → `127.0.0.1:1080` (Paqet) یا `127.0.0.1:14000` (GFK)
</details>

<details>
<summary><strong>🍎 macOS</strong></summary>

```bash
mkdir -p ~/starlyproxy && cd ~/starlyproxy
curl -LO https://github.com/hanselime/paqet/releases/download/v1.0.0-alpha.20/paqet-darwin-amd64-v1.0.0-alpha.20.tar.gz
tar -xzf paqet-darwin-amd64-v1.0.0-alpha.20.tar.gz
chmod +x paqet_darwin_amd64

cat > config.yaml << 'EOF'
role: "client"
socks5:
  - listen: "127.0.0.1:1080"
network:
  interface: "en0"
  ipv4:
    addr: "YOUR_LOCAL_IP:0"
    router_mac: "YOUR_ROUTER_MAC"
server:
  addr: "YOUR_SERVER_IP:8443"
transport:
  protocol: "kcp"
  kcp:
    mode: "fast"
    key: "YOUR_SECRET_KEY"
EOF

sudo ./paqet_darwin_amd64 run -c config.yaml
```
برای Apple Silicon فایل `arm64` رو دانلود کن. آی‌پی محلی: `ifconfig en0 | grep inet`، مک گیت‌وی: `arp -a | grep gateway`.
</details>

<details>
<summary><strong>🐧 لینوکس</strong></summary>

```bash
mkdir -p ~/starlyproxy && cd ~/starlyproxy
curl -LO https://github.com/hanselime/paqet/releases/download/v1.0.0-alpha.20/paqet-linux-amd64-v1.0.0-alpha.20.tar.gz
tar -xzf paqet-linux-amd64-v1.0.0-alpha.20.tar.gz
chmod +x paqet_linux_amd64

cat > config.yaml << 'EOF'
role: "client"
socks5:
  - listen: "127.0.0.1:1080"
network:
  interface: "eth0"
  ipv4:
    addr: "YOUR_LOCAL_IP:0"
    router_mac: "YOUR_ROUTER_MAC"
server:
  addr: "YOUR_SERVER_IP:8443"
transport:
  protocol: "kcp"
  kcp:
    mode: "fast"
    key: "YOUR_SECRET_KEY"
EOF

sudo ./paqet_linux_amd64 run -c config.yaml
```
یا خیلی ساده‌تر، از خود اسکریپت `paqctl.sh` روی همون دستگاه استفاده کن تا شبکه رو خودکار تشخیص بده.
</details>

## 🔀 اتصال به چند سرور هم‌زمان

اگه می‌خوای هم‌زمان به **چند سرور مختلف** وصل بشی (مثلاً اصلی + بکاپ، یا چند منطقه)، از **[paqet-multi.sh](./paqet-multi.sh)** استفاده کن — بخشی از StarlyProxy که هرچقدر سرور بخوای، هرکدوم با کانفیگ، پورت SOCKS5 (خودکار) و سرویس systemd مستقل خودشون مدیریت می‌کنه.

```bash
curl -sLO https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/paqet-multi.sh
chmod +x paqet-multi.sh
sudo ./paqet-multi.sh
```

راهنمای کامل: **[MULTI-SERVER.md](./MULTI-SERVER.md)**

## مدیریت سرور

```bash
sudo paqctl menu        # منوی تعاملی
sudo paqctl status      # وضعیت
sudo paqctl start/stop/restart
sudo paqctl info        # اطلاعات اتصال برای کلاینت
sudo paqctl logs        # لاگ‌ها

sudo paqctl monitor     # مانیتور کاربران فعال زنده
sudo paqctl speedtest   # تست سرعت سرور
sudo paqctl routing     # بررسی نشتی DNS و روتینگ

sudo paqctl ban <ip>    # بن آی‌پی مزاحم
sudo paqctl unban <ip>
sudo paqctl rotate-key  # چرخش کلید رمزنگاری

sudo paqctl turbo       # حالت توربوی هسته سیستم‌عامل (BBR)
sudo paqctl watchdog    # واچ‌داگ خودکار
sudo paqctl tune        # منوی پروفایل‌های عملکرد

sudo paqctl cleanup     # پاکسازی لاگ/کش
sudo paqctl export      # خروجی رشته کانفیگ اشتراک‌گذاری
sudo paqctl import      # ورودی رشته کانفیگ
```

## نکات امنیتی

- **کلیدهای پیش‌فرض/نمونه رو هرگز استفاده نکن** — همیشه کلید یکتا و قوی (حداقل ۱۶ کاراکتر) بساز
- **آی‌پی VPS رو خصوصی نگه دار**
- **به‌روز نگه دار**: `sudo paqctl update`
- **فایروال VPS**: فقط پورت‌های لازم رو باز بذار

## سوالات متداول

**می‌تونم هم‌زمان Paqet و GFK رو اجرا کنم؟**
بله. پورت‌های متفاوتی استفاده می‌کنن (۱۰۸۰ و ۱۴۰۰۰) و می‌تونی از یکی به‌عنوان بکاپ استفاده کنی.

**چه VPS‌ای استفاده کنم؟**
هر VPS خارج از منطقه محدود: DigitalOcean، Vultr، Linode، Hetzner و... — مکانی نزدیک به خودت برای سرعت بهتر انتخاب کن.

**اتصالم کنده، چیکار کنم؟**
سرور نزدیک‌تر انتخاب کن، پروفایل عملکرد رو عوض کن (`sudo paqctl tune`)، یا بین Paqet و GFK سوییچ کن.

**سرور مدام قطع می‌شه**
`sudo paqctl logs` رو چک کن، منابع VPS رو بررسی کن، و واچ‌داگ رو با `sudo paqctl watchdog` فعال کن.

## عیب‌یابی

| مشکل | راه‌حل |
|---|---|
| "Connection refused" | چک کن سرور روشنه: `sudo paqctl status` روی VPS |
| "Permission denied" | لینوکس/مک با `sudo`، ویندوز به‌عنوان Administrator اجرا کن |
| مک گیت‌وی پیدا نشد | یک بار پینگ به گیت‌وی بزن، بعد `ip neigh \| grep default` (لینوکس) یا `arp -a` (ویندوز) |
| پورت SOCKS5 اشغاله | با `ss -ltnp \| grep 1080` چک کن، یا از [مدیریت چندسروری](./MULTI-SERVER.md) استفاده کن که خودش پورت آزاد رو پیدا می‌کنه |

## اعتبار و منابع (Credits)

StarlyProxy یک شخصی‌سازی و لایه‌ی مدیریتی اضافه‌شده روی پروژه‌های زیره، و تمام حق و اعتبار فنی موتور اصلی متعلق به سازندگان اصلیشونه:

- **موتور نصب/مدیریت پایه**: [paqctl](https://github.com/SamNet-dev/paqctl) توسط SamNet-dev
- **پروتکل Paqet**: [paqet](https://github.com/hanselime/paqet) — KCP روی raw TCP packets
- **تکنیک GFW-Knocker**: [gfw_resist_tcp_proxy](https://github.com/GFW-knocker/gfw_resist_tcp_proxy)
- **QUIC**: [aioquic](https://github.com/aiortc/aioquic)
- **دستکاری پکت**: [scapy](https://scapy.net/)

این پروژه تحت لایسنس **AGPL-3.0** منتشر شده (مثل پروژه پایه‌اش)، پس هرگونه استفاده یا توزیع باید همون لایسنس رو رعایت کنه.

## لایسنس

AGPL-3.0 — فایل [LICENSE](./LICENSE) رو ببین.

## سلب مسئولیت

این ابزار برای حریم خصوصی و دسترسی مشروع به اینترنت طراحی شده. قوانین هر کشور فرق می‌کنه — مسئولیت استفاده از این ابزار و رعایت قوانین محلی با خودته.

---
---

# English

<a id="english"></a>

## What is StarlyProxy?

**StarlyProxy** is a personalized firewall-bypass proxy manager built on top of the battle-tested [paqctl](https://github.com/SamNet-dev/paqctl) engine. The installer and core logic are the proven paqctl codebase — StarlyProxy adds its own multi-server management layer, documentation, and branding on top.

You run the **server** component on a VPS outside the restricted network, and the **client** on your Windows/macOS/Linux machine to reach it.

## Key Features

- **Two bypass methods**: Paqet (simple, fast) and GFW-Knocker (advanced, for heavy censorship)
- **Simultaneous multi-server support**: run as many independent connections as you want via the [multi-server manager](./MULTI-SERVER.md)
- **Automatic network detection**: interface, local IP, and gateway MAC auto-detected
- **Ready-made performance profiles**: Standard, High-loss, CDN/High-throughput, Gaming/Low-latency
- **OS-level Turbo Mode**: one-click TCP BBR + socket buffer tuning
- **Self-healing watchdog**: continuous health monitoring and auto-recovery
- **Full CLI management**: install, status, logs, IP ban/unban, key rotation, backup/restore

## Two Methods

| | **Paqet** | **GFW-Knocker (GFK)** |
|---|---|---|
| **Difficulty** | Easy ⭐ | Advanced ⭐⭐⭐ |
| **Best for** | Most situations | Heavy censorship (GFW) |
| **Your proxy** | `127.0.0.1:1080` | `127.0.0.1:14000` |
| **Technology** | KCP over raw sockets | Violated TCP + QUIC tunnel |
| **Server needs** | Just the paqet binary | GFK + Xray |

> **Tip:** You can install both simultaneously and keep one as a backup — they use different ports.

### Which should I use?

If your network is heavily censored (e.g. Iran, China's GFW), try **GFK** first. Otherwise, **Paqet** is faster and simpler for most situations.

## Architecture

**Paqet (simple):**
```
[Browser] --> [Paqet Client] --KCP/Raw TCP--> [Paqet Server] --SOCKS5--> [Internet]
              127.0.0.1:1080                   your.vps.ip
```

**GFW-Knocker (advanced):**
```
[Browser] --> [GFK Client] --Violated TCP--> [GFK Server] --> [Xray] --> [Internet]
              (VIO+QUIC)                      (QUIC Tunnel)    (SOCKS5)
              127.0.0.1:14000                  your.vps.ip
```

## Quick Start

### 1. Server Setup (Linux VPS)

```bash
curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/paqctl.sh | sudo bash
sudo paqctl menu
```

Get your client connection info:

```bash
sudo paqctl info
```

> The installed command is still named `paqctl` — StarlyProxy runs on this same underlying engine; the branding and the extra management layer (like multi-server support) are what's uniquely StarlyProxy.

### 2. Client Setup

<details>
<summary><strong>🪟 Windows</strong></summary>

**Easy method:**
1. Go to [https://github.com/arimakomi/StarlyProxy](https://github.com/arimakomi/StarlyProxy) → **Code** → **Download ZIP**
2. Open the `windows` folder
3. Right-click `Paqet-Client.bat` → **Run as administrator**
4. Enter your server address + key → **Connect**

**Advanced (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/windows/paqet-client.ps1 | iex
```
If you get a script execution error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Browser: SOCKS5 → `127.0.0.1:1080` (Paqet) or `127.0.0.1:14000` (GFK)
</details>

<details>
<summary><strong>🍎 macOS</strong></summary>

```bash
mkdir -p ~/starlyproxy && cd ~/starlyproxy
curl -LO https://github.com/hanselime/paqet/releases/download/v1.0.0-alpha.20/paqet-darwin-amd64-v1.0.0-alpha.20.tar.gz
tar -xzf paqet-darwin-amd64-v1.0.0-alpha.20.tar.gz
chmod +x paqet_darwin_amd64

cat > config.yaml << 'EOF'
role: "client"
socks5:
  - listen: "127.0.0.1:1080"
network:
  interface: "en0"
  ipv4:
    addr: "YOUR_LOCAL_IP:0"
    router_mac: "YOUR_ROUTER_MAC"
server:
  addr: "YOUR_SERVER_IP:8443"
transport:
  protocol: "kcp"
  kcp:
    mode: "fast"
    key: "YOUR_SECRET_KEY"
EOF

sudo ./paqet_darwin_amd64 run -c config.yaml
```
Use the `arm64` build for Apple Silicon. Local IP: `ifconfig en0 | grep inet`, gateway MAC: `arp -a | grep gateway`.
</details>

<details>
<summary><strong>🐧 Linux</strong></summary>

```bash
mkdir -p ~/starlyproxy && cd ~/starlyproxy
curl -LO https://github.com/hanselime/paqet/releases/download/v1.0.0-alpha.20/paqet-linux-amd64-v1.0.0-alpha.20.tar.gz
tar -xzf paqet-linux-amd64-v1.0.0-alpha.20.tar.gz
chmod +x paqet_linux_amd64

cat > config.yaml << 'EOF'
role: "client"
socks5:
  - listen: "127.0.0.1:1080"
network:
  interface: "eth0"
  ipv4:
    addr: "YOUR_LOCAL_IP:0"
    router_mac: "YOUR_ROUTER_MAC"
server:
  addr: "YOUR_SERVER_IP:8443"
transport:
  protocol: "kcp"
  kcp:
    mode: "fast"
    key: "YOUR_SECRET_KEY"
EOF

sudo ./paqet_linux_amd64 run -c config.yaml
```
Or simply run `paqctl.sh` on the same machine to auto-detect the network for you.
</details>

## 🔀 Running Multiple Servers Simultaneously

If you want to connect to **several servers at once** (e.g. primary + failover, or different regions), use **[paqet-multi.sh](./paqet-multi.sh)** — part of StarlyProxy that manages as many servers as you want, each with its own config, auto-assigned SOCKS5 port, and independent systemd service.

```bash
curl -sLO https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/paqet-multi.sh
chmod +x paqet-multi.sh
sudo ./paqet-multi.sh
```

Full guide: **[MULTI-SERVER.md](./MULTI-SERVER.md)**

## Server Management

```bash
sudo paqctl menu        # Interactive menu
sudo paqctl status      # Check status
sudo paqctl start/stop/restart
sudo paqctl info        # Connection info for clients
sudo paqctl logs        # View logs

sudo paqctl monitor     # Live active-client monitor
sudo paqctl speedtest   # Server speed test
sudo paqctl routing     # DNS leak / routing check

sudo paqctl ban <ip>    # Ban an abusive IP
sudo paqctl unban <ip>
sudo paqctl rotate-key  # Rotate encryption key

sudo paqctl turbo       # OS-level kernel turbo mode (BBR)
sudo paqctl watchdog    # Self-healing watchdog
sudo paqctl tune        # Performance profile menu

sudo paqctl cleanup     # Clean logs/cache
sudo paqctl export      # Export shareable config string
sudo paqctl import      # Import a config string
```

## Security Notes

- **Never use example/default keys** — always generate a unique, strong key (16+ characters)
- **Keep your VPS IP private**
- **Stay updated**: `sudo paqctl update`
- **VPS firewall**: only open the ports you actually need

## FAQ

**Can I run Paqet and GFK at the same time?**
Yes — they use different ports (1080 and 14000), so you can keep one as a backup.

**Which VPS provider should I use?**
Any VPS outside the restricted region: DigitalOcean, Vultr, Linode, Hetzner, etc. Choose one geographically close to you for better speed.

**My connection is slow**
Pick a closer server, change the performance profile (`sudo paqctl tune`), or switch between Paqet and GFK.

**The server keeps disconnecting**
Check `sudo paqctl logs`, check VPS resources, and enable the watchdog with `sudo paqctl watchdog`.

## Troubleshooting

| Issue | Fix |
|---|---|
| "Connection refused" | Check the server is running: `sudo paqctl status` on the VPS |
| "Permission denied" | Linux/macOS: run with `sudo`; Windows: run as Administrator |
| Gateway MAC not found | Ping the gateway once, then `ip neigh \| grep default` (Linux) or `arp -a` (Windows) |
| SOCKS5 port already in use | Check with `ss -ltnp \| grep 1080`, or use the [multi-server manager](./MULTI-SERVER.md), which auto-picks a free port |

## Credits

StarlyProxy is a personalization and management layer on top of the projects below; full technical credit for the core engine belongs to their original authors:

- **Base install/management engine**: [paqctl](https://github.com/SamNet-dev/paqctl) by SamNet-dev
- **Paqet protocol**: [paqet](https://github.com/hanselime/paqet) — KCP over raw TCP packets
- **GFW-Knocker technique**: [gfw_resist_tcp_proxy](https://github.com/GFW-knocker/gfw_resist_tcp_proxy)
- **QUIC**: [aioquic](https://github.com/aiortc/aioquic)
- **Packet manipulation**: [scapy](https://scapy.net/)

This project is released under **AGPL-3.0** (same as its base project), so any use or redistribution must comply with that license.

## License

AGPL-3.0 — see [LICENSE](./LICENSE).

## Disclaimer

This tool is intended for legitimate privacy and internet access needs. Laws vary by country — you are responsible for using this tool in compliance with your local regulations.
