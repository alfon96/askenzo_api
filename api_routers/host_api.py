from fastapi import Depends, HTTPException, APIRouter, Query
from sqlalchemy.orm import Session
import models
from database import get_db
import schemas, crud
import api_routers.admin_api as log
from utility.authentication_data import Authentication
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from utility import encryption

host = APIRouter(tags=["Hosts"], prefix="/host")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_host(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    """
    The function `get_current_host` retrieves the current host user based on the provided token and
    checks if the user is authorized and active.
    
    \n**param** token: The `token` parameter is a string that represents the authentication token provided by
    the client. It is used to authenticate and authorize the user making the request
    **type** token: str
    \n**param** db: The `db` parameter is a dependency that represents the database connection. It is used to
    interact with the database and perform CRUD operations. The `get_db` function is responsible for
    creating and returning the database connection
    \n**return**: The function `get_current_host` returns an instance of `schemas.HostUser` if the user is a
    valid host and their state is active. If the user is not a valid host or their state is not active,
    it raises an HTTPException with the appropriate status code and detail message.
    """
    payload_token = log.is_jwt_valid(token=token)

    if payload_token:
        if payload_token["role"] == Authentication.roles[1]:
            host_id = payload_token["user_id"]
            db_host_user = crud.get_host_user(db, user_id=host_id)
            if db_host_user is None:
                raise HTTPException(status_code=404, detail="Host not found")
            host_user = schemas.HostUser(
                id=db_host_user.id,
                name=db_host_user.name,
                password=db_host_user.password,
                email=db_host_user.email,
                img_profile=db_host_user.img_profile,
                state_id=db_host_user.state_id,
            )
            if host_user.state_id == 1:
                return host_user
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This user has been deactivated.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
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


# Get the single user instance, with all its fields (no password).
@host.get("/", response_model=schemas.HostUserResponse)
def get_my_data(    host_user: schemas.HostUser = Depends(get_current_host),):
    """
    The function `get_my_data` returns a dictionary with the result being the `host_user` object.
    
    \n**param** host_user: The parameter `host_user` is of type `schemas.HostUser` and is obtained by calling
    the function `get_current_host` as a dependency
    **type** host_user: schemas.HostUser
    \n**return**: a dictionary with a key "result" and the value being the host_user object.
    """
    return {"result": host_user}


# Checks if the input password is correct.
def verify_my_password(    input_password: str,    host_user: schemas.HostUserCreate = Depends(get_current_host),):
    """
    The function `verify_my_password` is used to check if a given input password matches the hashed
    password stored for a host user.
    
    \n**param** input_password: The password that the user wants to verify
    **type** input_password: str
    \n**param** host_user: The `host_user` parameter is of type `schemas.HostUserCreate` and is obtained by
    calling the `get_current_host` function. It represents the host user for whom we want to verify the
    password
    **type** host_user: schemas.HostUserCreate
    \n**return**: the result of the `encryption.check_password` function, which is a boolean value indicating
    whether the `input_password` matches the `hashed_password_string` stored in the `host_user` object.
    """
    return encryption.check_password(
        input_password=input_password, hashed_password_string=host_user.password
    )


# Update host password.
@host.patch("/update_password")
def update_my_password(    old_password: str,    new_password: str,    host_user: schemas.HostUser = Depends(get_current_host),    db=Depends(get_db),):
    """
    The function `update_my_password` updates the password of a host user in a database if the old
    password is verified and the new password is different from the old one.
    
    \n**param** old_password: The old password that the user wants to update
    **type** old_password: str
    \n**param** new_password: The new password that the user wants to set
    **type** new_password: str
    \n**param** host_user: The `host_user` parameter is of type `schemas.HostUser` and is obtained by calling
    the `get_current_host` function. It represents the current host user who wants to update their
    password
    **type** host_user: schemas.HostUser
    \n**param** db: The `db` parameter is a dependency that represents the database connection. It is
    obtained using the `get_db` function, which is likely defined elsewhere in the code. This parameter
    allows the function to interact with the database to perform operations such as retrieving and
    updating user information
    \n**return**: a dictionary with the key "result" and the value being the result of the `crud.update`
    function.
    """
    # Check if new password is the same as old one
    if old_password == new_password:
        raise HTTPException(status_code=400, detail="Identical input passwords.")
    # Verify old password
    elif verify_my_password(input_password=old_password, host_user=host_user):
        new_password_encrypted = encryption.hash_password(new_password)

        db_host_user = crud.get_host_user(db, user_id=host_user.id)
        if db_host_user:
            # Update password
            db_host_user.password = new_password_encrypted
        else:
            raise HTTPException(status_code=404, detail="User not found on database")

        return {"result": crud.update(db, db_host_user)}
    else:
        raise HTTPException(status_code=401, detail="Invalid Password.")


# Updates every field at once, it doesn’t update new empty fields.
@host.patch("/")
def update_my_info(    new_name: str = "",    new_surname: str = "",    new_email: str = "",    new_img_profile: str = "",    new_state_id: int = Query(None, ge=1, le=2),    new_telephone: str = "",    host_user: schemas.HostUser = Depends(get_current_host),    db: Session = Depends(get_db),):
    """
    The function `update_my_info` updates the information of a host user in a database based on the
    provided parameters.
    
    \n**param** new_name: The new name that you want to update for the host user
    **type** new_name: str
    \n**param** new_surname: The parameter `new_surname` is a string that represents the new surname or last
    name that the user wants to update in their profile
    **type** new_surname: str
    \n**param** new_email: The new email address that you want to update for the host user
    **type** new_email: str
    \n**param** new_img_profile: The parameter `new_img_profile` is used to update the profile image of the
    host user. It accepts a string value representing the new image URL or file path
    **type** new_img_profile: str
    \n**param** new_state_id: The parameter `new_state_id` is an optional integer parameter that represents
    the new state ID for the host user. It has a default value of `None` and is constrained to be
    greater than or equal to 1 and less than or equal to 2
    **type** new_state_id: int
    \n**param** new_telephone: The `new_telephone` parameter is used to update the telephone number of the
    host user
    **type** new_telephone: str
    \n**param** host_user: The `host_user` parameter is of type `schemas.HostUser` and is obtained using the
    `get_current_host` dependency. It represents the current host user for whom the information is being
    updated
    **type** host_user: schemas.HostUser
    \n**param** db: The parameter `db` is of type `Session` and is used to access the database session. It is
    passed as a dependency to the function `get_db` which is used to create a new database session for
    each request
    **type** db: Session
    \n**return**: a dictionary with the key "result" and the value being the result of calling the `update`
    function from the `crud` module with the `db_host_user` object as the `host_user` argument.
    """
    db_host_user = crud.get_host_user(db, user_id=host_user.id)
    if db_host_user:
        if new_name:
            db_host_user.name = new_name
        if new_surname:
            db_host_user.surname = new_surname
        if new_email:
            db_host_user.email = new_email
        if new_img_profile:
            db_host_user.img_profile = new_img_profile
        if new_state_id:
            db_host_user.state_id = new_state_id
        if new_telephone:
            db_host_user.telephone = new_telephone

        return {"result": crud.update(db, host_user=db_host_user)}
    else:
        raise HTTPException(status_code=404, detail="Host not found")


# Creates a new host.
@host.post("/signup")
def register_me(host_user: schemas.HostUserCreate, db: Session = Depends(get_db)):
    """
    The function `register_me` registers a new host user by creating a new `HostUser` object with the
    provided information and storing it in the database.
    
    \n**param** host_user: The `host_user` parameter is of type `schemas.HostUserCreate`, which is a Pydantic
    model representing the data required to create a new host user. It contains the following fields:
    **type** host_user: schemas.HostUserCreate
    \n**param** db: The `db` parameter is of type `Session` and is used to interact with the database. It is
    obtained using the `get_db` function, which is a dependency that provides a database session
    **type** db: Session
    \n**return**: a dictionary with a key "result" and the value is the result of calling the
    `create_host_user` function from the `crud` module with the provided `db` and `new_host_user`
    arguments.
    """
    if host_user.state_id < 0 or host_user.state_id > 2:
        raise HTTPException(status_code=400, detail="state_id must be either 1 or 2.")

    encrypted_password = encryption.hash_password(host_user.password)
    new_host_user = models.HostUser(
        name=host_user.name,
        email=host_user.email,
        img_profile=host_user.img_profile,
        state_id=host_user.state_id,
        password=encrypted_password,
    )
    return {"result": crud.create_host_user(db=db, host_user=new_host_user)}


def authenticate_host(email: str, password: str, db):
    """
    The function `authenticate_host` takes an email, password, and database as input, retrieves a host
    user from the database using the email, checks if the password matches the hashed password stored in
    the database, and returns the host's ID if authentication is successful.
    
    \n**param** email: The email parameter is a string that represents the email address of the host user
    trying to authenticate
    **type** email: str
    \n**param** password: The `password` parameter is a string that represents the password entered by the
    user during authentication
    **type** password: str
    \n**param** db: The `db` parameter is a database connection object or session that is used to interact
    with the database. It is typically passed to the function so that it can perform database operations
    such as querying the user table to retrieve the host user with the given email
    \n**return**: the ID of the host user if the email and password provided match the user's credentials.
    """
    host = crud.get_host_user_by_email(email=email, db=db)
    if host:
        if encryption.check_password(
            input_password=password, hashed_password_string=host.password
        ):
            return host.id
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist-"
        )


