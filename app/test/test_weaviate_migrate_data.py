import weaviate
from tqdm import tqdm
from weaviate.classes.query import Filter

weaviate_src = weaviate.connect_to_local(port=8079, grpc_port=50060)
weaviate_tgt = weaviate.connect_to_local("192.168.0.139", 8080)
collections = "Qwen_data_base"

collection_tgt = weaviate_tgt.collections.get(collections)
collection_src = weaviate_src.collections.get(collections)

while True:
    filters = (
        Filter.by_property("instruction").like("*")
    )
    result = collection_tgt.data.delete_many(
        where=filters,
        # dry_run=True,
        # verbose=True
    )
    if result.matches < 10000:
        break
with collection_tgt.batch.fixed_size(batch_size=100) as batch:
    for q in tqdm(collection_src.iterator(include_vector=True)):
        batch.add_object(
            properties=q.properties,
            vector=q.vector["default"],
            uuid=q.uuid
        )
