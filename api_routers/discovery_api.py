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

discovery = APIRouter(tags=["Discoveries"], prefix="/discoveries")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="discovery/login")


def extract_coordinates(point_str):
    """
    The function `extract_coordinates` takes a string representing a point and returns the coordinates
    of the point.
    
    \n**param** point_str: The parameter `point_str` is a string that represents a point in the format "(x,
    y)"
    \n**return**: The function `extract_coordinates` returns the coordinates extracted from the input
    `point_str` as a string.
    """
    match = re.search(r"\(([^)]+)\)", point_str)
    if match:
        return match.group(1)
    else:
        return ""


@discovery.get("/", response_model=schemas.SingleDiscoveryResponse)
def get_discovery(    id: int = Query(..., gt=0),    db: Session = Depends(get_db),    _: bool = Depends(auth.get_tourist_host_admin_priviledge),):
    """
    The function `get_discovery` retrieves a discovery item from the database and returns it as a
    response.
    
    \n**param** id: The `id` parameter is an integer that represents the ID of the discovery that we want to
    fetch. It is a required parameter and must be greater than 0
    **type** id: int
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session. It is
    passed as a dependency using the `Depends` function and the `get_db` function is used to get the
    actual database session
    **type** db: Session
    \n**param** _: The underscore (_) parameter is used to indicate that the dependency is required but its
    value is not used in the function. In this case, it is used to enforce the authentication and
    authorization check for the tourist host admin privilege
    **type** _: bool
    \n**return**: The code is returning a dictionary with a key "result" and the value being an instance of
    the schemas.Discovery class.
    """
    discovery = crud.get_discovery(db=db, discovery_id=id)

    # In this code, we fetch one more item than requested (limit+1).
    # If we get this extra item, we know that there are more items to fetch,
    # so we set has_more to true. Otherwise, we set has_more to false
    if discovery:
        instance = schemas.Discovery(
            address=discovery.address,
            coordinate_gps=extract_coordinates(
                schemas.ewkb_to_wkt(discovery.coordinate_gps)
            ),
            description=discovery.description,
            id=discovery.id,
            img_paths=discovery.img_paths,
            img_preview_path=discovery.img_preview_path,
            kind_id=discovery.kind_id,
            state_id=discovery.state_id,
            title=discovery.title,
            video_paths=discovery.video_paths,
        )
        return {"result": instance}
    else:
        raise HTTPException(status_code=404, detail="Experience not found.")


# Get a list of N discoverys, from x to y.
@discovery.get("/", response_model=schemas.DiscoveryResponse)
def get_discoveries(    cursor: Union[int, None] = Query(None, ge=0),    limit: int = Query(20, gt=0),    category: int = Query(1, ge=1, le=4),    all: bool = True,    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_tourist_host_admin_priviledge),):
    """
    The function `get_discoveries` retrieves a list of discoveries from a database based on specified
    parameters and returns them in a standardized format.
    
    \n**param** cursor: The `cursor` parameter is used to specify the starting point for fetching
    discoveries. It is an optional parameter and can be an integer value or `None`. If provided, it
    should be greater than or equal to 0
    **type** cursor: Union[int, None]
    \n**param** limit: The `limit` parameter specifies the maximum number of discoveries to retrieve. The
    default value is 20, but it can be overridden by passing a different value when calling the function
    **type** limit: int
    \n**param** category: The `category` parameter is an integer that represents the category of discoveries
    to fetch. It has a default value of 1 and must be between 1 and 4 (inclusive)
    **type** category: int
    \n**param** all: The `all` parameter is a boolean flag that determines whether to fetch all discoveries
    or only a subset of them. If `all` is set to `True`, all discoveries will be fetched. If `all` is
    set to `False`, only a subset of discoveries will be fetched based on the, defaults to True
    **type** all: bool (optional)
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session. It is
    obtained using the `get_db` dependency
    **type** db: Session
    \n**param** _: The underscore (_) parameter is used to indicate that we are not using the value of that
    parameter. It is commonly used when we need to include a dependency in the function signature but we
    don't actually need to use the value of that dependency in the function body. In this case, the
    underscore (_) parameter
    **type** _: schemas.HostUser
    \n**return**: a `schemas.DiscoveryResponse` object. This object contains the following attributes:
    """
    discoveries = crud.get_discoveries(
        db=db, cursor=cursor, limit=limit, category=category, all=all
    )

    # In this code, we fetch one more item than requested (limit+1).
    # If we get this extra item, we know that there are more items to fetch,
    # so we set has_more to true. Otherwise, we set has_more to false
    if discoveries:
        has_more = len(discoveries) > limit
        discoveries = discoveries[:limit]

        return schemas.DiscoveryResponse(
            cursor=discoveries[-1].id if discoveries else None,
            has_more=has_more,
            items=[
                schemas.Discovery(
                    address=discovery.address,
                    coordinate_gps=extract_coordinates(
                        schemas.ewkb_to_wkt(discovery.coordinate_gps)
                    ),
                    description=discovery.description,
                    id=discovery.id,
                    img_paths=discovery.img_paths,
                    img_preview_path=discovery.img_preview_path,
                    kind_id=discovery.kind_id,
                    state_id=discovery.state_id,
                    title=discovery.title,
                    video_paths=discovery.video_paths,
                )
                for discovery in discoveries
            ],
        )
    else:
        raise HTTPException(status_code=404, detail="No discoveries found.")


