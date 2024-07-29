import weaviate
from weaviate.classes.query import Filter, MetadataQuery

client = weaviate.connect_to_local(grpc_port=50060, port=8079, skip_init_checks=True)
collections_name = 'Qwen_data_base'
jeopardy = client.collections.get(collections_name)


def delete_many():
    jeopardy.data.delete_many(
        where=Filter.by_property("datasets").like("*zn_school_department_project_01*"),
        # dry_run=True,
        # verbose=True
    )


def query_bm25():
    response = jeopardy.query.bm25(
        query="zn_school_department_project",
        query_properties=["database"],
        return_metadata=MetadataQuery(score=True),
        limit=3
    )

    for o in response.objects:
        print(o.properties)
        print(o.metadata.score)


if __name__ == "__main__":
    query_bm25()
