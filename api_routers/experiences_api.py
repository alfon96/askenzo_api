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

experience = APIRouter(tags=["Experiences"], prefix="/experiences")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login_admin")


@experience.get("/", response_model=schemas.SingleExperienceResponse)
def get_experience(    id: int = Query(..., gt=0),    db: Session = Depends(get_db),    _: bool = Depends(auth.get_tourist_host_admin_priviledge),):
    """
    The function `get_experience` retrieves an experience from the database based on the provided ID and
    returns it as a response.
    
    \n**param** id: The `id` parameter is an integer that represents the unique identifier of the experience
    that we want to retrieve. It is a required parameter and must be greater than 0
    **type** id: int
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database. It is
    obtained using the `get_db` dependency, which is responsible for creating a new database session for
    each request
    **type** db: Session
    \n**param** _: The underscore (_) parameter is used to indicate that we are not using the value of this
    parameter in our function. It is a convention to use underscore (_) as a variable name when we don't
    need to use the value of a parameter. In this case, the parameter is used to enforce the dependency
    on
    **type** _: bool
    \n**return**: The code is returning a dictionary with a key "result" and a value of an instance of the
    Experience model.
    """
    experience = crud.get_experience(db=db, experience_id=id)

    # In this code, we fetch one more item than requested (limit+1).
    # If we get this extra item, we know that there are more items to fetch,
    # so we set has_more to true. Otherwise, we set has_more to false
    if experience:
        instance = schemas.Experience(
            id=id,
            title=experience.title,
            description=experience.description,
            difficulty_id=experience.difficulty_id,
            duration=experience.duration,
            img_paths=experience.img_paths,
            img_preview_path=experience.img_preview_path,
            price=experience.price,
            state_id=experience.state_id,
        )
        return {"result": instance}
    else:
        raise HTTPException(status_code=404, detail="Experience not found.")


# Get a list of N experiences, from x to y.
@experience.get("/", response_model=schemas.ExperienceResponse)
def get_experiences(    cursor: Union[int, None] = Query(None, ge=0),    limit: int = Query(20, gt=0),    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_tourist_host_admin_priviledge),):
    """
    The function `get_experiences` retrieves a list of experiences from a database, with pagination
    support.
    
    \n**param** cursor: The `cursor` parameter is used for pagination. It represents the starting point or
    the last item ID from which the experiences should be fetched. If a cursor value is provided, only
    experiences with an ID greater than or equal to the cursor value will be returned
    **type** cursor: Union[int, None]
    \n**param** limit: The `limit` parameter is used to specify the maximum number of experiences to retrieve
    from the database. By default, it is set to 20, but it can be overridden by passing a different
    value when calling the `get_experiences` function
    **type** limit: int
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session. It is
    obtained using the `get_db` dependency
    **type** db: Session
    \n**param** _: The underscore (_) parameter is used to indicate that we are not using the value of that
    parameter. In this case, it is used to indicate that we are not using the value of the
    schemas.HostUser parameter in the function
    **type** _: schemas.HostUser
    \n**return**: The function `get_experiences` returns an instance of the `ExperienceResponse` class from
    the `schemas` module. This instance contains the following attributes:
    """
    experiences = crud.get_experiences(db=db, cursor=cursor, limit=limit)

    # In this code, we fetch one more item than requested (limit+1).
    # If we get this extra item, we know that there are more items to fetch,
    # so we set has_more to true. Otherwise, we set has_more to false
    if experiences:
        has_more = len(experiences) > limit
        experiences = experiences[:limit]

        return schemas.ExperienceResponse(
            cursor=experiences[-1].id if experiences else None,
            has_more=has_more,
            items=[schemas.Experience.from_orm(exp) for exp in experiences],
        )
    else:
        raise HTTPException(status_code=404, detail="No experiences found.")


