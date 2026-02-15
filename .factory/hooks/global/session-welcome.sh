#!/usr/bin/env bash
# Global hook: Welcome message with system info

cat << 'EOF'
🤖 Factory Droid Session Started
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Model: Claude Haiku 4.5
Autonomy: High
Time: $(date '+%Y-%m-%d %H:%M:%S')

💡 Quick Tips:
   • /spec - Enter specification mode
   • /hooks - Manage hooks
   • Ctrl+R - View transcript
EOF

exit 0
