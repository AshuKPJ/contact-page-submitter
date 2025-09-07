# auto_fix_imports.py
# Run this script to automatically fix all problematic settings imports

import os
import re
import shutil
from datetime import datetime


def backup_file(file_path):
    """Create a backup of the file before modifying"""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    return backup_path


def fix_settings_imports(file_path):
    """Fix settings imports in a single file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes_made = False

        # Pattern 1: Direct settings import
        pattern1 = r"from\s+app\.core\.config\s+import\s+settings"
        if re.search(pattern1, content):
            content = re.sub(
                pattern1, "from app.core.config import get_settings", content
            )

            # Add settings = get_settings() after the import if not already there
            if "settings = get_settings()" not in content:
                content = re.sub(
                    r"(from app\.core\.config import get_settings)",
                    r"\1\nsettings = get_settings()",
                    content,
                )
            changes_made = True

        # Pattern 2: Multiple imports including settings
        pattern2 = (
            r"from\s+app\.core\.config\s+import\s+([^,\n]*,\s*)*settings([^,\n]*,\s*)*"
        )
        if re.search(pattern2, content):
            # Replace complex import with get_settings
            content = re.sub(
                pattern2, "from app.core.config import get_settings", content
            )

            if "settings = get_settings()" not in content:
                content = re.sub(
                    r"(from app\.core\.config import get_settings)",
                    r"\1\nsettings = get_settings()",
                    content,
                )
            changes_made = True

        # Write the fixed content back to the file
        if changes_made and content != original_content:
            backup_path = backup_file(file_path)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ Fixed: {file_path}")
            print(f"   Backup: {backup_path}")
            return True
        else:
            print(f"⏭️  Skipped: {file_path} (no changes needed)")
            return False

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def find_and_fix_all_imports(directory="."):
    """Find and fix all problematic settings imports"""
    fixed_files = []

    # List of files to fix based on your scan results
    files_to_fix = [
        "./backend/debug_endpoints.py",
        "./backend/app/api/endpoints/health.py",
        "./backend/app/core/database.py",
        "./backend/app/core/encryption.py",
        "./backend/app/middleware/cors.py",
        "./backend/app/services/browser_automation_service.py",
        "./backend/app/services/browser_service.py",
        "./backend/app/services/captcha_service.py",
        "./backend/app/workers/browser_automation.py",
        "./backend/app/workers/__init__.py",
        "./SupportiveScripts/check_database.py",
        "./SupportiveScripts/create_tables.py",
        "./SupportiveScripts/fix_backend.py",
        "./SupportiveScripts/fix_database_schema.py",
        "./SupportiveScripts/run.py",
        "./SupportiveScripts/update_passwords.py",
    ]

    for file_path in files_to_fix:
        # Convert to absolute path and check if file exists
        abs_path = os.path.abspath(file_path)
        if os.path.exists(abs_path):
            if fix_settings_imports(abs_path):
                fixed_files.append(abs_path)
        else:
            print(f"⚠️  File not found: {file_path}")

    return fixed_files


if __name__ == "__main__":
    print("🔧 Starting automated import fixing...")
    print("📁 Creating backups of all files before modification...")

    fixed_files = find_and_fix_all_imports()

    print(f"\n✅ Successfully fixed {len(fixed_files)} files")

    if fixed_files:
        print("\n📋 Fixed files:")
        for file_path in fixed_files:
            print(f"  - {file_path}")

        print("\n💡 Next steps:")
        print("1. Update your app/core/config.py with the backward-compatible version")
        print("2. Restart your FastAPI server: uvicorn main:app --reload")
        print("3. Test your API endpoints")

        print("\n🔄 To restore from backups if needed:")
        print("   Find .backup_* files and rename them back to original names")
    else:
        print("ℹ️  No files were modified")
