from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.dependencies import get_db
from api.schemas.auth import LoginRequest, TokenResponse
from api.services.auth_service import authenticate_user


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    token = authenticate_user(
        db=db,
        email=login_data.email,
        password=login_data.password,
    )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }