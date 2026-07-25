#!/bin/bash
#
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PAQET-MULTI - Multi-Server Manager for paqet clients               ║
# ║  v2.0.0                                                             ║
# ║                                                                     ║
# ║  Add, remove, start, stop, edit, and monitor as many paqet client   ║
# ║  connections as you want, each to a different server, each with     ║
# ║  its own local SOCKS5 port and its own systemd service.             ║
# ║                                                                     ║
# ║  Works alongside the official paqctl.sh installer/binary:           ║
# ║  https://github.com/SamNet-dev/paqctl                               ║
# ╚═══════════════════════════════════════════════════════════════════╝
#
# Usage (interactive menu):
#   sudo bash paqet-multi.sh
#
# Usage (non-interactive / scriptable):
#   sudo bash paqet-multi.sh add    <name> <ip:port> <key> [profile]
#   sudo bash paqet-multi.sh list
#   sudo bash paqet-multi.sh start  <name|all>
#   sudo bash paqet-multi.sh stop   <name|all>
#   sudo bash paqet-multi.sh restart <name|all>
#   sudo bash paqet-multi.sh remove <name>
#   sudo bash paqet-multi.sh edit   <name>
#   sudo bash paqet-multi.sh ping   <name>
#   sudo bash paqet-multi.sh logs   <name>
#   sudo bash paqet-multi.sh backup [path]
#   sudo bash paqet-multi.sh restore <path>
#
set -eo pipefail

# ── Config ────────────────────────────────────────────────────────────
BASE_DIR="/opt/paqctl"
BIN="$BASE_DIR/bin/paqet"
SERVERS_DIR="$BASE_DIR/servers"
SERVICE_PREFIX="paqet-"
DEFAULT_SOCKS_PORT=1080
BACKUP_DEFAULT="/root/paqet-multi-backup-$(date +%Y%m%d-%H%M%S).tar.gz"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
log_err()   { echo -e "${RED}[✗]${NC} $1"; }

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_err "این اسکریپت باید با sudo/root اجرا بشه (Run with sudo)"
        exit 1
    fi
}

check_binary() {
    if [ ! -x "$BIN" ]; then
        log_err "باینری paqet پیدا نشد: $BIN"
        log_warn "اول paqctl رسمی رو نصب کن:"
        echo "  curl -sL https://raw.githubusercontent.com/SamNet-dev/paqctl/main/paqctl.sh | sudo bash"
        exit 1
    fi
}

mkdir_setup() { mkdir -p "$SERVERS_DIR"; }

