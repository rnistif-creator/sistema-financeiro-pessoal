import argparse
import sys
from getpass import getpass

from app.main import SessionLocal
from app.auth import create_user, get_user_by_email, get_password_hash, UserCreate, validate_password_strength


def main():
    parser = argparse.ArgumentParser(description="Create or promote an admin user (supports weak bootstrap)")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--name", required=True, help="Admin name")
    parser.add_argument("--password", help="Admin password (if omitted, will prompt)")
    parser.add_argument("--force-weak", action="store_true", help="Allow weak password (bootstrap only, e.g. 123456)")
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
            user.admin = True
            reset_msg = ""
            if password:
                if not validate_password_strength(password):
                    if not args.force_weak:
                        print("Senha fraca. Use --force-weak para permitir bootstrap com senha fraca.", file=sys.stderr)
                        sys.exit(3)
                user.senha_hash = get_password_hash(password)
                reset_msg = " (password reset)"
            if args.name and args.name.strip() and user.nome != args.name:
                user.nome = args.name
            db.commit()
            db.refresh(user)
            print(f"User promoted to admin: {user.email} (id={user.id}){reset_msg}")
        else:
            # Create new admin user (weak allowed with flag)
            if not validate_password_strength(password):
                if not args.force_weak:
                    print("Senha fraca. Use --force-weak para criar mesmo assim (bootstrap).", file=sys.stderr)
                    sys.exit(4)
            created = create_user(db, UserCreate(email=args.email, nome=args.name, password=(password if validate_password_strength(password) else 'XTemp123!')), is_admin=True)
            if not validate_password_strength(password):
                # Overwrite with provided weak password after creation bypass
                created.senha_hash = get_password_hash(password)
                db.commit()
                db.refresh(created)
                print(f"Admin user created with weak bootstrap password: {created.email} (id={created.id})")
            else:
                print(f"Admin user created: {created.email} (id={created.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