# Update every field at once, it doesn’t update new empty fields.
@discovery.patch("/")
def update(    discovery_id: int,    discovery_data: schemas.DiscoveryBase,    db: Session = Depends(get_db),    _=Depends(auth.get_admin_priviledge),):
    """
    The function `update` updates the fields of a discovery object in the database based on the provided
    data.
    
    \n**param** discovery_id: The `discovery_id` parameter is an integer that represents the unique
    identifier of a discovery. It is used to identify the specific discovery that needs to be updated
    **type** discovery_id: int
    \n**param** discovery_data: The `discovery_data` parameter is an instance of the `DiscoveryBase` schema.
    It contains the data that will be used to update the discovery object
    **type** discovery_data: schemas.DiscoveryBase
    \n**param** db: The `db` parameter is an instance of the `Session` class, which represents a connection
    to the database. It is used to perform database operations such as querying and updating data
    **type** db: Session
    \n**param** _: The underscore (_) is used as a variable name to indicate that the value is not going to
    be used in the function. It is commonly used when a function requires a certain parameter but the
    value of that parameter is not needed within the function itself
    \n**return**: a dictionary with the key "result" and the value being the result of the `crud.update(db)`
    function.
    """
    discovery = crud.get_discovery(db, discovery_id)
    if discovery:
        if discovery_data.title:
            discovery.title = discovery_data.title
        if discovery_data.description:
            discovery.description = discovery_data.description
        if discovery_data.video_paths:
            discovery.video_paths = discovery.video_paths
        if discovery_data.coordinate_gps:
            new_coordinate_gps = f"POINT ({discovery_data.coordinate_gps})"
            discovery.coordinate_gps = new_coordinate_gps
        if discovery_data.img_preview_path:
            discovery.img_preview_path = discovery_data.img_preview_path
        if discovery_data.img_paths:
            discovery.img_paths = discovery_data.img_paths
        if discovery_data.state_id:
            discovery.state_id = discovery_data.state_id
        if discovery_data.kind_id:
            discovery.kind_id = discovery_data.kind_id

        return {"result": crud.update(db)}
    else:
        raise HTTPException(status_code=404, detail="Discovery not found")


