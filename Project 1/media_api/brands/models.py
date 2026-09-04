"""
Brands Pydantic model with it's restrictions. 
 """

from pydantic import BaseModel, Field, ConfigDict


class Brand(BaseModel):
    # Allows Pydantic to validate other sqlalchemy objects. 
    model_config = ConfigDict(from_attributes=True)

    id: int 
    name: str = Field(min_length=1, max_length=100)
    industry: str = Field(min_length=1, max_length=100)

class BrandDto(BaseModel):

    # Prevent additional parameters. 
    model_config = ConfigDict(extra="forbid")   

    #ID is not necessary for updating an existing brand. 
    name: str = Field(min_length=1, max_length=100)
    industry: str = Field(min_length=1, max_length=100)
