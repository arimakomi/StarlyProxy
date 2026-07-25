#!/bin/bash
#
# Health Check Script for StarlyProxy
# بررسی سلامت instance ها و ریستارت خودکار در صورت نیاز
#

STARLYPROXY_CLI="/usr/local/bin/starlyproxy"

# Check if CLI exists
if [ ! -f "$STARLYPROXY_CLI" ]; then
    echo "❌ StarlyProxy CLI not found at $STARLYPROXY_CLI"
    exit 1
fi

# Get list of instances
INSTANCES=$($STARLYPROXY_CLI list 2>/dev/null | tail -n +3 | awk '{print $1}')

if [ -z "$INSTANCES" ]; then
    echo "ℹ️  No instances configured"
    exit 0
fi

echo "🔍 Checking health of instances..."

for INSTANCE in $INSTANCES; do
    # Get status
    STATUS=$($STARLYPROXY_CLI status "$INSTANCE" 2>/dev/null | grep "وضعیت:" | awk '{print $2}')
    
    if [ "$STATUS" != "running" ]; then
        echo "⚠️  Instance '$INSTANCE' is $STATUS"
        
        # Check if auto-restart is enabled
        # For now, restart all stopped instances
        echo "🔄 Attempting to restart '$INSTANCE'..."
        $STARLYPROXY_CLI start "$INSTANCE" >/dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "✅ Successfully restarted '$INSTANCE'"
        else
            echo "❌ Failed to restart '$INSTANCE'"
        fi
    else
        echo "✅ Instance '$INSTANCE' is healthy"
    fi
done

echo ""
echo "✓ Health check complete"
