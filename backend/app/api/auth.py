
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import User
from app.schemas.user import UserCreate, UserRead
from app.core.security import hash_password


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    # 1. Check whether email already exists
    statement = select(User).where(
        User.email == payload.email
    )

    existing_user = db.scalar(statement)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # 2. Hash the password
    hashed_password = hash_password(payload.password)

    # 3. Create the user object
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hashed_password
    )

    # 4. Save user in database
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        ) from None

    # 5. Refresh to retrieve generated database fields
    db.refresh(user)

    return user
