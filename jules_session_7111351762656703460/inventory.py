from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class VehicleStatus(str, Enum):
    IN_STOCK = "In Stock"
    COMING_SOON = "Coming Soon"
    SOLD = "Sold"

class Vehicle(BaseModel):
    vin: str = Field(..., description="Vehicle Identification Number")
    year: int = Field(..., description="Manufacturing year")
    make: str = Field(..., description="Vehicle make (e.g., Toyota)")
    model: str = Field(..., description="Vehicle model (e.g., Camry)")
    trim: Optional[str] = Field(None, description="Vehicle trim level")
    price: Optional[float] = Field(None, description="Listing price")
    mileage: Optional[int] = Field(None, description="Odometer reading in miles")
    exterior_color: Optional[str] = Field(None, description="Exterior color of the vehicle")
    status: VehicleStatus = Field(default=VehicleStatus.COMING_SOON, description="Current status of the vehicle")
    description: Optional[str] = Field(None, description="Detailed text description")
    image_urls: List[str] = Field(default_factory=list, description="List of image URLs")

    @field_validator('year')
    @classmethod
    def check_year(cls, v):
        if v < 1900 or v > 2100:
            raise ValueError('Year must be between 1900 and 2100')
        return v
    
    @field_validator('price')
    @classmethod
    def check_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('Price cannot be negative')
        return v

    @field_validator('mileage')
    @classmethod
    def check_mileage(cls, v):
        if v is not None and v < 0:
            raise ValueError('Mileage cannot be negative')
        return v
