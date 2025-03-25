from pydantic import BaseModel

# Pydantic models
class MessageRequest(BaseModel):
    message: str



