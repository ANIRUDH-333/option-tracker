#!/bin/bash

echo "=================================="
echo "Copy Trading Monitor - Start"
echo "=================================="
echo ""

# Run safety checks first
echo "🔍 Running pre-flight safety checks..."
python tests/safety_checks.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ SAFETY CHECKS FAILED!"
    echo "   Fix the issues above before starting."
    echo ""
    exit 1
fi

echo ""
echo "✅ Safety checks passed!"
echo ""
echo "Starting web UI..."
echo "📊 Dashboard: http://localhost:5000"
echo ""

python web_ui.py
