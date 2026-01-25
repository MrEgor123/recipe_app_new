from pydantic import BaseModel, Field


class PageResponse(BaseModel):
    page: int = Field(ge=1)
    size: int = Field(ge=1, le=50)
    total: int = Field(ge=0)
    pages: int = Field(ge=0)
