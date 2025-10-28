"""
Setup validator for multi-account copy trading.
Run this to check if everything is configured correctly before starting.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*100)
    print(text)
    print("="*100 + "\n")


def print_check(text, status, details=None):
    """Print a check result."""
    icon = "✅" if status else "❌"
    print(f"{icon} {text}")
    if details:
        print(f"   {details}")


def check_environment_file():
    """Check if .env file exists."""
    print_header("STEP 1: Checking .env File")
    
    env_exists = os.path.exists('.env')
    print_check(".env file exists", env_exists)
    
    if not env_exists:
        print("\n⚠️  ACTION REQUIRED:")
        print("   1. Create a .env file in the project root")
        print("   2. Add your account credentials")
        print("   3. See QUICK_START_COPY_TRADING.md for template")
        return False
    
    return True


def check_master_account():
    """Check master account configuration."""
    print_header("STEP 2: Checking Master Account Configuration")
    
    required_vars = ['API_KEY', 'CLIENT_ID', 'PASSWORD', 'TOTP_SECRET', 'SECRET_KEY']
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        is_present = bool(value)
        all_present = all_present and is_present
        
        if is_present:
            # Show first/last few chars for verification
            if len(value) > 8:
                masked = value[:4] + "****" + value[-4:]
            else:
                masked = "****"
            print_check(var, True, f"Set: {masked}")
        else:
            print_check(var, False, "NOT SET")
    
    if not all_present:
        print("\n⚠️  ACTION REQUIRED:")
        print("   Master account credentials are incomplete")
        print("   Add missing variables to .env file")
        return False
    
    return True


def check_follower_accounts():
    """Check follower account configurations."""
    print_header("STEP 3: Checking Follower Account Configuration")
    
    follower_count = 0
    follower_number = 1
    
    while True:
        prefix = f'FOLLOWER_{follower_number}_'
        api_key = os.getenv(f'{prefix}API_KEY')
        
        if not api_key:
            break
        
        # Check all required fields for this follower
        required_vars = ['API_KEY', 'CLIENT_ID', 'PASSWORD', 'TOTP_SECRET', 'SECRET_KEY']
        all_present = True
        
        print(f"\n👤 Follower {follower_number}:")
        
        for var in required_vars:
            value = os.getenv(f'{prefix}{var}')
            is_present = bool(value)
            all_present = all_present and is_present
            
            if is_present:
                if len(value) > 8:
                    masked = value[:4] + "****" + value[-4:]
                else:
                    masked = "****"
                print_check(f"   {prefix}{var}", True, masked)
            else:
                print_check(f"   {prefix}{var}", False, "NOT SET")
        
        if all_present:
            follower_count += 1
        
        follower_number += 1
    
    print(f"\n📊 Total Follower Accounts Found: {follower_count}")
    
    if follower_count == 0:
        print("\n⚠️  WARNING:")
        print("   No follower accounts configured!")
        print("   Add follower credentials to .env file:")
        print("   FOLLOWER_1_API_KEY=...")
        print("   FOLLOWER_1_CLIENT_ID=...")
        print("   etc.")
        return False
    
    return True


def check_dependencies():
    """Check if required packages are installed."""
    print_header("STEP 4: Checking Dependencies")
    
    required_packages = [
        ('pyotp', 'pyotp'),
        ('SmartApi', 'smartapi-python'),
        ('dotenv', 'python-dotenv'),
    ]
    
    all_installed = True
    
    for package_name, pip_name in required_packages:
        try:
            __import__(package_name)
            print_check(f"{pip_name}", True, "Installed")
        except ImportError:
            print_check(f"{pip_name}", False, "NOT INSTALLED")
            all_installed = False
    
    if not all_installed:
        print("\n⚠️  ACTION REQUIRED:")
        print("   Install missing packages:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def check_file_structure():
    """Check if required files exist."""
    print_header("STEP 5: Checking File Structure")
    
    required_files = [
        'multi_account_config.py',
        'multi_account_client.py',
        'multi_account_copy_trader.py',
        'run_multi_account_copy_trading.py',
    ]
    
    all_present = True
    
    for filename in required_files:
        exists = os.path.exists(filename)
        print_check(filename, exists)
        all_present = all_present and exists
    
    if not all_present:
        print("\n⚠️  ERROR:")
        print("   Some required files are missing!")
        print("   Ensure all files were created correctly")
        return False
    
    return True


def check_logs_directory():
    """Check if logs directory exists."""
    print_header("STEP 6: Checking Logs Directory")
    
    logs_exist = os.path.exists('logs')
    print_check("logs/ directory", logs_exist)
    
    if not logs_exist:
        print("\n   Creating logs directory...")
        try:
            os.makedirs('logs')
            print_check("Created logs/ directory", True)
        except Exception as e:
            print_check("Failed to create logs/ directory", False, str(e))
            return False
    
    # Check write permission
    try:
        test_file = 'logs/.test_write'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print_check("logs/ directory is writable", True)
    except Exception as e:
        print_check("logs/ directory is writable", False, str(e))
        return False
    
    return True


def test_import_modules():
    """Test importing the copy trading modules."""
    print_header("STEP 7: Testing Module Imports")
    
    modules = [
        ('multi_account_config', 'MultiAccountConfig'),
        ('multi_account_client', 'ClientManager'),
        ('multi_account_copy_trader', 'MultiAccountCopyTrader'),
    ]
    
    all_imported = True
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            getattr(module, class_name)
            print_check(f"Import {module_name}.{class_name}", True)
        except Exception as e:
            print_check(f"Import {module_name}.{class_name}", False, str(e))
            all_imported = False
    
    if not all_imported:
        print("\n⚠️  ERROR:")
        print("   Failed to import required modules")
        print("   Check for syntax errors in the files")
        return False
    
    return True


def test_configuration_load():
    """Test loading configuration."""
    print_header("STEP 8: Testing Configuration Load")
    
    try:
        from multi_account_config import MultiAccountConfig
        
        config = MultiAccountConfig()
        
        # Check master
        if config.master_account:
            print_check("Master account loaded", True, 
                       f"Client ID: {config.master_account.client_id}")
        else:
            print_check("Master account loaded", False, "No master account")
            return False
        
        # Check followers
        follower_count = len(config.follower_accounts)
        print_check(f"Follower accounts loaded", True, f"Count: {follower_count}")
        
        for idx, follower in enumerate(config.follower_accounts, 1):
            print(f"   {idx}. {follower.name} (Client ID: {follower.client_id})")
        
        # Validate
        try:
            config.validate()
            print_check("Configuration validation", True, "All accounts valid")
        except Exception as e:
            print_check("Configuration validation", False, str(e))
            return False
        
        return True
        
    except Exception as e:
        print_check("Configuration load test", False, str(e))
        return False


def print_final_summary(all_checks_passed):
    """Print final summary and next steps."""
    print_header("VALIDATION SUMMARY")
    
    if all_checks_passed:
        print("🎉 " * 20)
        print("\n✅ ALL CHECKS PASSED!")
        print("\n🎉 " * 20)
        
        print("\n📋 You're ready to start copy trading!")
        print("\n🚀 Next Steps:")
        print("   1. Run unit tests:")
        print("      cd tests && python test_multi_account_copy_trading.py")
        print("\n   2. Start in dry run mode (safe testing):")
        print("      python run_multi_account_copy_trading.py")
        print("\n   3. Place a test order in your master account")
        print("\n   4. Watch it get detected (but not executed in dry run)")
        print("\n   5. When ready, change dry_run=False in the script")
        print("\n   6. Read QUICK_START_COPY_TRADING.md for detailed guide")
        
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\n⚠️  Please fix the issues above before proceeding.")
        print("\n📖 Resources:")
        print("   - QUICK_START_COPY_TRADING.md - Quick start guide")
        print("   - MULTI_ACCOUNT_COPY_TRADING.md - Full documentation")
        print("\n   Run this validator again after fixing issues:")
        print("   python validate_setup.py")
    
    print("\n" + "="*100 + "\n")


def main():
    """Run all validation checks."""
    print("\n" + "🔍 " * 40)
    print("MULTI-ACCOUNT COPY TRADING - SETUP VALIDATOR")
    print("🔍 " * 40)
    
    checks = [
        check_environment_file,
        check_master_account,
        check_follower_accounts,
        check_dependencies,
        check_file_structure,
        check_logs_directory,
        test_import_modules,
        test_configuration_load,
    ]
    
    results = []
    
    for check in checks:
        try:
            result = check()
            results.append(result)
            
            # Stop if critical check fails
            if not result and check in [check_environment_file, check_dependencies]:
                print("\n❌ Critical check failed. Cannot continue.")
                break
        except Exception as e:
            print(f"\n❌ Unexpected error in check: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
            break
    
    all_checks_passed = all(results)
    print_final_summary(all_checks_passed)
    
    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    sys.exit(main())
