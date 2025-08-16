from pydantic import BaseModel
from typing import List


class SplitRequest(BaseModel):
    page_ranges: str


class SplitResponse(BaseModel):
    success: bool
    message: str
    filename: str = None


class ErrorResponse(BaseModel):
    success: bool
    message: str
    details: str = None