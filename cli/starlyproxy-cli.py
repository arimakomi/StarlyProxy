#!/usr/bin/env python3
"""
StarlyProxy CLI - Command Line Interface
مدیریت کامل instance ها از خط فرمان
"""

import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import InstanceManager, ConfigManager, DatabaseManager
from core.utils import check_root_privileges, format_bytes, format_duration

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("StarlyProxy.CLI")


def cmd_list(args):
    """List all instances"""
    mgr = InstanceManager()
    instances = mgr.list_instances()
    
    if not instances:
        print("هیچ instance ای یافت نشد.")
        return
    
    print(f"\n{'نام':<20} {'نوع':<8} {'حالت':<8} {'وضعیت':<10} {'پورت SOCKS':<12} {'سرور':<30}")
    print("=" * 100)
    
    for inst in instances:
        status = inst.get('status', 'unknown')
        socks_port = inst.get('socks_port', '-')
        server_addr = inst.get('server_address', '-')
        
        print(f"{inst['name']:<20} {inst['type']:<8} {inst['mode']:<8} "
              f"{status:<10} {str(socks_port):<12} {server_addr:<30}")
    
    print()


def cmd_add(args):
    """Add new instance"""
    if not check_root_privileges():
        print("❌ نیاز به دسترسی root دارید.")
        return 1
    
    mgr = InstanceManager()
    
    # Parse server address
    if ':' in args.server:
        server_ip, server_port = args.server.rsplit(':', 1)
        server_port = int(server_port)
    else:
        print("❌ فرمت آدرس سرور نادرست است. استفاده کنید: IP:PORT")
        return 1
    
    print(f"در حال ایجاد instance: {args.name}...")
    
    success = mgr.create_instance(
        name=args.name,
        instance_type=args.type,
        mode=args.mode,
        server_address=server_ip,
        server_port=server_port,
        secret_key=args.key,
        profile=args.profile,
        auto_restart=not args.no_auto_restart
    )
    
    if success:
        print(f"✅ Instance '{args.name}' با موفقیت ایجاد شد.")
        if args.mode == 'client':
            config = mgr.config_mgr.load_instance_config(args.name)
            print(f"📡 پورت SOCKS: {config.get('socks_port')}")
        return 0
    else:
        print(f"❌ خطا در ایجاد instance '{args.name}'")
        return 1


def cmd_start(args):
    """Start instance"""
    if not check_root_privileges():
        print("❌ نیاز به دسترسی root دارید.")
        return 1
    
    mgr = InstanceManager()
    
    if args.name == 'all':
        instances = mgr.config_mgr.list_instances()
        success_count = 0
        for name in instances:
            if mgr.start_instance(name):
                success_count += 1
                print(f"✅ {name} شروع شد")
            else:
                print(f"❌ خطا در شروع {name}")
        print(f"\n{success_count}/{len(instances)} instance شروع شد.")
    else:
        if mgr.start_instance(args.name):
            print(f"✅ Instance '{args.name}' شروع شد.")
            return 0
        else:
            print(f"❌ خطا در شروع instance '{args.name}'")
            return 1


def cmd_stop(args):
    """Stop instance"""
    if not check_root_privileges():
        print("❌ نیاز به دسترسی root دارید.")
        return 1
    
    mgr = InstanceManager()
    
    if args.name == 'all':
        instances = mgr.list_instances()
        success_count = 0
        for inst in instances:
            if mgr.stop_instance(inst['name'], force=args.force):
                success_count += 1
                print(f"✅ {inst['name']} متوقف شد")
            else:
                print(f"❌ خطا در توقف {inst['name']}")
        print(f"\n{success_count}/{len(instances)} instance متوقف شد.")
    else:
        if mgr.stop_instance(args.name, force=args.force):
            print(f"✅ Instance '{args.name}' متوقف شد.")
            return 0
        else:
            print(f"❌ خطا در توقف instance '{args.name}'")
            return 1


def cmd_restart(args):
    """Restart instance"""
    if not check_root_privileges():
        print("❌ نیاز به دسترسی root دارید.")
        return 1
    
    mgr = InstanceManager()
    
    if mgr.restart_instance(args.name):
        print(f"✅ Instance '{args.name}' ریستارت شد.")
        return 0
    else:
        print(f"❌ خطا در ریستارت instance '{args.name}'")
        return 1


def cmd_delete(args):
    """Delete instance"""
    if not check_root_privileges():
        print("❌ نیاز به دسترسی root دارید.")
        return 1
    
    if not args.yes:
        confirm = input(f"آیا مطمئن هستید که می‌خواهید '{args.name}' را حذف کنید؟ (yes/no): ")
        if confirm.lower() not in ['yes', 'y', 'بله']:
            print("لغو شد.")
            return 0
    
    mgr = InstanceManager()
    
    if mgr.delete_instance(args.name, stop_first=True):
        print(f"✅ Instance '{args.name}' حذف شد.")
        return 0
    else:
        print(f"❌ خطا در حذف instance '{args.name}'")
        return 1


