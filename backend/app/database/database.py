from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select

from ..core.config import settings

engine = create_engine(settings.database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    create_default_admin()
    
def create_default_admin():
    # Import here to avoid circular imports
    from app.models.user import Role, User
    from app.services.auth import hash_password
    with Session(engine) as session:
        # Check if any admin user already exists
        statement = select(User).where(User.role == Role.ADMIN)
        existing_admin = session.exec(statement).first()
        
        if not existing_admin:
            # Create default admin
            admin_password = "admin@123"  # Fallback password
            admin = User(
                username="admin",
                full_name="System Administrator",
                email=settings.admin_email or "admin@example.com",
                hashed_password=hash_password(admin_password),
                role=Role.ADMIN,
                is_active=True
            )
            
            session.add(admin)
            try:
                session.commit()
            except Exception as e:
                session.rollback()

def get_session() -> Session:
    return Session(engine)

## Session dependency for FastAPI routes
SessionDep = Annotated[Session, Depends(get_session)]
