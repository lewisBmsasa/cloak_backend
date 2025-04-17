from pydantic import BaseModel
from typing import List, Dict

# Pydantic models
class SystemPrompts(BaseModel):
    detect: str
    abstract: str = None


class MessageRequest(BaseModel):
    message: str
    system_prompts: SystemPrompts = None


class WordListRequest(BaseModel):
    words: Dict[str, List[int]] 
