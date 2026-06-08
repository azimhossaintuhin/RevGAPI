from pydantic import BaseModel, Field
from typing import Union, Literal



class AgentOutput(BaseModel):
    feedback_language: str = Field(..., description="The language of the comment or feedback")
    translation: str | None= Field(default=None, description="The translation of the comment or feedback in english, if the comment or feedback is not in english")
    sentiment: Union[Literal["positive", "negative", "neutral"]] = Field(..., description="The sentiment of the comment or feedback")
    summary: str = Field(..., description="The summary of the comment or feedback")
    pros: list[str] = Field(..., description="The pros of the comment or feedback")
    cons: list[str] = Field(..., description="The cons of the comment or feedback")
    action_items: list[str] = Field(..., description="The action items to improve the comment or feedback")
    suggestions: list[str] = Field(..., description="The suggestions to improve the comment or feedback")
    customer_repeats: bool = Field(..., description="Will  it be a repeat customer?")
    confidence_score: float = Field(..., description="The confidence score of the sentiment")
    
    
    