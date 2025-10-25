from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.utils.token_generation import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/user/login')


def get_user_info(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


        uid: str = payload.get("sub")
        fcm_token: str = payload.get("fcmToken")

        if uid is None or fcm_token is None:
            raise credentials_exception

    except JWTError:

        raise credentials_exception

    return {"uid": uid, "fcm_token": fcm_token}