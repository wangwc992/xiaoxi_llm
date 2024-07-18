from typing import Optional

from pydantic import BaseModel
from weaviate.collections.classes.grpc import HybridFusion, MetadataQuery

from app.database.weaviate.weaviate_client import WeaviateClient
from app.common.core.langchain_client import Embedding

collections_name = "Knowledge_ik_index"

collections = WeaviateClient.client.collection.get(collections_name)
class KnowledgeIkIndexModel(BaseModel):
    uuid: Optional[str]
    instruction: str
    output: str


class KnowledgeIkIndexMapper:

    @classmethod
    def search_hybrid(cls, query, limit):
        response = collections.query.hybrid(
            query=query,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            target_vector="instruction",
            vector=Embedding.embed_query(query),
            # query_properties=["instruction", "output"],
            return_metadata=MetadataQuery(score=True, explain_score=True),
            limit=limit,
        )
        response_list = []
        for o in response.objects:
            Knowledge_ik_index_model = KnowledgeIkIndexModel(uuid=str(o.uuid), instruction=o.properties['instruction'],
                                                             output=o.properties['output'])
            response_list.append(Knowledge_ik_index_model)
        return response_list


if __name__ == '__main__':
    print(KnowledgeIkIndexMapper.search_hybrid("墨尔本大学怎么样", 10))
