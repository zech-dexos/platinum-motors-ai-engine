from fastapi import FastAPI, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from inventory import Vehicle, VehicleStatus
from parser import manual_intake

app = FastAPI(
    title="Platinum Motors AI Engine",
    description="Backend for custom dealership AI sales and inventory management.",
    version="1.0.0"
)

# In-memory mock database for inventory (max 37 cars locally typically, as per specs)
inventory_db: Dict[str, Vehicle] = {}

# Pydantic models for chat
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    qualified_lead: bool
    recommended_vins: List[str]

@app.get("/inventory", response_model=List[Vehicle])
async def get_inventory():
    """Returns all active and upcoming vehicles."""
    return [v for v in inventory_db.values() if v.status != VehicleStatus.SOLD]

@app.get("/inventory/search", response_model=List[Vehicle])
async def search_inventory(
    q: Optional[str] = Query(None, description="General text search query"),
    make: Optional[str] = Query(None, description="Filter by make"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    status: Optional[VehicleStatus] = Query(None, description="Filter by status")
):
    """Allows filtering by query string, make, price range, and status."""
    results = list(inventory_db.values())
    
    if q:
        q_lower = q.lower()
        results = [
            v for v in results 
            if q_lower in v.make.lower() 
            or q_lower in v.model.lower() 
            or (v.description and q_lower in v.description.lower())
        ]
    
    if make:
        make_lower = make.lower()
        results = [v for v in results if v.make.lower() == make_lower]
        
    if min_price is not None:
        results = [v for v in results if v.price is not None and v.price >= min_price]
        
    if max_price is not None:
        results = [v for v in results if v.price is not None and v.price <= max_price]
        
    if status:
        results = [v for v in results if v.status == status]
        
    return results

@app.post("/intake/manual", response_model=Vehicle)
async def intake_manual(raw_data: Dict[str, Any] = Body(...)):
    """
    Endpoint for dealership staff to instantly add/update a "Coming Soon" vehicle 
    or push a new VIN into the active catalog.
    """
    vehicle = manual_intake(raw_data)
    if not vehicle:
        raise HTTPException(status_code=400, detail="Invalid vehicle data provided.")
    
    # Add or update in the mock db
    inventory_db[vehicle.vin] = vehicle
    return vehicle

@app.post("/chat/agent", response_model=ChatResponse)
async def chat_agent(request: ChatRequest):
    """
    Receives inbound customer messages from the website widget, matches the query 
    against current vehicle data, and generates a context-aware response.
    (Mocked LLM logic for scaffolding).
    """
    message_lower = request.message.lower()
    
    # Mock simple intent matching for demonstration
    recommended_vins = []
    reply = "Hello! I am the Platinum Motors AI assistant. How can I help you today? Would you like to schedule a test drive?"
    qualified_lead = False
    
    if "test drive" in message_lower:
        qualified_lead = True
        reply = "Great! I can help you schedule a test drive. Which vehicle are you interested in?"
        
    # Search for mentioned makes in inventory
    available_makes = {v.make.lower() for v in inventory_db.values()}
    for make in available_makes:
        if make in message_lower:
            matched_vehicles = [v for v in inventory_db.values() if v.make.lower() == make]
            if matched_vehicles:
                recommended_vins = [v.vin for v in matched_vehicles[:3]] # Recommend up to 3
                reply = f"We have {len(matched_vehicles)} {make.capitalize()}s available. Would you like to know more about pricing or schedule a test drive?"
                break

    return ChatResponse(
        reply=reply,
        qualified_lead=qualified_lead,
        recommended_vins=recommended_vins
    )
