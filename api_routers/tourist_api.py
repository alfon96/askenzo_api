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


tourist = APIRouter(tags=["Tourists"], prefix="/tourist")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_tourist(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    """
    The function `get_current_tourist` retrieves the current tourist user based on the provided token,
    checking its validity and role.
    
    \n**param** token: The `token` parameter is a string that represents the authentication token of the
    user. It is used to verify the user's identity and authorization
    **type** token: str
    \n**param** db: The `db` parameter is a dependency that represents the database connection. It is used to
    interact with the database and perform CRUD operations. The `get_db` function is responsible for
    creating and returning the database connection
    \n**return**: the `tourist_user` object if the user is a valid tourist and their state is active. If the
    user is not a tourist or their state is not active, it raises an HTTPException with the appropriate
    status code and detail message. If the token is incorrect, it also raises an HTTPException.
    """
    payload_token = log.is_jwt_valid(token=token)

    if payload_token:
        if payload_token["role"] == Authentication.roles[2]:
            tourist_id = payload_token["user_id"]
            db_tourist_user = crud.get_tourist_user(db, user_id=tourist_id)
            if db_tourist_user is None:
                raise HTTPException(status_code=404, detail="Tourist not found")
            tourist_user = schemas.TouristUser(
                id=db_tourist_user.id,
                name=db_tourist_user.name,
                surname=db_tourist_user.surname,
                password=db_tourist_user.password,
                telephone=db_tourist_user.telephone,
                email=db_tourist_user.email,
                img_profile=db_tourist_user.img_profile,
                state_id=db_tourist_user.state_id,
            )
            if db_tourist_user.state_id == 1:
                return tourist_user
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
@tourist.get("/", response_model=schemas.TouristUserResponse)
def get_my_data(    tourist_user: schemas.TouristUser = Depends(get_current_tourist)):
    """
    The function `get_my_data` returns the current tourist user.
    
    \n**param** tourist_user: The parameter `tourist_user` is of type `schemas.TouristUser` and is obtained
    by calling the `get_current_tourist` function as a dependency
    \n**type** tourist_user: schemas.TouristUser
    \n**return** a dictionary with a key "result" and the value being the tourist_user object.
    """

    return {"result": tourist_user}


# Checks if the input password is correct.
def verify_my_password(    input_password: str,    tourist_user: schemas.TouristUserCreate = Depends(get_current_tourist),):
    """
    The function `verify_my_password` is used to check if a given input password matches the hashed
    password stored for a tourist user.
    
    \n**param** input_password: The password that the user has entered and wants to verify
    **type** input_password: str
    \n**param** tourist_user: The `tourist_user` parameter is of type `schemas.TouristUserCreate` and is
    obtained by calling the `get_current_tourist` function. It represents the current tourist user for
    whom we want to verify the password
    **type** tourist_user: schemas.TouristUserCreate
    \n**return**: the result of the `encryption.check_password` function, which is a boolean value indicating
    whether the `input_password` matches the `hashed_password_string` stored in the `tourist_user`
    object.
    """
    return encryption.check_password(
        input_password=input_password, hashed_password_string=tourist_user.password
    )


# Update tourist password.
@tourist.patch("/update_password")
def update_my_password(    old_password: str,    new_password: str,    tourist_user: schemas.TouristUser = Depends(get_current_tourist),    db=Depends(get_db),):
    """
    The function `update_my_password` updates the password of a tourist user in the database if the old
    password is verified and the new password is not the same as the old one.
    
    \n**param** old_password: The old password that the user wants to update
    **type** old_password: str
    \n**param** new_password: The `new_password` parameter is a string that represents the new password that
    the user wants to set
    **type** new_password: str
    \n**param** tourist_user: The `tourist_user` parameter is of type `schemas.TouristUser` and is used to
    get the current tourist user from the database. It is obtained using the `get_current_tourist`
    dependency
    **type** tourist_user: schemas.TouristUser
    \n**param** db: The parameter "db" is a dependency that represents the database connection. It is used to
    interact with the database and perform CRUD (Create, Read, Update, Delete) operations. The "get_db"
    function is responsible for providing the database connection to the function
    \n**return**: a dictionary with the key "result" and the value being the result of the update operation
    in the database.
    """
    # Check if new password is the same as old one
    if old_password == new_password:
        return {"result": "Identical input passwords."}
    # Verify old password
    elif verify_my_password(input_password=old_password, tourist_user=tourist_user):
        new_password_encrypted = encryption.hash_password(new_password)

        db_tourist_user = crud.get_tourist_user(db, user_id=tourist_user.id)
        if db_tourist_user:
            # Update password
            db_tourist_user.password = new_password_encrypted
        else:
            raise HTTPException(status_code=404, detail="User not found on database")

        return {"result": crud.update(db, db_tourist_user)}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Password."
        )


