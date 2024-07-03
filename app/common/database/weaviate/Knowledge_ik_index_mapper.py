import os
from typing import Optional

from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from weaviate.collections.classes.grpc import HybridFusion, MetadataQuery

from app.common.database.weaviate.weaviate_client import WeaviateClient
from app.common.core.langchain_client import Embedding
from app.common.utils.logging import get_logger
from app.prompt.prompt_load import generate_prompt

collections_name = "Knowledge_ik_index"

collections = WeaviateClient.client.collections.get(collections_name)
logger = get_logger(__name__)

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

    @classmethod
    def generate_prompt(self, text: str) -> str:
        """生成包含参考数据的完整 prompt."""
        response_list = self.search_hybrid(text, 10)
        reference_data = "\n\n".join(
            [f"Reference data {n + 1}: {response_list[n].instruction}————{response_list[n].output}"
             for n in range(len(response_list))])
        logger.info(reference_data)

        template = generate_prompt("knowledge_prompt.txt")
        prompt = template.format(input=text, reference_data=reference_data)

        return prompt


if __name__ == '__main__':
    print(KnowledgeIkIndexMapper.search_hybrid("墨尔本大学怎么样", 10))
