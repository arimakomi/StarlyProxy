# Paqet Multi-Server Manager

A companion script for [paqctl](https://github.com/SamNet-dev/paqctl) that lets you run **as many simultaneous paqet client connections as you want**, each to a different server, each with its own local SOCKS5 port and its own independent systemd service.

> paqctl itself manages a single connection (one `config.yaml`, one `paqctl.service`). This script sits alongside it and manages *N* independent connections using the same `paqet` binary that paqctl installs.

[نسخه فارسی پایین صفحه](#نسخه-فارسی)

---

## Requirements

- Linux with systemd
- The official `paqctl.sh` already installed (this script reuses its `paqet` binary at `/opt/paqctl/bin/paqet`):
  ```bash
  curl -sL https://raw.githubusercontent.com/SamNet-dev/paqctl/main/paqctl.sh | sudo bash
  ```
- Root access

## Install

```bash
curl -sLO https://raw.githubusercontent.com/arimakomi/paqctl/main/paqet-multi.sh
chmod +x paqet-multi.sh
sudo ./paqet-multi.sh
```

## How it works

Each server you add gets:

- Its own config file: `/opt/paqctl/servers/<name>.yaml`
- Its own systemd service: `paqet-<name>.service` (independent start/stop/restart, auto-restart on crash)
- Its own local SOCKS5 port, auto-assigned starting at `1080` (1080, 1081, 1082, ...) — no manual port bookkeeping, no collisions.

Network interface, local IP, and gateway MAC are auto-detected the same way the official installer does it, with the option to override manually.

## Interactive menu

```bash
sudo ./paqet-multi.sh
```

```
 1) Add new server              9) Start all
 2) Start one server           10) Stop all
 3) Stop one server            11) Restart all
 4) Restart one server
 5) Remove one server
 6) Show logs for one server
 7) Edit a server (address/key)
 8) Test connection (ping) to a server
12) Backup all configs
13) Restore from a backup file
 0) Exit
```

## Non-interactive / scriptable usage

Every menu action is also available as a CLI subcommand, so you can automate setup (e.g. via SSH, Ansible, cron):

```bash
# Add a server non-interactively
sudo ./paqet-multi.sh add germany1 1.2.3.4:8443 "myEncryptionKey123" 1
#                        ^name    ^server:port  ^key                 ^profile (1=standard,2=high-loss,3=cdn,4=gaming)

sudo ./paqet-multi.sh add finland1 5.6.7.8:8443 "anotherKey456" 1

# List all configured servers with live status
sudo ./paqet-multi.sh list

# Start / stop / restart one, or all at once
sudo ./paqet-multi.sh start germany1
sudo ./paqet-multi.sh stop all
sudo ./paqet-multi.sh restart all

# Edit an existing server's remote address or key (keeps everything else, backs up the old config)
sudo ./paqet-multi.sh edit germany1

# Test connectivity
sudo ./paqet-multi.sh ping germany1

# View recent logs
sudo ./paqet-multi.sh logs germany1

# Remove a server completely (stops service, deletes config + unit file)
sudo ./paqet-multi.sh remove germany1

# Backup every server config to a tar.gz (default path under /root)
sudo ./paqet-multi.sh backup /root/my-paqet-backup.tar.gz

# Restore from a backup (recreates configs + systemd units, does not auto-start)
sudo ./paqet-multi.sh restore /root/my-paqet-backup.tar.gz
```

## Example: two servers as primary + failover

```bash
sudo ./paqet-multi.sh add primary  1.2.3.4:8443 "keyA" 1   # -> 127.0.0.1:1080
sudo ./paqet-multi.sh add backup   5.6.7.8:8443 "keyB" 1   # -> 127.0.0.1:1081
```

Point your browser/app at `127.0.0.1:1080` normally. If that server gets blocked or goes down, switch to `127.0.0.1:1081` — no need to touch configs, both are already running.

## Performance profiles

| # | Profile | Best for |
|---|---------|----------|
| 1 | Standard | General browsing, everyday use |
| 2 | High-loss | Heavy DPI / restricted networks with packet loss |
| 3 | CDN | High-throughput tunnels, multi-layer CDN routing |
| 4 | Gaming | Low-latency real-time traffic (games, VOIP) |

## Files created

```
/opt/paqctl/servers/<name>.yaml               # per-server config
/etc/systemd/system/paqet-<name>.service      # per-server systemd unit
```

## Uninstall a single server

```bash
sudo ./paqet-multi.sh remove <name>
```

This stops and disables the service, and deletes both the config and the unit file. Other servers are untouched.

## Troubleshooting

- **Port already in use**: the script auto-picks the next free port; if you still hit a conflict, check `ss -ltnp | grep 1080` and adjust manually in the YAML's `socks5.listen`.
- **Service won't start**: `sudo journalctl -u paqet-<name>.service -n 50`
- **Gateway MAC not detected**: run `ip neigh | grep default` after pinging your gateway once, or enter it manually when prompted (format `aa:bb:cc:dd:ee:ff`).

---

# نسخه فارسی

اسکریپت کمکی برای [paqctl](https://github.com/SamNet-dev/paqctl) که بهت اجازه می‌ده **هرچقدر که بخوای اتصال کلاینت paqet هم‌زمان** داشته باشی — هر کدوم به یک سرور متفاوت، هر کدوم با پورت SOCKS5 و سرویس systemd مستقل خودش.

> خود paqctl فقط یک اتصال رو مدیریت می‌کنه (یک `config.yaml`، یک `paqctl.service`). این اسکریپت کنارش می‌شینه و از همون باینری `paqet` که paqctl نصب کرده، برای مدیریت چند اتصال مستقل استفاده می‌کنه.

## پیش‌نیازها

- لینوکس با systemd
- نصب رسمی `paqctl.sh` (این اسکریپت از باینری `paqet` نصب‌شده در `/opt/paqctl/bin/paqet` استفاده می‌کنه):
  ```bash
  curl -sL https://raw.githubusercontent.com/SamNet-dev/paqctl/main/paqctl.sh | sudo bash
  ```
- دسترسی root

## نصب

```bash
curl -sLO https://raw.githubusercontent.com/arimakomi/paqctl/main/paqet-multi.sh
chmod +x paqet-multi.sh
sudo ./paqet-multi.sh
```

## چطور کار می‌کنه

هر سروری که اضافه کنی این‌ها رو می‌گیره:

- فایل کانفیگ مخصوص خودش: `/opt/paqctl/servers/<name>.yaml`
- سرویس systemd مخصوص خودش: `paqet-<name>.service` (روشن/خاموش/ری‌استارت مستقل، خودش بعد از کرش دوباره بالا میاد)
- پورت SOCKS5 محلی مخصوص خودش، خودکار از `1080` شروع می‌شه (۱۰۸۰، ۱۰۸۱، ۱۰۸۲، ...) — نیازی به شمارش دستی پورت یا نگرانی تداخل نیست.

اینترفیس شبکه، آی‌پی محلی و مک گیت‌وی دقیقاً مثل نصب‌کننده رسمی خودکار تشخیص داده می‌شن، با امکان تغییر دستی.

## منوی تعاملی

```bash
sudo ./paqet-multi.sh
```

```
 1) افزودن سرور جدید            9) روشن کردن همه
 2) روشن کردن یک سرور          10) خاموش کردن همه
 3) خاموش کردن یک سرور         11) ری‌استارت همه
 4) ری‌استارت یک سرور
 5) حذف یک سرور
 6) نمایش لاگ یک سرور
 7) ویرایش یک سرور (آدرس/کلید)
 8) تست اتصال (ping) یک سرور
12) بکاپ از همه کانفیگ‌ها
13) بازیابی از فایل بکاپ
 0) خروج
```

## استفاده غیرتعاملی / اسکریپت‌نویسی

هر گزینه منو به‌صورت دستور CLI هم موجوده، پس می‌تونی راه‌اندازی رو خودکار کنی (مثلاً از طریق SSH، Ansible، یا cron):

```bash
# افزودن سرور بدون منو
sudo ./paqet-multi.sh add germany1 1.2.3.4:8443 "myEncryptionKey123" 1
#                        ^اسم      ^سرور:پورت    ^کلید                ^پروفایل (۱=استاندارد, ۲=پرافت, ۳=CDN, ۴=گیمینگ)

sudo ./paqet-multi.sh add finland1 5.6.7.8:8443 "anotherKey456" 1

# لیست همه سرورها با وضعیت زنده
sudo ./paqet-multi.sh list

# روشن/خاموش/ری‌استارت یکی، یا همه با هم
sudo ./paqet-multi.sh start germany1
sudo ./paqet-multi.sh stop all
sudo ./paqet-multi.sh restart all

# ویرایش آدرس یا کلید یک سرور موجود (بقیه چیزها ثابت می‌مونه، نسخه قبلی بکاپ می‌شه)
sudo ./paqet-multi.sh edit germany1

# تست اتصال
sudo ./paqet-multi.sh ping germany1

# مشاهده لاگ‌های اخیر
sudo ./paqet-multi.sh logs germany1

# حذف کامل یک سرور (سرویس متوقف می‌شه، کانفیگ + فایل سرویس حذف می‌شن)
sudo ./paqet-multi.sh remove germany1

# بکاپ از همه کانفیگ‌ها
sudo ./paqet-multi.sh backup /root/my-paqet-backup.tar.gz

# بازیابی از بکاپ (کانفیگ‌ها + سرویس‌های systemd رو می‌سازه، خودکار روشن نمی‌کنه)
sudo ./paqet-multi.sh restore /root/my-paqet-backup.tar.gz
```

## مثال: دو سرور اصلی و بکاپ

```bash
sudo ./paqet-multi.sh add primary  1.2.3.4:8443 "keyA" 1   # -> 127.0.0.1:1080
sudo ./paqet-multi.sh add backup   5.6.7.8:8443 "keyB" 1   # -> 127.0.0.1:1081
```

مرورگر/برنامه‌ت رو روی `127.0.0.1:1080` تنظیم کن. اگه اون سرور مسدود یا خاموش شد، برو روی `127.0.0.1:1081` — نیازی به دست‌کاری کانفیگ نیست، هر دو از قبل روشن‌اند.

## پروفایل‌های عملکرد

| # | پروفایل | مناسب برای |
|---|---------|------------|
| ۱ | استاندارد | وب‌گردی عمومی، استفاده روزمره |
| ۲ | پرافت (High-loss) | DPI سنگین / شبکه‌های محدود با پکت‌لاس |
| ۳ | CDN | تانل‌های پرسرعت، مسیریابی چندلایه CDN |
| ۴ | گیمینگ | ترافیک بلادرنگ کم‌تاخیر (بازی، تماس صوتی) |

## فایل‌های ساخته‌شده

```
/opt/paqctl/servers/<name>.yaml               # کانفیگ هر سرور
/etc/systemd/system/paqet-<name>.service      # سرویس systemd هر سرور
```

## حذف یک سرور خاص

```bash
sudo ./paqet-multi.sh remove <name>
```

سرویس متوقف و غیرفعال می‌شه، و هم کانفیگ هم فایل سرویس حذف می‌شن. بقیه سرورها دست‌نخورده می‌مونن.

## عیب‌یابی

- **پورت قبلاً استفاده شده**: اسکریپت خودش پورت آزاد بعدی رو انتخاب می‌کنه؛ اگه بازم تداخل داشتی، `ss -ltnp | grep 1080` رو چک کن و دستی توی `socks5.listen` فایل YAML عوضش کن.
- **سرویس بالا نمیاد**: `sudo journalctl -u paqet-<name>.service -n 50`
- **مک گیت‌وی پیدا نشد**: بعد از یک بار پینگ به گیت‌وی، `ip neigh | grep default` رو بزن، یا وقتی اسکریپت پرسید دستی وارد کن (فرمت `aa:bb:cc:dd:ee:ff`).
