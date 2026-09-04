"""
Post Pydantic model. 
"""
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

Platform = Literal["twitter", "instagram", "facebook", "linkedin"]
Compliance_Status = Literal["pending", "approved", "blocked"]

class Post(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int     # Identifier
    platform: Platform  
    caption_text: str = Field(min_length=20, max_length=5000)  #text body
    image: str | None = None #Optional Image. 
    scheduled_publish_time: datetime
    brand_id: int  # Identifier of assigned brand. 
    compliance_status: Compliance_Status = "pending" #Default to pending status 

    # Validate image being a .png or .jpg
    @field_validator("image")
    def must_be_png_or_jpg(cls, file_name):
        if file_name is None:
            return file_name
        if not file_name.lower().endswith((".png", ".jpg")):
            raise ValueError("File must be a .png or .jpg image")
        return file_name



class PostDto(BaseModel):
    # forbid extra parameters
    model_config = ConfigDict(extra="forbid")


    platform: Platform  
    caption_text: str = Field(max_length=5000)  #text body
    image: str | None = None #Optional Image. 
    scheduled_publish_time: datetime
    brand_id: int
    compliance_status: Compliance_Status = "pending" #Default to pending status 
    # We don't need to establish default. 

    # Validate image being a .png or .jpg
    @field_validator("image")
    def must_be_png_or_jpg(cls, file_name):
        if file_name is None:
            return file_name
        if not file_name.lower().endswith((".png", ".jpg")):
            raise ValueError("File must be a .png or .jpg image")
        return file_name
