from app.common.core.langchain_client import Embedding
from app.database.weaviate.major_category_weaviate import major_category_weaviate

query = 'it'
doc_vecs = Embedding.embed_query(query)

major_category_weaviate.hybrid_data(query, ["category_english_name","zh_category_name"], doc_vecs)