# Updates every field at once, it doesn’t update new empty fields.
@tourist.patch("/")
def update_my_info(    new_name: str = "",    new_surname: str = "",    new_email: str = "",    new_img_profile: str = "",    new_state_id: int = Query(None, ge=1, le=2),    new_telephone: str = "",    tourist_user: schemas.TouristUser = Depends(get_current_tourist),    db: Session = Depends(get_db),):
    """
    The function `update_my_info` updates the information of a tourist user in a database based on the
    provided parameters.
    
    \n**param** new_name: The new name that you want to update for the tourist user
    **type** new_name: str
    \n**param** new_surname: The parameter `new_surname` is a string that represents the new surname of the
    tourist user
    **type** new_surname: str
    \n**param** new_email: The new email address that you want to update for the tourist user
    **type** new_email: str
    \n**param** new_img_profile: The parameter `new_img_profile` is a string that represents the new image
    profile for the tourist user. It is an optional parameter, which means it has a default value of an
    empty string. If a new image profile is provided, it will be assigned to the `db_tourist_user.img
    **type** new_img_profile: str
    \n**param** new_state_id: The parameter `new_state_id` is an optional integer parameter that represents
    the new state ID for the tourist user. It has a default value of `None` and is constrained to be
    greater than or equal to 1 and less than or equal to 2
    **type** new_state_id: int
    \n**param** new_telephone: The `new_telephone` parameter is used to update the telephone number of a
    tourist user. It is a string type parameter that represents the new telephone number that you want
    to update for the tourist user
    **type** new_telephone: str
    \n**param** tourist_user: The parameter `tourist_user` is of type `schemas.TouristUser` and is obtained
    using the `get_current_tourist` dependency. It represents the current tourist user making the
    request
    **type** tourist_user: schemas.TouristUser
    \n**param** db: The `db` parameter is of type `Session` and is used to interact with the database. It is
    obtained using the `get_db` dependency
    **type** db: Session
    \n**return**: a dictionary with the key "result" and the value being the result of the update operation
    performed by the `crud.update` function.
    """
    db_tourist_user = crud.get_tourist_user(db, user_id=tourist_user.id)
    if db_tourist_user:
        if new_name:
            db_tourist_user.name = new_name
        if new_surname:
            db_tourist_user.surname = new_surname
        if new_email:
            db_tourist_user.email = new_email
        if new_img_profile:
            db_tourist_user.img_profile = new_img_profile
        if new_state_id:
            db_tourist_user.state_id = new_state_id
        if new_telephone:
            db_tourist_user.telephone = new_telephone

        return {"result": crud.update(db, tourist_user=db_tourist_user)}
    else:
        raise HTTPException(status_code=404, detail="Tourist not found")


# Creates a new tourist.
@tourist.post("/signup")
def register_me(tourist_user: schemas.TouristUserCreate, db: Session = Depends(get_db)):
    """
    The function `register_me` creates a new tourist user in the database with the provided information,
    after validating the state_id.
    
    \n**param** tourist_user: The `tourist_user` parameter is an instance of the `TouristUserCreate` model
    from the `schemas` module. It contains the data needed to create a new tourist user
    **type** tourist_user: schemas.TouristUserCreate
    \n**param** db: The `db` parameter is a database session object. It is used to interact with the database
    and perform CRUD (Create, Read, Update, Delete) operations
    **type** db: Session
    \n**return**: a dictionary with a key "result" and the value is the result of calling the
    "create_tourist_user" function from the "crud" module with the "db" and "new_tourist_user"
    arguments.
    """
    if tourist_user.state_id < 0 or tourist_user.state_id > 2:
        raise HTTPException(status_code=400, detail="state_id must be either 1 or 2.")

    encrypted_password = encryption.hash_password(tourist_user.password)
    new_tourist_user = models.TouristUser(
        name=tourist_user.name,
        surname=tourist_user.surname,
        email=tourist_user.email,
        img_profile=tourist_user.img_profile,
        state_id=tourist_user.state_id,
        telephone=tourist_user.telephone,
        password=encrypted_password,
    )
    return {"result": crud.create_tourist_user(db=db, tourist_user=new_tourist_user)}


def authenticate_tourist(email: str, password: str, db):
    """
    The function `authenticate_tourist` takes an email, password, and database as input and checks if
    the tourist user exists and if the password matches the hashed password in the database.
    
    \n**param** email: The email parameter is a string that represents the email address of the tourist user
    trying to authenticate
    **type** email: str
    \n**param** password: The `password` parameter is a string that represents the password entered by the
    user during authentication
    **type** password: str
    \n**param** db: The `db` parameter is a database connection object or session that is used to interact
    with the database. It is typically passed to the function so that it can perform database operations
    such as querying for user data or updating user information
    \n**return**: the ID of the authenticated tourist if the email and password provided match the user's
    credentials in the database.
    """
    tourist = crud.get_tourist_user_by_email(email=email, db=db)
    if tourist:
        if encryption.check_password(
            input_password=password, hashed_password_string=tourist.password
        ):
            return tourist.id
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist-"
        )


