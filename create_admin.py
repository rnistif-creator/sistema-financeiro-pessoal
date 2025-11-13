import argparse
import sys
from getpass import getpass

from app.main import SessionLocal
from app.auth import create_user, get_user_by_email, get_password_hash, UserCreate


def main():
    parser = argparse.ArgumentParser(description="Create or promote an admin user")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--name", required=True, help="Admin name")
    parser.add_argument("--password", help="Admin password (if omitted, will prompt)")
    args = parser.parse_args()

    password = args.password
    if not password:
        password = getpass("Password: ")
        if not password:
            print("Password is required", file=sys.stderr)
            sys.exit(2)

    db = SessionLocal()
    try:
        user = get_user_by_email(db, args.email)
        if user:
            # Promote to admin and optionally reset password
            user.admin = True
            if password:
                user.senha_hash = get_password_hash(password)
            if args.name and args.name.strip() and user.nome != args.name:
                user.nome = args.name
            db.commit()
            db.refresh(user)
            print(f"User promoted to admin: {user.email} (id={user.id})")
        else:
            # Create new admin user
            created = create_user(db, UserCreate(email=args.email, nome=args.name, password=password), is_admin=True)
            print(f"Admin user created: {created.email} (id={created.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