# ── Validation helpers ───────────────────────────────────────────────
_validate_port() { [[ "$1" =~ ^[0-9]+$ ]] && [ "$1" -ge 1 ] && [ "$1" -le 65535 ]; }
_validate_ip()   { [[ "$1" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; }
_validate_mac()  { [[ "$1" =~ ^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$ ]]; }
_slug()          { echo "$1" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-'; }

list_names() {
    [ -d "$SERVERS_DIR" ] || return 0
    for f in "$SERVERS_DIR"/*.yaml; do
        [ -f "$f" ] && basename "$f" .yaml
    done
}

server_exists() { [ -f "$SERVERS_DIR/${1}.yaml" ]; }

port_in_use_by_us() {
    local port="$1"
    for f in "$SERVERS_DIR"/*.yaml; do
        [ -f "$f" ] || continue
        grep -q "listen: \"127.0.0.1:${port}\"" "$f" 2>/dev/null && return 0
    done
    return 1
}

next_free_port() {
    local port=$DEFAULT_SOCKS_PORT
    while port_in_use_by_us "$port" || ss -ltn 2>/dev/null | grep -q ":${port} "; do
        port=$((port + 1))
    done
    echo "$port"
}

detect_network() {
    local route_line iface
    route_line=$(ip route show default 2>/dev/null | head -1)
    if [[ "$route_line" == *" via "* ]]; then
        iface=$(echo "$route_line" | awk '{print $5}')
    elif [[ "$route_line" == *" dev "* ]]; then
        iface=$(echo "$route_line" | awk '{print $3}')
    fi
    [ -z "$iface" ] && iface=$(ip -o link show | awk -F': ' '{print $2}' | grep -vE '^(lo|docker|br-|veth|tun|tap|wg)' | head -1)
    DETECTED_IFACE="$iface"
    DETECTED_IP=$(ip -4 addr show "$iface" 2>/dev/null | awk '/inet /{print $2}' | cut -d/ -f1 | head -1)
    local gw=""
    [[ "$route_line" == *" via "* ]] && gw=$(echo "$route_line" | awk '{print $3}')
    DETECTED_GATEWAY="$gw"
    DETECTED_GW_MAC=""
    if [ -n "$gw" ]; then
        DETECTED_GW_MAC=$(ip neigh show "$gw" 2>/dev/null | awk '/lladdr/{print $5; exit}')
        if [ -z "$DETECTED_GW_MAC" ]; then
            ping -c1 -W1 "$gw" &>/dev/null || true
            sleep 1
            DETECTED_GW_MAC=$(ip neigh show "$gw" 2>/dev/null | awk '/lladdr/{print $5; exit}')
        fi
    fi
}

ask() { local prompt="$1" def="$2" input; read -rp " $prompt${def:+ [$def]}: " input < /dev/tty || true; echo "${input:-$def}"; }

profile_values() {
    # sets: conn mtu wnd nodelay
    case "$1" in
        highloss|2) profile="highloss"; conn=4; mtu=1300; wnd=1024; nodelay=0 ;;
        cdn|3)      profile="cdn";      conn=8; mtu=1400; wnd=2048; nodelay=0 ;;
        gaming|4)   profile="gaming";   conn=2; mtu=1200; wnd=512;  nodelay=1 ;;
        *)          profile="standard"; conn=2; mtu=1350; wnd=1024; nodelay=0 ;;
    esac
}

write_config() {
    # args: file port iface lip gwmac remote key conn mtu wnd nodelay
    local file="$1" port="$2" iface="$3" lip="$4" gwmac="$5" remote="$6" key="$7" conn="$8" mtu="$9" wnd="${10}" nodelay="${11}"
    cat > "$file" << EOF
role: "client"
log:
  level: "info"
socks5:
  - listen: "127.0.0.1:${port}"
network:
  interface: "${iface}"
  ipv4:
    addr: "${lip}:0"
    router_mac: "${gwmac}"
server:
  addr: "${remote}"
transport:
  protocol: "kcp"
  kcp:
    mode: "fast"
    key: "${key}"
    conn: ${conn}
    mtu: ${mtu}
    sndwnd: ${wnd}
    rcvwnd: ${wnd}
    nodelay: ${nodelay}
EOF
    chmod 600 "$file"
}

write_service() {
    local name="$1"
    cat > "/etc/systemd/system/${SERVICE_PREFIX}${name}.service" << EOF
[Unit]
Description=Paqet Client - ${name}
After=network.target

[Service]
ExecStart=${BIN} run -c ${SERVERS_DIR}/${name}.yaml
Restart=always
RestartSec=3
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
}

# ── Add server ────────────────────────────────────────────────────────
do_add() {
    local name="$1" remote="$2" key="$3" profile_choice="${4:-1}"
    local iface lip gwmac port conn mtu wnd nodelay

    if [ -z "$name" ]; then
        echo ""
        echo -e "${CYAN}═══ افزودن سرور جدید ═══${NC}"
        while true; do
            name=$(_slug "$(ask "اسم سرور (مثلا germany1)" "")")
            [ -z "$name" ] && { log_warn "اسم نامعتبره"; continue; }
            server_exists "$name" && { log_warn "این اسم قبلاً استفاده شده"; continue; }
            break
        done
        while true; do
            remote=$(ask "آدرس سرور (IP:PORT)" "")
            local rip="${remote%:*}" rport="${remote##*:}"
            _validate_ip "$rip" && _validate_port "$rport" && break
            log_warn "فرمت باید IP:PORT باشه"
        done
        key=$(ask "کلید رمزنگاری" "")
        [ -z "$key" ] && { log_err "کلید الزامیه"; return 1; }

        detect_network
        echo ""
        log_info "شبکه شناسایی‌شده: iface=${DETECTED_IFACE:-?} ip=${DETECTED_IP:-?} gw_mac=${DETECTED_GW_MAC:-?}"
        iface=$(ask "اینترفیس شبکه" "${DETECTED_IFACE:-eth0}")
        lip=$(ask "آی‌پی محلی" "${DETECTED_IP:-}")
        gwmac=$(ask "مک آدرس گیت‌وی" "${DETECTED_GW_MAC:-}")

        echo ""
        echo " پروفایل عملکرد: 1) استاندارد  2) پرافت/DPI سنگین  3) پرسرعت/CDN  4) کم‌تاخیر/گیمینگ"
        profile_choice=$(ask "انتخاب [1-4]" "1")
    else
        name=$(_slug "$name")
        server_exists "$name" && { log_err "سرور «$name» از قبل وجود داره"; return 1; }
        local rip="${remote%:*}" rport="${remote##*:}"
        if ! _validate_ip "$rip" || ! _validate_port "$rport"; then
            log_err "آدرس سرور باید IP:PORT باشه"; return 1
        fi
        [ -z "$key" ] && { log_err "کلید الزامیه"; return 1; }
        detect_network
        iface="${DETECTED_IFACE:-eth0}"
        lip="${DETECTED_IP:-}"
        gwmac="${DETECTED_GW_MAC:-}"
    fi

    if [ -z "$gwmac" ] || ! _validate_mac "$gwmac"; then
        log_warn "مک گیت‌وی خودکار پیدا نشد"
        gwmac=$(ask "مک آدرس گیت‌وی رو دستی بده (aa:bb:cc:dd:ee:ff)" "")
        if ! _validate_mac "$gwmac"; then
            log_err "مک آدرس گیت‌وی معتبر لازمه"; return 1
        fi
    fi

    profile_values "$profile_choice"
    port=$(next_free_port)

    write_config "$SERVERS_DIR/${name}.yaml" "$port" "$iface" "$lip" "$gwmac" "$remote" "$key" "$conn" "$mtu" "$wnd" "$nodelay"
    log_ok "کانفیگ ساخته شد: $SERVERS_DIR/${name}.yaml (پروکسی 127.0.0.1:${port})"

    write_service "$name"
    if command -v systemctl &>/dev/null && [ -d /run/systemd/system ]; then
        systemctl enable --now "${SERVICE_PREFIX}${name}.service" &>/dev/null
        sleep 1
        if systemctl is-active --quiet "${SERVICE_PREFIX}${name}.service"; then
            log_ok "سرور «${name}» روشن شد. پروکسی: 127.0.0.1:${port}"
        else
            log_err "سرویس بالا نیومد. لاگ: journalctl -u ${SERVICE_PREFIX}${name}.service -n 50"
        fi
    else
        log_warn "systemd نیست. اجرای دستی: sudo ${BIN} run -c ${SERVERS_DIR}/${name}.yaml"
    fi
}

# ── Edit existing server ────────────────────────────────────────────
do_edit() {
    local name="$1"
    [ -z "$name" ] && { name=$(pick_server) || return 1; }
    server_exists "$name" || { log_err "سرور «$name» پیدا نشد"; return 1; }

    local f="$SERVERS_DIR/${name}.yaml"
    local cur_remote cur_port
    cur_remote=$(grep 'addr:' "$f" | tail -1 | sed 's/.*addr: "\(.*\)"/\1/')
    cur_port=$(grep 'listen:' "$f" | sed 's/.*127.0.0.1:\([0-9]*\).*/\1/')

    echo ""
    echo -e "${CYAN}═══ ویرایش سرور «$name» ═══${NC}"
    local new_remote new_key
    new_remote=$(ask "آدرس سرور جدید (خالی = بدون تغییر: $cur_remote)" "")
    new_key=$(ask "کلید جدید (خالی = بدون تغییر)" "")

    cp "$f" "${f}.bak.$(date +%s)"

    [ -n "$new_remote" ] && sed -i "s|addr: \".*:.*\"$|addr: \"${new_remote}\"|" "$f" 2>/dev/null
    if [ -n "$new_remote" ]; then
        # server addr line only (last addr line is server, first is ipv4 - be precise)
        python3 - "$f" "$new_remote" << 'PYEOF' 2>/dev/null || true
import sys, re
f, remote = sys.argv[1], sys.argv[2]
s = open(f).read()
s = re.sub(r'(server:\s*\n\s*addr:\s*")[^"]*(")', r'\g<1>' + remote + r'\g<2>', s)
open(f, 'w').write(s)
PYEOF
    fi
    if [ -n "$new_key" ]; then
        sed -i "s|key: \".*\"|key: \"${new_key}\"|" "$f"
    fi

    log_ok "کانفیگ «$name» به‌روز شد (نسخه قبلی بکاپ گرفته شد)"
    if systemctl is-active --quiet "${SERVICE_PREFIX}${name}.service" 2>/dev/null; then
        systemctl restart "${SERVICE_PREFIX}${name}.service"
        log_ok "سرویس ری‌استارت شد"
    fi
}

# ── List / status ─────────────────────────────────────────────────────
list_servers() {
    echo ""
    local names; names=$(list_names)
    if [ -z "$names" ]; then
        log_warn "هنوز هیچ سروری اضافه نشده"
        return
    fi
    printf " %-3s %-18s %-22s %-12s %-10s\n" "#" "نام" "سرور" "SOCKS5" "وضعیت"
    echo " ---------------------------------------------------------------------"
    local i=1
    for name in $names; do
        local f="$SERVERS_DIR/${name}.yaml"
        local remote port status
        remote=$(grep 'addr:' "$f" | tail -1 | sed 's/.*addr: "\(.*\)"/\1/')
        port=$(grep 'listen:' "$f" | sed 's/.*127.0.0.1:\([0-9]*\).*/\1/')
        if systemctl is-active --quiet "${SERVICE_PREFIX}${name}.service" 2>/dev/null; then
            status="${GREEN}روشن${NC}"
        else
            status="${RED}خاموش${NC}"
        fi
        printf " %-3s %-18s %-22s 127.0.0.1:%-6s " "$i" "$name" "$remote" "$port"
        echo -e "$status"
        i=$((i + 1))
    done
}

pick_server() {
    local names; names=($(list_names))
    if [ ${#names[@]} -eq 0 ]; then
        log_warn "هیچ سروری موجود نیست"
        return 1
    fi
    list_servers
    echo ""
    local sel; sel=$(ask "شماره یا اسم سرور" "")
    if [[ "$sel" =~ ^[0-9]+$ ]] && [ "$sel" -ge 1 ] && [ "$sel" -le "${#names[@]}" ]; then
        echo "${names[$((sel-1))]}"
    else
        for n in "${names[@]}"; do
            [ "$n" = "$sel" ] && { echo "$n"; return 0; }
        done
        log_err "پیدا نشد"
        return 1
    fi
}

do_start() {
    local n="$1"
    if [ "$n" = "all" ]; then
        for name in $(list_names); do
            systemctl start "${SERVICE_PREFIX}${name}.service" && log_ok "«$name» روشن شد"
        done
        return
    fi
    [ -z "$n" ] && { n=$(pick_server) || return 1; }
    systemctl start "${SERVICE_PREFIX}${n}.service" && log_ok "«$n» روشن شد"
}

do_stop() {
    local n="$1"
    if [ "$n" = "all" ]; then
        for name in $(list_names); do
            systemctl stop "${SERVICE_PREFIX}${name}.service" && log_ok "«$name» خاموش شد"
        done
        return
    fi
    [ -z "$n" ] && { n=$(pick_server) || return 1; }
    systemctl stop "${SERVICE_PREFIX}${n}.service" && log_ok "«$n» خاموش شد"
}

do_restart() {
    local n="$1"
    if [ "$n" = "all" ]; then
        for name in $(list_names); do
            systemctl restart "${SERVICE_PREFIX}${name}.service" && log_ok "«$name» ری‌استارت شد"
        done
        return
    fi
    [ -z "$n" ] && { n=$(pick_server) || return 1; }
    systemctl restart "${SERVICE_PREFIX}${n}.service" && log_ok "«$n» ری‌استارت شد"
}

do_remove() {
    local n="$1"
    [ -z "$n" ] && { n=$(pick_server) || return 1; }
    server_exists "$n" || { log_err "سرور «$n» پیدا نشد"; return 1; }
    read -rp " مطمئنی می‌خوای «$n» رو کامل حذف کنی؟ [y/N]: " conf < /dev/tty || true
    if [[ "$conf" =~ ^[yY]$ ]]; then
        systemctl stop "${SERVICE_PREFIX}${n}.service" 2>/dev/null || true
        systemctl disable "${SERVICE_PREFIX}${n}.service" 2>/dev/null || true
        rm -f "/etc/systemd/system/${SERVICE_PREFIX}${n}.service"
        rm -f "$SERVERS_DIR/${n}.yaml" "$SERVERS_DIR/${n}.yaml".bak.*
        systemctl daemon-reload
        log_ok "«$n» حذف شد"
    fi
}

do_logs() {
    local n="$1"
    [ -z "$n" ] && { n=$(pick_server) || return 1; }
    journalctl -u "${SERVICE_PREFIX}${n}.service" -n 50 --no-pager
}

do_ping() {
    local n="$1"
    [ -z "$n" ] && { n=$(pick_server) || return 1; }
    server_exists "$n" || { log_err "سرور «$n» پیدا نشد"; return 1; }
    log_info "تست اتصال به «$n»..."
    if "$BIN" ping -c "$SERVERS_DIR/${n}.yaml" 2>&1; then
        log_ok "اتصال برقراره"
    else
        log_err "پینگ ناموفق بود (paqet ممکنه این ساب‌کامند رو نداشته باشه — به‌جاش وضعیت سرویس رو با گزینه 6 چک کن)"
    fi
}

do_backup() {
    local path="${1:-$BACKUP_DEFAULT}"
    tar -czf "$path" -C "$BASE_DIR" servers 2>/dev/null
    log_ok "بکاپ ذخیره شد: $path"
}

do_restore() {
    local path="$1"
    [ -z "$path" ] && { log_err "مسیر فایل بکاپ رو بده"; return 1; }
    [ -f "$path" ] || { log_err "فایل پیدا نشد: $path"; return 1; }
    tar -xzf "$path" -C "$BASE_DIR"
    log_ok "بکاپ بازیابی شد. حالا برای هرکدوم سرویس systemd بساز یا از منو استفاده کن."
    for f in "$SERVERS_DIR"/*.yaml; do
        [ -f "$f" ] || continue
        local name; name=$(basename "$f" .yaml)
        server_exists "$name" && [ ! -f "/etc/systemd/system/${SERVICE_PREFIX}${name}.service" ] && write_service "$name"
    done
    log_ok "سرویس‌های systemd برای سرورهای بازیابی‌شده ساخته شدن (خاموش، دستی روشنشون کن)"
}

# ── Menu ──────────────────────────────────────────────────────────────
main_menu() {
    while true; do
        echo ""
        echo -e "${CYAN}═══════════════════════════════════════════${NC}"
        echo -e "${BOLD}  PAQET MULTI-SERVER MANAGER v2.0.0${NC}"
        echo -e "${CYAN}═══════════════════════════════════════════${NC}"
        list_servers
        echo ""
        echo "  1) افزودن سرور جدید"
        echo "  2) روشن کردن یک سرور        9) روشن کردن همه"
        echo "  3) خاموش کردن یک سرور      10) خاموش کردن همه"
        echo "  4) ری‌استارت یک سرور       11) ری‌استارت همه"
        echo "  5) حذف یک سرور"
        echo "  6) نمایش لاگ یک سرور"
        echo "  7) ویرایش یک سرور (آدرس/کلید)"
        echo "  8) تست اتصال (ping) یک سرور"
        echo " 12) بکاپ از همه کانفیگ‌ها"
        echo " 13) بازیابی از فایل بکاپ"
        echo "  0) خروج"
        echo ""
        local choice; choice=$(ask "انتخاب" "")
        case "$choice" in
            1) do_add ;;
            2) do_start ;;
            3) do_stop ;;
            4) do_restart ;;
            5) do_remove ;;
            6) do_logs ;;
            7) do_edit ;;
            8) do_ping ;;
            9) do_start all ;;
            10) do_stop all ;;
            11) do_restart all ;;
            12) do_backup ;;
            13) local p; p=$(ask "مسیر فایل بکاپ" ""); do_restore "$p" ;;
            0) exit 0 ;;
            *) log_warn "گزینه نامعتبر" ;;
        esac
    done
}

# ── Main ──────────────────────────────────────────────────────────────
check_root
check_binary
mkdir_setup

case "${1:-menu}" in
    add)      shift; do_add "$@" ;;
    list)     list_servers ;;
    start)    do_start "$2" ;;
    stop)     do_stop "$2" ;;
    restart)  do_restart "$2" ;;
    remove)   do_remove "$2" ;;
    edit)     do_edit "$2" ;;
    ping)     do_ping "$2" ;;
    logs)     do_logs "$2" ;;
    backup)   do_backup "$2" ;;
    restore)  do_restore "$2" ;;
    menu)     main_menu ;;
    *)
        echo "Usage: $0 {add|list|start|stop|restart|remove|edit|ping|logs|backup|restore|menu} [args]"
        exit 1
        ;;
esac
