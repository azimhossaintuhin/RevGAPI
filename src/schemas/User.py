from  pydantic import BaseModel, Field, field_serializer, ConfigDict, field_validator , EmailStr
from uuid import UUID
from datetime import datetime
from fastapi import UploadFile, Form,File
from decouple import config
BACKEND_URL = config("ALLOWED_DOMAIN")



class UserCreate(BaseModel):
    name: str = Field(..., description="The name of the user")
    email: EmailStr = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user")
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    @field_validator("email")
    @classmethod
    def validate_email(cls, email: EmailStr) -> EmailStr:
        return email.lower().strip()
 
class UserPermissionsOut(BaseModel):
    permission_code: str = Field(..., description="The permission code of the user")
 
 
class UserToken(BaseModel):
    token: str = Field(..., description="The token of the user")
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    
 
 
class UserOutput(BaseModel):
     id: UUID = Field(..., description="The id of the user")
     name: str = Field(..., description="The name of the user")
     email: EmailStr = Field(..., description="The email of the user")
     image_url: str | None = Field(default=None, description="The image url of the user")
     created_at: datetime = Field(..., description="The creation date of the user")
     updated_at: datetime = Field(..., description="The update date of the user")
     is_active: bool = Field(..., description="The active status of the user")
     is_deleted: bool = Field(..., description="The deleted status of the user")
     permissions: list[UserPermissionsOut]  = Field(default_factory=list)
     model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
        
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
    email: EmailStr = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user")
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, email: EmailStr) -> EmailStr:
        return email.lower().strip()
        
class UserLoginOutput(BaseModel):
    access_token: str = Field(..., description="The access token of the user")
    token_type: str = Field(default="bearer", description="The token type")
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    

class UserVerifyPasswordResetToken(BaseModel):
    otp: str = Field(..., description="The OTP of the user")
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    @field_validator("otp")
    @classmethod
    def validate_otp(cls, otp: str) -> str:
        return otp.strip()

class UserForgotPassword(BaseModel):
    email: EmailStr = Field(..., description="The email of the user")
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, email: EmailStr) -> EmailStr:
        return email.lower().strip()

class  UserPasswordReset(BaseModel):
    password: str = Field(..., description="The password of the user")
    confirm_password: str = Field(..., description="The confirm password of the user")
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        return password.strip()
    
    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, confirm_password: str) -> str:
        return confirm_password.strip()



# ======= Api key ======== #
class UserApiKey(BaseModel):
    api_key: str = Field(..., description="The API key of the user")
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, api_key: str) -> str:
        return api_key.strip()