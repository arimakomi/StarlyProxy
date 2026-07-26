# StarlyProxy v3.0 - Changelog

## v3.0.1 (2026-07-26) - رفع باگ‌های بحرانی پایداری 🛠️

### 🐛 باگ‌های بحرانی رفع‌شده

- **پنل وب (`panel/app.py`)**: یک بلوک `if __name__ == '__main__': app.run(...)` وسط فایل قرار داشت. چون `app.run()` بلاک‌کننده است، وقتی پنل مستقیماً اجرا می‌شد (دقیقاً همان‌طور که سرویس systemd آن را اجرا می‌کند)، تمام روت‌هایی که *بعد* از آن بلوک تعریف شده بودند اصلاً ثبت نمی‌شدند. نتیجه: APIهای بک‌آپ، سرورهای چندگانه، مدیریت کاربران، متریک‌ها و بررسی/اعمال آپدیت همگی خطای 404 می‌دادند. این بلوک به انتهای واقعی فایل منتقل شد.
- **پنل وب**: توابع `api_check_updates` و `api_system_update` دوبار تعریف شده بودند (تعریف تکراری روت در Flask)؛ به یک نسخهٔ واحد و صحیح ادغام شدند. `subprocess` که استفاده می‌شد اما import نشده بود، اضافه شد. متغیر تعریف‌نشدهٔ `PORT` در انتهای فایل با `port` صحیح جایگزین شد.
- **`core/xray/manager.py`**: توابع `stop()` و `get_status()` از `signal` و `psutil` بدون import استفاده می‌کردند؛ در نتیجه توقف Xray از پنل به‌طور بی‌صدا شکست می‌خورد. importها اضافه شدند.
- **`core/backup.py`**: نام فایل دیتابیس در بک‌آپ‌گیر (`instances.db`) با نام واقعی فایلی که `core/database.py` می‌سازد (`starlyproxy.db`) مطابقت نداشت؛ در نتیجه بک‌آپ‌ها هرگز شامل دیتابیس واقعی نمی‌شدند. اصلاح و با تست عملی تأیید شد.
- **`install.sh`**: متغیر رنگ `MAGENTA` استفاده می‌شد اما تعریف نشده بود؛ چون اسکریپت با `set -u` اجرا می‌شود، نصب درست در همان خط پایانی با خطای «unbound variable» کرش می‌کرد. تعریف شد.
- **`install.sh`**: پورت پنل که به‌صورت خودکار پیدا می‌شد (`PANEL_PORT`) هرگز به سرویس systemd پاس داده نمی‌شد، پس پنل همیشه با مقدار پیش‌فرض (۵۰۰۰) بالا می‌آمد نه پورت واقعاً آزاد. متغیر محیطی `FLASK_PORT` به تنظیمات سرویس اضافه شد.
- **`install.sh`**: نصب دستور CLI با `python3 -m cli ...` انجام می‌شد که چون `cli/` نه `__init__.py` دارد و نه `__main__.py`، همیشه با خطای `No module named cli` شکست می‌خورد. اکنون از `starlyproxy-wrapper.sh` موجود در ریپو استفاده می‌شود (که در بخش Troubleshooting خود README هم درست مستند شده بود).
- **`uninstall.sh`**: متغیر رنگ `CYAN` استفاده می‌شد ولی تعریف نشده بود (مشکل ظاهری/بی‌رنگ شدن پیام‌ها). تعریف شد.

### 🧹 پاکسازی
- حذف importها و متغیرهای بلااستفاده در ۲۰+ فایل پایتون (بدون تغییر رفتار).

### ✅ نحوهٔ تست
همهٔ موارد بالا با اجرای واقعی پنل، بررسی تک‌تک روت‌ها، اجرای CLI نصب‌شده، و ساخت/بازبینی محتوای یک بک‌آپ واقعی تأیید شدند؛ نه فقط با خواندن کد.

## v3.0.0 (2026-07-25) - کامل شده ✅

### 🎉 تغییرات عمده

**بازنویسی کامل پروژه** - از یک مجموعه اسکریپت به یک سیستم مدیریت حرفه‌ای.

### ✨ ویژگی‌های جدید

#### 🏗️ معماری جدید
- **Core Module** - هسته مرکزی با ConfigManager، DatabaseManager، InstanceManager
- **Proxy Wrappers** - پوشش‌های یکپارچه برای Paqet و GFK
- **Database Layer** - SQLite برای ذخیره configs، logs و stats
- **Plugin Architecture** - قابلیت افزودن proxy types جدید

#### 🚀 مدیریت چند Instance
- پشتیبانی نامحدود از instance های همزمان
- هر instance با config، port، و process مستقل
- Auto-assign پورت‌های SOCKS بدون تداخل
- مدیریت lifecycle کامل (start/stop/restart)