# Update every field at once, it doesn’t update new empty fields.
@experience.patch("/update")
def update(    experience_id: int,    experience_data: schemas.ExperienceBase,    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_admin_priviledge),):
    """
    The function `update` updates the fields of an experience object in the database based on the
    provided experience data.
    
    \n**param** experience_id: The ID of the experience that needs to be updated
    **type** experience_id: int
    \n**param** experience_data: The `experience_data` parameter is an instance of the `ExperienceBase`
    schema. It contains the updated data for an experience, including the title, description, difficulty
    ID, price, image preview path, image paths, duration, and state ID
    **type** experience_data: schemas.ExperienceBase
    \n**param** db: The `db` parameter is an instance of the `Session` class, which represents a connection
    to the database. It is used to perform database operations such as querying and updating data
    **type** db: Session
    \n**param** _: The underscore (_) parameter is used to indicate that the dependency is required but its
    value is not used in the function. In this case, it is used to enforce the requirement that the user
    must have admin privileges in order to access this endpoint
    **type** _: schemas.HostUser
    \n**return**: a dictionary with the key "result" and the value being the result of the `crud.update(db)`
    function.
    """
    experience = crud.get_experience(db, experience_id)
    if experience:
        if experience_data.title:
            experience.title = experience_data.title
        if experience_data.description:
            experience.description = experience_data.description
        if experience_data.difficulty_id:
            experience.difficulty_id = experience_data.difficulty_id
        if experience_data.price:
            experience.price = experience_data.price
        if experience_data.img_preview_path:
            experience.img_preview_path = experience_data.img_preview_path
        if experience_data.img_paths:
            experience.img_paths = experience_data.img_paths
        if experience_data.duration:
            experience.duration = experience_data.duration
        if experience_data.state_id:
            experience.state_id = experience_data.state_id

        return {"result": crud.update(db)}
    else:
        raise HTTPException(status_code=404, detail="Experience not found")


# Creates a new experience.
@experience.post("/new")
def create(    experience: schemas.ExperienceBase,    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_admin_priviledge),):
    """
    The function creates a new experience in the database with the provided information.
    
    \n**param** experience: The `experience` parameter is of type `schemas.ExperienceBase`, which is a
    Pydantic model representing the data required to create a new experience. It contains the following
    attributes:
    **type** experience: schemas.ExperienceBase
    \n**param** db: The `db` parameter is a database session object. It is used to interact with the database
    and perform CRUD operations
    **type** db: Session
    \n**param** _: The underscore (_) in the function signature is used as a variable name to indicate that
    the value is not going to be used in the function. It is a convention to use underscore (_) as a
    variable name when the value is not needed or not important in the context of the function
    **type** _: schemas.HostUser
    \n**return**: a dictionary with a key "result" and the value is the result of calling the function
    `crud.create_experience` with the arguments `db=db` and `new_experience=new_experience`.
    """
    if experience.state_id < 0 or experience.state_id > 2:
        raise HTTPException(status_code=400, detail="state_id must be either 1 or 2.")

    new_experience = models.Experiences(
        title=experience.title,
        description=experience.description,
        difficulty_id=experience.difficulty_id,
        price=experience.price,
        duration=experience.duration,
        img_preview_path=experience.img_preview_path,
        img_paths=experience.img_paths,
        state_id=experience.state_id,
    )
    return {"result": crud.create_experience(db=db, new_experience=new_experience)}


# Deletes the experience by its id.
@experience.delete("/delete")
def delete(    experience_id: int,    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_admin_priviledge),):
    """
    The `delete` function deletes an experience from the database based on the provided experience ID.
    
    \n**param** experience_id: The ID of the experience that needs to be deleted
    **type** experience_id: int
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session
    **type** db: Session
    \n**param** _: The underscore (_) parameter is used to indicate that the dependency is required but its
    value is not going to be used in the function. In this case, it is used to indicate that the admin
    privilege is required for this function, but the actual value of the admin user is not needed in the
    function body
    **type** _: schemas.HostUser
    \n**return**: a dictionary with a key "result" and the value is the result of calling the
    `crud.delete_experience` function with the `experience_to_remove` and `db` as arguments.
    """
    experience_to_remove = crud.get_experience(db=db, experience_id=experience_id)
    if experience_to_remove:
        return {
            "result": crud.delete_experience(
                experience_to_remove=experience_to_remove, db=db
            )
        }
    else:
        raise HTTPException(
            status_code=404, detail=f"No experience found with id: {experience_id}"
        )
