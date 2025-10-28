#!/usr/bin/env python3
"""
Cleanup script - Remove unnecessary files and keep only essentials.
"""

import os
import shutil

# Files needed for production
ESSENTIAL_FILES = {
    # Core functionality
    'config.py',
    'smartapi_client.py',
    'smart_polling.py',
    'display.py',
    'web_ui.py',
    
    # Configuration
    '.env',
    '.env.example',
    '.gitignore',
    'requirements.txt',
    
    # Documentation
    'README.md',
    'TESTING_GUIDE.md',
    
    # Startup script
    'start_ui.sh',
    
    # Templates
    'templates/index.html',
    
    # Tests
    'tests/__init__.py',
    'tests/run_all_tests.py',
    'tests/test_config.py',
    'tests/test_order_detection.py',
    'tests/test_rate_limiting.py',
    'tests/test_smartapi_client.py',
    'tests/test_market_hours.py',
    'tests/test_integration.py',
    'tests/safety_checks.py',
}

# Files that can be removed (not needed for production)
REMOVABLE_FILES = {
    'main.py',  # Replaced by web_ui.py
    'order_monitor.py',  # Replaced by smart_polling.py
    'polling_monitor.py',  # Replaced by smart_polling.py
    'websocket_monitor.py',  # Not using WebSocket
    'copy_trading.py',  # Not implemented yet
    'order_utils.py',  # Functions moved to smart_polling.py
    'show_config.py',  # Utility script, not needed
    'test_detection.py',  # Replaced by proper tests
    
    # Documentation we don't need
    'RATE_LIMITS.md',
    'STRATEGY_COMPARISON.md',
    'WEB_UI_GUIDE.md',
    'YOUR_SETUP.md',
}


def analyze_files():
    """Analyze current files and recommend cleanup."""
    print("="*80)
    print("FILE CLEANUP ANALYSIS")
    print("="*80)
    print()
    
    print("📁 ESSENTIAL FILES (Keep these):")
    print("-" * 80)
    for file in sorted(ESSENTIAL_FILES):
        exists = "✅" if os.path.exists(file) else "❌ MISSING"
        print(f"  {exists} {file}")
    
    print()
    print("🗑️  REMOVABLE FILES (Can delete):")
    print("-" * 80)
    for file in sorted(REMOVABLE_FILES):
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024
            print(f"  📄 {file} ({size:.1f} KB)")
    
    # Check for unknown files
    all_py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    unknown_files = set(all_py_files) - ESSENTIAL_FILES - REMOVABLE_FILES
    
    if unknown_files:
        print()
        print("⚠️  UNKNOWN FILES (Review manually):")
        print("-" * 80)
        for file in sorted(unknown_files):
            print(f"  ❓ {file}")
    
    print()
    print("="*80)


def confirm_cleanup():
    """Ask user for confirmation before cleanup."""
    response = input("\nDo you want to remove unnecessary files? (yes/no): ")
    return response.lower() in ['yes', 'y']


def perform_cleanup(dry_run=True):
    """Remove unnecessary files."""
    if dry_run:
        print("\n🔍 DRY RUN - No files will be deleted")
    else:
        print("\n🗑️  CLEANING UP FILES...")
    
    removed_count = 0
    for file in REMOVABLE_FILES:
        if os.path.exists(file):
            if not dry_run:
                os.remove(file)
                print(f"  ✅ Removed: {file}")
            else:
                print(f"  Would remove: {file}")
            removed_count += 1
    
    if dry_run:
        print(f"\n{removed_count} files would be removed")
        print("Run with --execute to actually delete files")
    else:
        print(f"\n✅ Cleanup complete! Removed {removed_count} files")


if __name__ == '__main__':
    import sys
    
    analyze_files()
    
    if '--execute' in sys.argv:
        if confirm_cleanup():
            perform_cleanup(dry_run=False)
        else:
            print("\nCleanup cancelled.")
    else:
        print("\n💡 To actually delete files, run: python cleanup.py --execute")
        perform_cleanup(dry_run=True)
