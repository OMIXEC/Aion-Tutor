from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Capability(BaseModel):
    name: str = Field(description="Name of the capability")
    description: str = Field(description="Description of what this capability does")

class Endpoints(BaseModel):
    chat: str = Field(description="POST endpoint for chat/task execution")
    health: str = Field(description="GET endpoint for health check")

class AgentCard(BaseModel):
    """
    Standardized A2A Agent Card.
    Hosted on the MCP Server, fetched by the Orchestrator.
    """
    id: str = Field(description="Unique agent identifier")
    name: str = Field(description="Human readable name")
    description: str = Field(description="Description of the agent's specialization")
    capabilities: List[Capability] = Field(description="List of capabilities")
    endpoints: Endpoints = Field(description="Network endpoints for A2A communication")

class A2AMessage(BaseModel):
    """
    Standardized message payload for A2A communication over HTTP.
    """
    session_id: str
    user_id: str
    role: str = Field(default="user")
    content: str
    context: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None
    
class A2AResponse(BaseModel):
    """
    Standardized response payload for A2A communication.
    """
    reply: str
    metadata: Optional[Dict[str, Any]] = None
    agent_id: str
