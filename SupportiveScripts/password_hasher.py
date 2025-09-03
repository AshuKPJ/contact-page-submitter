#!/usr/bin/env python3
"""
Simple Password Hasher - Generate and verify password hashes
No complex setup required - just run the script!
"""

import hashlib
import secrets
import getpass
import sys

# Try to import bcrypt (optional but recommended)
try:
    import bcrypt

    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    print("Note: bcrypt not installed. Using SHA256 instead.")
    print("For better security, install: pip install bcrypt\n")


class SimplePasswordHasher:
    """Simple password hashing utility"""

    @staticmethod
    def hash_with_bcrypt(password: str) -> str:
        """Hash password using bcrypt (most secure)"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_bcrypt(password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    @staticmethod
    def hash_with_sha256(password: str, salt: str = None) -> tuple:
        """Hash password using SHA256 with salt"""
        if salt is None:
            salt = secrets.token_hex(16)

        # Combine password and salt
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()

        # Return in format: algorithm$salt$hash
        return f"sha256${salt}${pwd_hash}"

    @staticmethod
    def verify_sha256(password: str, hash_string: str) -> bool:
        """Verify password against SHA256 hash"""
        try:
            # Parse the hash string
            parts = hash_string.split("$")
            if len(parts) != 3 or parts[0] != "sha256":
                return False

            algorithm, salt, stored_hash = parts

            # Hash the password with the same salt
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()

            return test_hash == stored_hash
        except:
            return False

    @staticmethod
    def hash_simple_sha256(password: str) -> str:
        """Simple SHA256 without salt (NOT recommended for production)"""
        return hashlib.sha256(password.encode()).hexdigest()


def main():
    """Main program"""
    hasher = SimplePasswordHasher()

    print("=" * 60)
    print("SIMPLE PASSWORD HASHER")
    print("=" * 60)

    while True:
        print("\nOptions:")
        print("1. Hash a password")
        print("2. Verify a password")
        print("3. Batch hash passwords")
        print("4. Quick demo")
        print("5. Exit")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            # Hash a password
            print("\n--- Hash Password ---")
            password = getpass.getpass("Enter password to hash: ")

            if not password:
                print("Password cannot be empty!")
                continue

            print("\nSelect hashing method:")
            if BCRYPT_AVAILABLE:
                print("1. BCrypt (Most Secure - Recommended)")
                print("2. SHA256 with Salt (Good)")
                print("3. Simple SHA256 (Not Recommended)")
                method = input("Choice (1-3): ").strip()
            else:
                print("1. SHA256 with Salt (Good)")
                print("2. Simple SHA256 (Not Recommended)")
                method = input("Choice (1-2): ").strip()
                if method == "1":
                    method = "2"
                elif method == "2":
                    method = "3"

            print("\n" + "=" * 60)
            print("GENERATED HASH:")
            print("=" * 60)

            if method == "1" and BCRYPT_AVAILABLE:
                hashed = hasher.hash_with_bcrypt(password)
                print(f"Method: BCrypt")
                print(f"Hash: {hashed}")
                print("\nTo verify, use this hash with option 2")
            elif method == "2":
                hashed = hasher.hash_with_sha256(password)
                print(f"Method: SHA256 with Salt")
                print(f"Hash: {hashed}")
                print("\nTo verify, use this hash with option 2")
            elif method == "3":
                hashed = hasher.hash_simple_sha256(password)
                print(f"Method: Simple SHA256 (No Salt)")
                print(f"Hash: {hashed}")
                print("\n⚠️  Warning: This method is not secure for production use!")
            else:
                print("Invalid choice!")

            print("=" * 60)

        elif choice == "2":
            # Verify a password
            print("\n--- Verify Password ---")
            password = getpass.getpass("Enter password to verify: ")
            hash_string = input("Enter hash to verify against: ").strip()

            if not password or not hash_string:
                print("Password and hash cannot be empty!")
                continue

            # Try to identify and verify
            is_valid = False
            hash_type = "Unknown"

            if BCRYPT_AVAILABLE and hash_string.startswith("$2"):
                # BCrypt hash
                hash_type = "BCrypt"
                is_valid = hasher.verify_bcrypt(password, hash_string)
            elif hash_string.startswith("sha256$"):
                # SHA256 with salt
                hash_type = "SHA256 with Salt"
                is_valid = hasher.verify_sha256(password, hash_string)
            elif len(hash_string) == 64:
                # Simple SHA256
                hash_type = "Simple SHA256"
                is_valid = hasher.hash_simple_sha256(password) == hash_string

            print("\n" + "=" * 60)
            print(f"Hash Type: {hash_type}")
            print(f"Result: {'✓ PASSWORD VALID' if is_valid else '✗ PASSWORD INVALID'}")
            print("=" * 60)

        elif choice == "3":
            # Batch hash passwords
            print("\n--- Batch Hash Passwords ---")
            print("Enter passwords (one per line, empty line to finish):")

            passwords = []
            while True:
                pwd = getpass.getpass(f"Password {len(passwords) + 1}: ")
                if not pwd:
                    break
                passwords.append(pwd)

            if passwords:
                print("\nSelect hashing method:")
                if BCRYPT_AVAILABLE:
                    print("1. BCrypt (Recommended)")
                    print("2. SHA256 with Salt")
                    method = input("Choice (1-2): ").strip()
                else:
                    method = "2"
                    print("Using SHA256 with Salt...")

                print("\n" + "=" * 60)
                print("HASHED PASSWORDS:")
                print("=" * 60)

                for i, pwd in enumerate(passwords, 1):
                    if method == "1" and BCRYPT_AVAILABLE:
                        hashed = hasher.hash_with_bcrypt(pwd)
                    else:
                        hashed = hasher.hash_with_sha256(pwd)

                    print(f"\nPassword {i}:")
                    print(f"  Original: {'*' * len(pwd)}")
                    print(f"  Hash: {hashed}")

                print("=" * 60)

        elif choice == "4":
            # Quick demo
            print("\n--- Quick Demo ---")
            demo_password = "DemoPassword123!"

            print(f"Demo Password: {demo_password}")
            print("\nGenerating hashes...")

            # Generate different types of hashes
            if BCRYPT_AVAILABLE:
                bcrypt_hash = hasher.hash_with_bcrypt(demo_password)
                print(f"\n1. BCrypt Hash:")
                print(f"   {bcrypt_hash}")
                print(
                    f"   Verified: {hasher.verify_bcrypt(demo_password, bcrypt_hash)}"
                )

            sha256_salt_hash = hasher.hash_with_sha256(demo_password)
            print(f"\n2. SHA256 with Salt:")
            print(f"   {sha256_salt_hash}")
            print(
                f"   Verified: {hasher.verify_sha256(demo_password, sha256_salt_hash)}"
            )

            simple_sha256 = hasher.hash_simple_sha256(demo_password)
            print(f"\n3. Simple SHA256:")
            print(f"   {simple_sha256}")
            print(
                f"   Verified: {hasher.hash_simple_sha256(demo_password) == simple_sha256}"
            )

            # Show what happens with wrong password
            print(f"\n4. Testing with wrong password:")
            wrong_password = "WrongPassword"
            if BCRYPT_AVAILABLE:
                print(f"   BCrypt: {hasher.verify_bcrypt(wrong_password, bcrypt_hash)}")
            print(
                f"   SHA256 with Salt: {hasher.verify_sha256(wrong_password, sha256_salt_hash)}"
            )
            print(
                f"   Simple SHA256: {hasher.hash_simple_sha256(wrong_password) == simple_sha256}"
            )

        elif choice == "5":
            print("\nGoodbye!")
            break

        else:
            print("Invalid choice! Please enter 1-5.")


def quick_hash(password: str = None):
    """Quick function to hash a password from command line"""
    if password is None:
        password = getpass.getpass("Enter password: ")

    hasher = SimplePasswordHasher()

    if BCRYPT_AVAILABLE:
        hashed = hasher.hash_with_bcrypt(password)
        print(f"\nBCrypt Hash: {hashed}")
    else:
        hashed = hasher.hash_with_sha256(password)
        print(f"\nSHA256 Hash: {hashed}")

    return hashed


# Allow running with command line argument
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            # Quick hash mode
            if len(sys.argv) > 2:
                quick_hash(sys.argv[2])
            else:
                quick_hash()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python password_hasher.py          # Run interactive mode")
            print("  python password_hasher.py --quick  # Quick hash a password")
            print(
                "  python password_hasher.py --quick 'password'  # Hash specific password"
            )
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Run interactive mode
        main()
