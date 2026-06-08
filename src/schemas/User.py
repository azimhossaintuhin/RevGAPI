from  pydantic import BaseModel, Field, field_serializer
from uuid import UUID
from datetime import datetime
from fastapi import UploadFile, Form,File
from decouple import config

BACKEND_URL = config("ALLOWED_DOMAIN")



class UserCreate(BaseModel):
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user")

 
 
class UserOutput(BaseModel):
     id: UUID = Field(..., description="The id of the user")
     name: str = Field(..., description="The name of the user")
     email: str = Field(..., description="The email of the user")
     image_url: str | None = Field(default=None, description="The image url of the user")
     created_at: datetime = Field(..., description="The creation date of the user")
     updated_at: datetime = Field(..., description="The update date of the user")
     is_active: bool = Field(..., description="The active status of the user")
     is_deleted: bool = Field(..., description="The deleted status of the user")
     
     class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        
     @field_serializer("image_url")
     def serialize_image_url(self, image_url: str | None) -> str | None:
        if image_url is None:
            return None
        return f"{BACKEND_URL}{image_url}"


class UserUpdate:
    def __init__(self, name: str | None = Form(None), image: UploadFile | None = File(None)):
        self.name = name
        self.image = image
    def model_dump(self):
        return {
            "name": self.name,
            "image": self.image
        }
        
    
        

class UserLogin(BaseModel):
    email: str = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user")
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        
class UserLoginOutput(BaseModel):
    access_token: str = Field(..., description="The access token of the user")
    token_type: str = Field(default="bearer", description="The token type")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        


        
        
        
        