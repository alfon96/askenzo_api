from fastapi import Depends, HTTPException, APIRouter, Query, status
from sqlalchemy.orm import Session
import models
from database import SessionLocal
import schemas, crud
from typing import Union
from database import get_db
import api_routers.admin_api as log
from fastapi.security import OAuth2PasswordBearer
import utility.authentication_data as auth
import re

popup = APIRouter(tags=["PopupMsg"], prefix="/popup")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="discovery/login")


@popup.get("/", response_model=schemas.SinglePopupResponse)
def get_msg(    id: int,    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_tourist_host_admin_priviledge),):
    """
    The function `get_msg` retrieves a single popup message from the database based on its ID and
    returns it as a result, or raises an HTTPException with a 404 status code if no popup messages are
    found.
    
    \n**param** id: The `id` parameter is an integer that represents the ID of the popup message that we want
    to retrieve from the database
    **type** id: int
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database. It is
    obtained using the `get_db` function
    **type** db: Session
    \n**param** _: The parameter "_" is used to indicate that the value is not going to be used in the
    function. It is commonly used when a dependency is required but its value is not needed in the
    function body. In this case, it is used to indicate that the value of "schemas.HostUser" is not
    **type** _: schemas.HostUser
    \n**return**: a dictionary with the key "result" and the value being the popup message retrieved from the
    database.
    """
    popup = crud.get_single_popup(db=db, popup_id=id)

    if popup:
        return {"result": popup}
    else:
        raise HTTPException(status_code=404, detail="No popup messages found.")


@popup.get("/", response_model=schemas.PopupResponse)
def get_msgs(    cursor: Union[int, None] = Query(None, ge=0),    limit: int = Query(20, gt=0),    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_tourist_host_admin_priviledge),):
    """
    The function `get_msgs` retrieves popup messages from a database and returns them in a paginated
    response.
    
    \n**param** cursor: The `cursor` parameter is used to specify the starting point for retrieving popup
    messages. It is an optional parameter and can be an integer value or `None`. If a cursor value is
    provided, the function will retrieve popup messages starting from that cursor value. If `None` is
    provided, the function
    **type** cursor: Union[int, None]
    \n**param** limit: The `limit` parameter specifies the maximum number of popup messages to retrieve. By
    default, it is set to 20, but you can provide a different value if needed
    **type** limit: int
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session. It is
    passed as a dependency using the `Depends` function
    **type** db: Session
    \n**param** _: The parameter "_" is of type "schemas.HostUser" and is used to authenticate the user and
    check if they have the necessary privileges (tourist, host, or admin) to access the function
    **type** _: schemas.HostUser
    \n**return**: The function `get_msgs` returns a `schemas.PopupResponse` object.
    """
    popups = crud.get_popup_msg(db=db, cursor=cursor, limit=limit)

    if popups:
        has_more = len(popups) > limit
        popups = popups[:limit]

        return schemas.PopupResponse(
            cursor=popups[-1].id if popups else None,
            has_more=has_more,
            items=[
                schemas.PopupMsg(
                    id=popup.id,
                    text=popup.text,
                )
                for popup in popups
            ],
        )
    else:
        raise HTTPException(status_code=404, detail="No popup messages found.")


@popup.post("/")
def create(    popup: schemas.PopupMsgBase,    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_admin_priviledge),):
    """
    The `create` function creates a new popup message in the database.
    
    \n**param** popup: The `popup` parameter is of type `schemas.PopupMsgBase` and represents the data for
    creating a new popup message
    **type** popup: schemas.PopupMsgBase
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session
    **type** db: Session
    \n**param** _: The underscore (_) is used as a variable name to indicate that the value is not going to
    be used in the function. In this case, it is used as a placeholder for the HostUser object returned
    by the auth.get_admin_privilege function
    **type** _: schemas.HostUser
    \n**return**: a dictionary with a key "result" and a value of True if the popup message is successfully
    created in the database. If the popup message is not found, it raises an HTTPException with a status
    code of 404 and a detail message of "No popup messages found."
    """
    if crud.create_popup_msg(db=db, popup=models.PopupMsg(text=popup.text)):
        return {"result": True}
    else:
        raise HTTPException(status_code=404, detail="No popup messages found.")


@popup.patch("/")
def update(    popup_id: int,    popup: schemas.PopupMsgBase,    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_admin_priviledge),):
    """
    The `update` function updates a popup message in the database if it exists, otherwise it raises a
    404 error.
    
    \n**param** popup_id: The `popup_id` parameter is an integer that represents the unique identifier of the
    popup message that needs to be updated
    **type** popup_id: int
    \n**param** popup: The `popup` parameter is of type `schemas.PopupMsgBase` and represents the updated
    popup message data that will be used to update the existing popup message
    **type** popup: schemas.PopupMsgBase
    \n**param** db: The `db` parameter is a database session object. It is used to interact with the database
    and perform CRUD (Create, Read, Update, Delete) operations
    **type** db: Session
    \n**param** _: The underscore (_) parameter is used to indicate that the dependency is not being used in
    the function. In this case, it is used to indicate that the schemas.HostUser dependency is not being
    used in the function
    **type** _: schemas.HostUser
    \n**return**: a dictionary with the key "result" and the value being the result of the `crud.update(db)`
    function.
    """
    old_popup = crud.get_single_popup(db=db, popup_id=popup_id)

    if old_popup:
        if popup.text != old_popup.text:
            old_popup.text = popup.text
            return {"result": crud.update(db)}
    else:
        raise HTTPException(status_code=404, detail="Popup message not found")


@popup.delete("/")
def delete(    popup_id: int,    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_admin_priviledge),):
    """
    The function `delete` deletes a popup message from the database if it exists, otherwise it raises a
    404 error.
    
    \n**param** popup_id: The `popup_id` parameter is an integer that represents the unique identifier of the
    popup message that needs to be deleted
    **type** popup_id: int
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session for
    performing CRUD operations
    **type** db: Session
    \n**param** _: The underscore (_) is used as a variable name to indicate that the value is not going to
    be used in the function. In this case, it is used to indicate that the schemas.HostUser object
    returned by the auth.get_admin_privilege function is not going to be used in the delete function
    **type** _: schemas.HostUser
    \n**return**: a dictionary with a key "result" and the value is the result of calling the function
    `crud.delete_popup_msg()` with the arguments `db=db` and `popup_to_delete=popup_to_delete`.
    """
    popup_to_delete = crud.get_single_popup(db=db, popup_id=popup_id)

    if popup_to_delete:
        return {"result": crud.delete_popup_msg(db=db, popup_to_delete=popup_to_delete)}
    else:
        raise HTTPException(status_code=404, detail="No popup messages found.")
