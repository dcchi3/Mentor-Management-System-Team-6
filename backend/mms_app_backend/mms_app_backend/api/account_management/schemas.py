from pydantic import BaseModel, HttpUrl


class SocialLink(BaseModel):
    url: HttpUrl
    name: str


class Location(BaseModel):
    city: str
    state: str
    country: str


class BaseProfile(BaseModel):
    about: str
    website: HttpUrl
    social_links: list[SocialLink]
    location: Location


class ViewProfile(BaseProfile):
    username: str
    email: str
    firstname: str
    lastname: str
    is_mentor: bool = False
    is_mentor_manager: bool = False

    class Config:
        orm_mode = True


class CreateProfile(BaseProfile):
    pass
