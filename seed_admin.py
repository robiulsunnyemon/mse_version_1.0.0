import os
from sqlalchemy.orm import Session
from app.db.db import Session as DBSession
from app.auth.model.auth_user import AuthUserModel
from app.utils.get_hashed_password import get_hashed_password

def seed_admin():
    db: Session = DBSession()
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin1234")
        admin_first_name = os.getenv("ADMIN_FIRST_NAME", "Admin")

        # Check if admin already exists
        existing_admin = db.query(AuthUserModel).filter(AuthUserModel.email == admin_email).first()
        if existing_admin:
            print(f"Admin with email {admin_email} already exists.")
            # Ensure role is admin and verified
            if existing_admin.role != "admin" or not existing_admin.is_verified:
                existing_admin.role = "admin"
                existing_admin.is_verified = True
                db.commit()
                print("Updated existing user to be a verified admin.")
            return

        # Create new admin
        hashed_password = get_hashed_password(admin_password)
        new_admin = AuthUserModel(
            first_name=admin_first_name,
            email=admin_email,
            password=hashed_password,
            is_verified=True,
            role="admin",
            auth_provider="email"
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print(f"Admin seeded successfully with email: {admin_email}")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
