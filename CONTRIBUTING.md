# StarlyProxy v3.0 - Contributing Guide

ممنون که می‌خواهید به StarlyProxy کمک کنید! 🎉

## چطور می‌توانم کمک کنم؟

### 🐛 گزارش باگ

اگر باگی پیدا کردید:

1. بررسی کنید که قبلاً گزارش نشده باشد
2. Issue جدید باز کنید
3. شامل موارد زیر باشد:
   - توضیح دقیق مشکل
   - مراحل بازسازی (reproduce)
   - خروجی `starlyproxy status`
   - لاگ‌ها (`starlyproxy logs`)
   - سیستم عامل و نسخه Python
   - نسخه StarlyProxy (`git rev-parse HEAD`)

### 💡 پیشنهاد ویژگی

برای ویژگی جدید:

1. Discussion باز کنید (نه Issue)
2. توضیح دهید چرا مفید است
3. Use case واقعی بیاورید
4. منتظر feedback بمانید قبل از شروع کد

### 🔧 Pull Request

برای ارسال کد:

1. **Fork** کنید
2. **Branch** جدید بسازید:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

3. **تغییرات** را انجام دهید:
   - کد تمیز و خوانا
   - PEP 8 style guide
   - Type hints کامل
   - Docstrings واضح

4. **Test** کنید:
   ```bash
   python tests/test_core.py
   ```

5. **Commit** با پیام واضح:
   ```bash
   git commit -m "feat: add automatic failover between instances"
   ```

6. **Push** کنید:
   ```bash
   git push origin feature/my-awesome-feature
   ```

7. **PR** باز کنید در GitHub

## استانداردهای کد

### Python Style

```python
# ✅ خوب
def create_instance(name: str, config: Dict[str, Any]) -> bool:
    """
    Create a new proxy instance
    
    Args:
        name: Unique instance name
        config: Instance configuration dict
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Implementation
        logger.info(f"Created instance: {name}")
        return True
    except Exception as e:
        logger.error(f"Failed to create instance: {e}")
        return False

# ❌ بد
def create_instance(name,config):
    # no type hints, no docstring
    print("creating")
    return True
```

### Logging

```python
# ✅ خوب
logger.info(f"Starting instance: {name}")
logger.error(f"Failed to connect: {e}", exc_info=True)

# ❌ بد
print("Starting...")  # No logging
logger.info("Error!")  # No context
```

### Error Handling

```python
# ✅ خوب
try:
    result = risky_operation()
    return result
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise

# ❌ بد
try:
    result = risky_operation()
except:  # Bare except
    pass  # Silent failure
```

## ساختار Branch

- `main` - نسخه stable
- `develop` - نسخه در حال توسعه
- `feature/xyz` - ویژگی جدید
- `fix/xyz` - رفع باگ
- `docs/xyz` - مستندات

## Commit Messages

فرمت: `<type>: <description>`

**Types:**
- `feat`: ویژگی جدید
- `fix`: رفع باگ
- `docs`: تغییرات مستندات
- `style`: فرمت کد (بدون تغییر منطق)
- `refactor`: بازنویسی کد
- `test`: اضافه کردن تست
- `chore`: کارهای نگهداری

**مثال‌ها:**
```
feat: add Telegram bot integration
fix: resolve port collision in multi-instance
docs: update API documentation
refactor: simplify instance lifecycle management
```

## چک‌لیست PR

قبل از ارسال PR:

- [ ] کد با PEP 8 سازگار است
- [ ] Type hints اضافه شده
- [ ] Docstrings نوشته شده
- [ ] تست شده (manual یا automated)
- [ ] Logging مناسب اضافه شده
- [ ] Error handling درست است
- [ ] مستندات بروز شده (اگر لازم)
- [ ] CHANGELOG.md بروز شده
- [ ] Commit messages واضح هستند
- [ ] کد review شخصی انجام شده

## تست

### Manual Testing

```bash
# نصب development
git clone https://github.com/arimakomi/StarlyProxy.git
cd StarlyProxy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# تست core
python tests/test_core.py

# تست CLI
python cli/starlyproxy-cli.py list

# تست panel
python panel/app.py
# باز کنید: http://localhost:5000
```

### Unit Tests (آینده)

```python
# tests/test_instance_manager.py
import unittest
from core import InstanceManager

class TestInstanceManager(unittest.TestCase):
    def test_create_instance(self):
        # Implementation
        pass
```

## سوالات؟

- GitHub Discussions
- Issues برای سوالات فنی
- Email: artin@starly.me

---

**ممنون که به StarlyProxy کمک می‌کنید! 🙏**
