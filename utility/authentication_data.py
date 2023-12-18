from fastapi import Depends, HTTPException, status
import api_routers.admin_api as log
from fastapi.security import OAuth2PasswordBearer
import crud
from decouple import config



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login_admin")


class Authentication:
    username = config("username")
    password = config("password")
    secret_key = config("secret_key")
    roles = ["Admin", "Host", "Tourist"]
    expiration_days = 7


def get_tourist_host_priviledge(token: str = Depends(oauth2_scheme)):
    payload_token = log.is_jwt_valid(token=token)

    if payload_token:
        if (
            payload_token["role"] == Authentication.roles[1]
            or payload_token["role"] == Authentication.roles[2]
        ):
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized user.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_admin_priviledge(token: str = Depends(oauth2_scheme)):
    payload_token = log.is_jwt_valid(token=token)

    if payload_token:
        if payload_token["role"] == Authentication.roles[0]:
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized user.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_tourist_host_admin_priviledge(token: str = Depends(oauth2_scheme)) -> bool:
    payload_token = log.is_jwt_valid(token=token)

    if payload_token:
        if (
            payload_token["role"] == Authentication.roles[0]
            or payload_token["role"] == Authentication.roles[1]
            or payload_token["role"] == Authentication.roles[2]
        ):
            return payload_token["role"]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized user.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Bearer"},
        )