# Creates a new discovery.
@discovery.post("/")
def create(    discovery: schemas.DiscoveryBase,    db: Session = Depends(get_db),    _=Depends(auth.get_admin_priviledge),):
    """
    The function creates a new discovery object in the database with the provided information.
    
    \n**param** discovery: The `discovery` parameter is an instance of the `DiscoveryBase` schema. It
    contains the data needed to create a new discovery entry in the database
    **type** discovery: schemas.DiscoveryBase
    \n**param** db: The `db` parameter is a database session object. It is used to interact with the database
    and perform CRUD operations
    **type** db: Session
    \n**param** _: The underscore (_) parameter is used as a placeholder for a variable that is not going to
    be used in the function. In this case, it is used as a placeholder for the admin privilege, which is
    obtained through the `auth.get_admin_privilege` dependency
    \n**return**: a dictionary with a key "result" and the value is the result of calling the
    `create_discovery` function from the `crud` module with the `db` and `new_discovery` arguments.
    """
    if discovery.state_id < 0 or discovery.state_id > 2:
        raise HTTPException(status_code=400, detail="state_id must be either 1 or 2.")

    coordinate_gps = f"POINT ({discovery.coordinate_gps})"
    new_discovery = models.Discovery(
        title=discovery.title,
        description=discovery.description,
        img_preview_path=discovery.img_preview_path,
        img_paths=discovery.img_paths,
        video_paths=discovery.video_paths,
        coordinate_gps=coordinate_gps,
        address=discovery.address,
        kind_id=discovery.kind_id,
        state_id=discovery.state_id,
    )
    return {"result": crud.create_discovery(db=db, new_discovery=new_discovery)}


# Deletes the discovery by its id.
@discovery.delete("/")
def delete(    discovery_id: int,    db: Session = Depends(get_db),    _=Depends(auth.get_admin_priviledge),):
    """
    The `delete` function deletes a discovery from the database based on its ID.
    
    \n**param** discovery_id: The `discovery_id` parameter is an integer that represents the unique
    identifier of the discovery that needs to be deleted
    **type** discovery_id: int
    \n**param** db: The `db` parameter is of type `Session` and is used to access the database session
    **type** db: Session
    \n**param** _: The underscore (_) is used as a variable name to indicate that the value is not going to
    be used in the function. It is commonly used when a function requires a certain dependency or
    parameter, but the value itself is not needed within the function's logic
    \n**return**: a dictionary with a key "result" and the value being the result of calling the
    `crud.delete_discovery()` function.
    """
    discovery_to_remove = crud.get_discovery(db=db, discovery_id=discovery_id)
    if discovery_to_remove:
        return {
            "result": crud.delete_discovery(
                discovery_to_remove=discovery_to_remove, db=db
            )
        }
    else:
        raise HTTPException(
            status_code=404, detail=f"No discovery found with id: {discovery_id}"
        )


@discovery.get("/distance", response_model=schemas.DistanceResponseModel)
def distance(    my_position: str,    db: Session = Depends(get_db),    _: schemas.HostUser = Depends(auth.get_tourist_host_admin_priviledge),):
    """
    The function calculates the distances from a given position to discoveries and returns the results
    in kilometers.
    
    \n**param** my_position: The `my_position` parameter is a string representing the position of the user.
    It should be in the format "latitude, longitude" or "longitude, latitude". For example, "40.7128,
    -74.0060" represents the position of New York City
    **type** my_position: str
    \n**param** db: The `db` parameter is a database session object. It is used to interact with the database
    and perform CRUD operations
    **type** db: Session
    \n**param** _: The underscore (_) in the function signature is used as a placeholder for a variable that
    is not going to be used in the function. In this case, it is used to indicate that the function
    depends on the `schemas.HostUser` dependency, but the value of that dependency is not going to be
    used
    **type** _: schemas.HostUser
    \n**return**: a dictionary with the key "result" and the value being another dictionary. The inner
    dictionary contains the distances in kilometers from the given position to the discoveries found in
    the database.
    """
    distances_in_m = crud.distance_from_discoveries(
        db=db,
        my_position=f"POINT({my_position})",
    )

    if distances_in_m:
        result = {int(distance[0]): distance[1] / 1000 for distance in distances_in_m}
        return {"result": result}
    else:
        raise HTTPException(status_code=404, detail="No discoveries found.")