def cmd_status(args):
    """Show instance status"""
    mgr = InstanceManager()
    
    status = mgr.get_instance_status(args.name)
    if not status:
        print(f"❌ Instance '{args.name}' یافت نشد.")
        return 1
    
    print(f"\n{'='*50}")
    print(f"📊 وضعیت Instance: {args.name}")
    print(f"{'='*50}")
    print(f"نوع: {status['type']}")
    print(f"حالت: {status['mode']}")
    print(f"وضعیت: {status['actual_status']}")
    
    if status['mode'] == 'client':
        print(f"پورت SOCKS: {status['socks_port']}")
    
    print(f"سرور: {status['server_address']}")
    
    if status['actual_status'] == 'running':
        print(f"PID: {status.get('pid')}")
        print(f"CPU: {status.get('cpu_percent', 0):.1f}%")
        print(f"Memory: {status.get('memory_mb', 0):.1f} MB")
        print(f"Uptime: {format_duration(status.get('uptime', 0))}")
    
    print(f"ایجاد شده در: {status['created_at']}")
    print(f"{'='*50}\n")
    
    return 0


def cmd_logs(args):
    """Show instance logs"""
    db = DatabaseManager()
    logs = db.get_logs(instance_name=args.name, limit=args.lines)
    
    if not logs:
        print("لاگی یافت نشد.")
        return
    
    print(f"\n📋 لاگ‌های {args.name if args.name else 'همه'}:\n")
    for log in reversed(logs):
        timestamp = log['timestamp']
        level = log['level']
        message = log['message']
        instance = log.get('instance_name', 'system')
        print(f"[{timestamp}] [{level}] [{instance}] {message}")


def main():
    parser = argparse.ArgumentParser(
        description='StarlyProxy - مدیریت پروکسی چند instance',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='دستورات')
    
    # list command
    parser_list = subparsers.add_parser('list', help='نمایش لیست instance ها')
    parser_list.set_defaults(func=cmd_list)
    
    # add command
    parser_add = subparsers.add_parser('add', help='افزودن instance جدید')
    parser_add.add_argument('name', help='نام instance')
    parser_add.add_argument('type', choices=['paqet', 'gfk'], help='نوع پروکسی')
    parser_add.add_argument('mode', choices=['client', 'server'], help='حالت')
    parser_add.add_argument('server', help='آدرس سرور (IP:PORT)')
    parser_add.add_argument('key', help='کلید رمزنگاری')
    parser_add.add_argument('--profile', default='standard', 
                          choices=['standard', 'high-loss', 'cdn', 'gaming'],
                          help='پروفایل عملکرد')
    parser_add.add_argument('--no-auto-restart', action='store_true',
                          help='غیرفعال کردن ریستارت خودکار')
    parser_add.set_defaults(func=cmd_add)
    
    # start command
    parser_start = subparsers.add_parser('start', help='شروع instance')
    parser_start.add_argument('name', help='نام instance (یا all برای همه)')
    parser_start.set_defaults(func=cmd_start)
    
    # stop command
    parser_stop = subparsers.add_parser('stop', help='توقف instance')
    parser_stop.add_argument('name', help='نام instance (یا all برای همه)')
    parser_stop.add_argument('-f', '--force', action='store_true', help='توقف اجباری')
    parser_stop.set_defaults(func=cmd_stop)
    
    # restart command
    parser_restart = subparsers.add_parser('restart', help='ریستارت instance')
    parser_restart.add_argument('name', help='نام instance')
    parser_restart.set_defaults(func=cmd_restart)
    
    # delete command
    parser_delete = subparsers.add_parser('delete', help='حذف instance')
    parser_delete.add_argument('name', help='نام instance')
    parser_delete.add_argument('-y', '--yes', action='store_true', help='بدون تایید')
    parser_delete.set_defaults(func=cmd_delete)
    
    # status command
    parser_status = subparsers.add_parser('status', help='نمایش وضعیت instance')
    parser_status.add_argument('name', help='نام instance')
    parser_status.set_defaults(func=cmd_status)
    
    # logs command
    parser_logs = subparsers.add_parser('logs', help='نمایش لاگ‌ها')
    parser_logs.add_argument('name', nargs='?', help='نام instance (اختیاری)')
    parser_logs.add_argument('-n', '--lines', type=int, default=50, help='تعداد خطوط')
    parser_logs.set_defaults(func=cmd_logs)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args) or 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ خطا: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