#### 🎨 پنل وب Flask
- **Dashboard** - نمای کلی با آمار real-time
- **Instance Manager** - مدیریت کامل از مرورگر
- **Live Logs** - نمایش لاگ‌ها با رنگ‌بندی
- **Charts & Stats** - نمودارهای مصرف و ترافیک
- **REST API** - تمام عملیات از طریق API

#### ⚡ CLI قدرتمند
- دستورات فارسی و کاربرپسند
- `starlyproxy list` - لیست تمام instances
- `starlyproxy add` - افزودن instance جدید
- `starlyproxy start/stop/restart` - کنترل instances
- `starlyproxy status` - نمایش وضعیت کامل
- `starlyproxy logs` - نمایش لاگ‌ها
- پشتیبانی از bulk operations (start all, stop all)

#### 💾 مدیریت داده
- SQLite database برای persistence
- جدول instances - اطلاعات و وضعیت
- جدول stats - آمار استفاده
- جدول logs - لاگ‌های جامع
- Auto-cleanup لاگ‌های قدیمی

#### 🛠️ ابزارهای کمکی
- `health_check.sh` - بررسی سلامت و ریستارت خودکار
- `backup.sh` - پشتیبان‌گیری از configs و database
- `install.sh` - نصب خودکار با یک دستور
- systemd integration - مدیریت به عنوان سرویس

### 🔧 بهبودها

#### Paqet Integration
- دانلود خودکار binary از GitHub releases
- پشتیبانی از linux-amd64 و linux-arm64
- ساخت خودکار config.yaml
- مدیریت process با proper signal handling

#### GFK Integration
- یکپارچه‌سازی کامل کد موجود
- ساخت خودکار parameters.py
- مدیریت process group برای cleanup بهتر
- پشتیبانی از client و server mode

#### Network Detection
- تشخیص خودکار interface
- تشخیص خودکار local IP
- تشخیص خودکار gateway MAC
- fallback برای محیط‌های مختلف

#### Error Handling
- Logging جامع در تمام سطوح
- Exception handling مناسب
- Error messages واضح و فارسی
- Stack traces برای debugging

### 📚 مستندات

- README کامل با مثال‌های کاربردی
- API documentation جامع
- راهنمای troubleshooting
- مثال‌های سناریوهای واقعی

### 🔄 Migration از v2.x

**تغییرات breaking:**
- ساختار فایل‌ها کاملاً تغییر کرده
- دیگر `paqctl` مستقیم نیست - از `starlyproxy` استفاده کنید
- configs قدیمی سازگار نیستند

**نحوه migration:**
1. Backup از تنظیمات فعلی
2. نصب StarlyProxy v3.0
3. افزودن دوباره instances با CLI جدید

### ⚙️ تغییرات فنی

#### Python Requirements
- `netifaces>=0.11.0` - network detection
- `psutil>=5.9.0` - process management
- `flask>=3.0.0` - web panel
- `scapy>=2.5.0` - GFK packet manipulation
- `aioquic>=0.9.21` - GFK QUIC support
- `pyyaml>=6.0` - config management

#### File Structure
```
/opt/starlyproxy/
├── core/                    # Core modules
├── proxy/                   # Proxy wrappers
│   ├── paqet/              # Paqet binaries
│   └── gfk/                # GFK code
├── panel/                   # Web panel
├── cli/                     # CLI scripts
├── instances/               # Instance data
│   └── <name>/
│       ├── config.yaml
│       ├── parameters.py
│       └── *.log
├── config.json             # Main config
├── starlyproxy.db          # Database
└── venv/                   # Python venv
```

### 🐛 رفع مشکلات

- رفع مشکل port collision در multi-instance
- رفع memory leak در long-running instances
- رفع crash در network interface changes
- رفع مشکل zombie processes
- رفع مشکل config validation

### 🔒 امنیت

- Validation ورودی‌های کاربر
- SQL injection prevention (parameterized queries)
- Process isolation
- Proper signal handling
- No hardcoded secrets

### 📊 Performance

- Lazy loading برای imports
- Connection pooling برای database
- Efficient process monitoring
- Minimal overhead per instance

---

## نسخه‌های قبلی

### v2.0.0
- اضافه شدن `paqet-multi.sh`
- پشتیبانی محدود از چند سرور
- مستندات MULTI-SERVER.md

### v1.0.0
- نسخه اولیه بر پایه paqctl
- پشتیبانی از Paqet و GFK
- اسکریپت‌های ساده bash

---

## Roadmap v3.1

### در حال برنامه‌ریزی:
- [ ] Web UI Authentication
- [ ] Telegram Bot برای مدیریت
- [ ] Auto-failover بین instances
- [ ] Traffic statistics visualization
- [ ] Config import/export
- [ ] Docker support
- [ ] Android/iOS client apps

---

**نویسنده:** STaRly (Artin)  
**تاریخ:** 2026-07-25  
**لایسنس:** AGPL-3.0
