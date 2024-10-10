from typing import Optional

from pydantic import BaseModel, Field
from app.database.weaviate.weaviate_client import WeaviateClient
from weaviate.classes.config import Property
from weaviate.collections.classes.config import DataType


class MajorCategoryWeaviateModel(BaseModel):
    db_id: Optional[int] = Field(None, description='数据库的id')
    zh_category_name: Optional[str] = Field(None, description='专业中文名')
    category_english_name: Optional[str] = Field(None, description='专业英文名')


class MajorCategoryWeaviate(WeaviateClient):
    collections_name = "Major_category"
    properties = [
        Property(name='db_id', data_type=DataType.INT, description='数据库的id'),
        Property(name='zh_category_name', data_type=DataType.TEXT, description='专业中文名'),
        Property(name='category_english_name', data_type=DataType.TEXT, description='专业英文名'),
    ]


major_category_weaviate = MajorCategoryWeaviate(MajorCategoryWeaviate.collections_name)

if __name__ == "__main__":
    major_category_weaviate.delete_collection_name(MajorCategoryWeaviate.collections_name)
    major_category_weaviate.create_collection(MajorCategoryWeaviate.properties)