@tourist.post("/signin", response_model=log.Token)
def signin(    email: str,    password: str,    db: Session = Depends(get_db),):
    """
    The `login` function takes an email and password as input, authenticates the user, and returns an
    access token if successful, otherwise raises an HTTPException.
    
    \n**param** email: The email parameter is a string that represents the user's email address
    **type** email: str
    \n**param** password: The `password` parameter is a string that represents the user's password. It is
    used to authenticate the user during the login process
    **type** password: str
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session. It is
    obtained using the `get_db` dependency
    **type** db: Session
    \n**return**: a dictionary with two keys: "access_token" and "token_type". The value of "access_token" is
    the token generated by the `log.create_jwt()` function, and the value of "token_type" is "bearer".
    """
    id = authenticate_tourist(email=email, password=password, db=db)
    if id:
        token = log.create_jwt(
            {
                "user_id": id,
                "role": Authentication.roles[2],
            }
        )
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Deletes the tourist by its id.
@tourist.delete("/")
def delete_my_account(    password: str,    db: Session = Depends(get_db),    tourist_to_remove: schemas.TouristUser = Depends(get_current_tourist),):
    """
    The function `delete_my_account` deletes a tourist user account from the database if the provided
    password is correct.
    
    \n**param** password: The `password` parameter is a string that represents the password provided by the
    user to verify their identity before deleting their account
    **type** password: str
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session. It is
    obtained using the `get_db` dependency
    **type** db: Session
    \n**param** tourist_to_remove: The parameter `tourist_to_remove` is of type `schemas.TouristUser` and is
    obtained by calling the `get_current_tourist` dependency. It represents the tourist user who wants
    to delete their account
    **type** tourist_to_remove: schemas.TouristUser
    \n**return**: a dictionary with a key "result" and the value is the result of calling the function
    `crud.delete_tourist()` with the argument `db_tourist_user` and `db`.
    """
    if verify_my_password(input_password=password, tourist_user=tourist_to_remove):
        db_tourist_user = crud.get_tourist_user(db, user_id=tourist_to_remove.id)
        return {"result": crud.delete_tourist(tourist_to_remove=db_tourist_user, db=db)}
    else:
        raise HTTPException(status_code=401, detail=f"Invalid password.")


# LIKES
# Get get all user's liked experiences by id.
@tourist.get("/likes_list", response_model=dict)
def get_my_likes_list(    db: Session = Depends(get_db),    me: schemas.TouristUser = Depends(get_current_tourist),):
    """
    The function `get_my_likes_list` retrieves a list of likes for a specific tourist user from a
    database.
    
    \n**param** db: The parameter `db` is of type `Session` and is used to access the database session
    **type** db: Session
    \n**param** me: The `me` parameter is of type `schemas.TouristUser` and is obtained by calling the
    `get_current_tourist` function. It represents the currently logged-in tourist user
    **type** me: schemas.TouristUser
    \n**return**: a dictionary with a single key-value pair. The key is "result" and the value is a list of
    indexes.
    """
    result = []
    user_tourist_likes = crud.get_likes(db, user_id=me.id)
    if user_tourist_likes:
        indexes = [row[0] for row in user_tourist_likes]
        result = indexes
    return {"result": result}


# Creates(deletes) a new(existing) like.
@tourist.post("/toggle_like")
def toggle_like(    experience_id: int,    db: Session = Depends(get_db),    me: schemas.TouristUser = Depends(get_current_tourist),):
    """
    The function `toggle_like` toggles the like status of an experience for a tourist user.
    
    \n**param** experience_id: The `experience_id` parameter is an integer that represents the ID of the
    experience that the user wants to toggle the like status for
    **type** experience_id: int
    \n**param** db: The `db` parameter is of type `Session` and is used to interact with the database. It is
    obtained using the `get_db` dependency
    **type** db: Session
    \n**param** me: The "me" parameter is of type "schemas.TouristUser" and represents the currently
    authenticated tourist user. It is obtained using the "Depends(get_current_tourist)" dependency,
    which is responsible for retrieving the authenticated user from the request
    **type** me: schemas.TouristUser
    """
    is_experience_existing = crud.get_experience(db=db, experience_id=experience_id)
    if is_experience_existing:
        already_liked = crud.get_like(db=db, user_id=me.id, experience_id=experience_id)
        if already_liked:
            if crud.delete_like(db=db, like_to_remove=already_liked):
                return {"result": False}
        else:
            new_like = models.TouristUserLikes(
                tourist_user_id=me.id,
                experience_id=experience_id,
            )
            if crud.create_like(db=db, new_like=new_like):
                return {"result": True}
    else:
        raise HTTPException(status_code=404, detail=f"Experience not found.")