@host.post("/signin", response_model=log.Token)
def signin(email: str, password: str, db: Session = Depends(get_db)):
    """
    The `login` function takes an email and password as input, authenticates the user, and returns an
    access token if the authentication is successful.
    
    \n**param** email: The `email` parameter is a string that represents the user's email address. It is used
    to identify the user during the login process
    **type** email: str
    \n**param** password: The `password` parameter is a string that represents the user's password
    **type** password: str
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session. It is
    obtained using the `get_db` dependency, which is likely a function that returns a database session.
    The session is then passed to the `authenticate_host` function to authenticate the user
    **type** db: Session
    \n**return**: a dictionary with two keys: "access_token" and "token_type". The value of "access_token" is
    the token generated by the `log.create_jwt()` function, and the value of "token_type" is "bearer".
    """
    id = authenticate_host(email=email, password=password, db=db)
    if id:
        token = log.create_jwt(
            {
                "user_id": id,
                "role": Authentication.roles[1],
            }
        )
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Deletes the host by its id.
@host.delete("/")
def delete_my_account(    password: str,    db: Session = Depends(get_db),    host_to_remove: schemas.HostUser = Depends(get_current_host),):
    """
    The function `delete_my_account` deletes the host user account if the provided password matches the
    password of the host user.
    
    \n**param** password: The `password` parameter is a string that represents the password provided by the
    user to verify their identity before deleting their account
    **type** password: str
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session
    **type** db: Session
    \n**param** host_to_remove: The `host_to_remove` parameter is of type `schemas.HostUser` and is obtained
    by calling the `get_current_host` dependency. It represents the host user that wants to delete their
    account
    **type** host_to_remove: schemas.HostUser
    \n**return**: If the password verification is successful, the function will return a dictionary with the
    key "result" and the value being the result of the `crud.delete_host()` function.
    """
    if verify_my_password(input_password=password, host_user=host_to_remove):
        db_host_user = crud.get_host_user(db, user_id=host_to_remove.id)
        return {"result": crud.delete_host(host_to_remove=db_host_user, db=db)}
    else:
        raise HTTPException(status_code=401, detail=f"Invalid password.")
