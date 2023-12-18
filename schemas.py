from typing import Optional
from pydantic import BaseModel, validator
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement
from shapely.wkb import loads
from binascii import unhexlify
from typing import List
import datetime


# Tourist classes
class TouristUserBase(BaseModel):
    name: str
    surname: str
    email: str
    img_profile: str
    state_id: int
    telephone: str


class TouristUserCreate(TouristUserBase):
    password: str


class TouristUser(TouristUserCreate):
    id: int

    class Config:
        orm_mode = True


class TouristUserResponse(BaseModel):
    result: TouristUserBase


# Host classes
class HostUserBase(BaseModel):
    name: str
    email: str
    img_profile: str
    state_id: int


class HostUserCreate(HostUserBase):
    password: str


class HostUser(HostUserCreate):
    id: int

    class Config:
        orm_mode = True


class HostUserResponse(BaseModel):
    result: HostUserBase


# Experience class
class ExperienceBase(BaseModel):
    title: str
    description: str
    difficulty_id: int
    price: dict
    duration: datetime.time
    img_preview_path: str
    img_paths: List[str]
    state_id: int


class Experience(ExperienceBase):
    id: int

    class Config:
        orm_mode = True


class SingleExperienceResponse(BaseModel):
    result: Experience


class ExperienceResponse(BaseModel):
    cursor: Optional[int]
    has_more: bool
    items: List[Experience]


# Discovery class


class DiscoveryBase(BaseModel):
    title: str
    description: str
    img_preview_path: str
    img_paths: List[str]
    video_paths: List[str]
    coordinate_gps: Optional[str]
    address: str
    kind_id: int
    state_id: int

    @validator("coordinate_gps", pre=True)
    def correct_geom_format(cls, v):
        if isinstance(v, WKBElement):
            wkt_str = ewkb_to_wkt(v)
            return wkt_str
        elif isinstance(v, str):
            return v
        else:
            return ValueError("must be a valid WKBE element")

    class Config:
        orm_mode = True


class Discovery(DiscoveryBase):
    coordinate_gps: str
    id: int


class SingleDiscoveryResponse(BaseModel):
    result: Discovery


def ewkb_to_wkt(geom_hex: str):
    try:
        # Convert the hex string to bytes
        geom_bytes = unhexlify(geom_hex)

        # Create a shapely geometry object from WKB bytes
        a = loads(geom_bytes)

        if a:
            # Return the Well-Known Text (WKT) representation of the geometry
            return a.wkt
    except Exception as e:
        print(e)


class DiscoveryResponse(BaseModel):
    cursor: Optional[int]
    has_more: bool
    items: List[Discovery]


class DistanceResponseModel(BaseModel):
    result: dict


# Like class
class Likes(BaseModel):
    tourist_user_id: int
    experience_id: int

    class Config:
        orm_mode = True


# Popup class
class PopupMsgBase(BaseModel):
    text: str

    class Config:
        orm_mode = True


class PopupMsg(PopupMsgBase):
    id: int

    class Config:
        orm_mode = True


class PopupResponse(BaseModel):
    cursor: Optional[int]
    has_more: bool
    items: List[PopupMsg]


class SinglePopupResponse(BaseModel):
    result: PopupMsg
