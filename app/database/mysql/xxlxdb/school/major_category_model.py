from typing import Optional

from pydantic import BaseModel, Field


class MajorCategoryModel(BaseModel):
    id:  Optional[str] = Field(None,description="id")
    category_english_name: Optional[str] = Field(None,description="分类中文名称")
    zh_category_name: Optional[str] = Field(None,description="分类英文名称")
