from connection import (
    get_client,
    close
)

from config import (
    COLLECTION_NAME,
    WEAVIATE_ADMIN_API_KEY
)

from weaviate.classes.config import (
    Configure,
    Property,
    DataType
)


def create_collection():

    client = get_client(WEAVIATE_ADMIN_API_KEY)

    collections = client.collections

    if collections.exists(COLLECTION_NAME):

        print(
            f"Collection '{COLLECTION_NAME}' already exists."
        )

        return

    collections.create(
        name=COLLECTION_NAME,

        description=(
            "Wikipedia knowledge base for "
            "debate tournament retrieval."
        ),

        properties=[

            Property(
                name="pageid",
                data_type=DataType.INT
            ),

            Property(
                name="chunk_id",
                data_type=DataType.INT
            ),

            Property(
                name="title",
                data_type=DataType.TEXT
            ),

            Property(
                name="domain",
                data_type=DataType.TEXT
            ),

            Property(
                name="url",
                data_type=DataType.TEXT
            ),

            Property(
                name="revision_id",
                data_type=DataType.INT
            ),

            Property(
                name="retrieved_at",
                data_type=DataType.DATE
            ),

            Property(
                name="source",
                data_type=DataType.TEXT
            ),

            Property(
                name="section_title",
                data_type=DataType.TEXT
            ),

            Property(
                name="section_index",
                data_type=DataType.INT
            ),

            Property(
                name="categories",
                data_type=DataType.TEXT_ARRAY
            ),

            Property(
                name="text",
                data_type=DataType.TEXT
            )

        ],

        # vectorizer_config=Configure.Vectorizer.none()
        vector_config=Configure.Vectors.self_provided()
    )

    print(
        f"Created collection '{COLLECTION_NAME}'."
    )


def delete_collection():

    client = get_client()

    collections = client.collections

    if collections.exists(COLLECTION_NAME):

        collections.delete(COLLECTION_NAME)

        print(
            f"Deleted collection '{COLLECTION_NAME}'."
        )

    else:

        print(
            f"Collection '{COLLECTION_NAME}' does not exist."
        )


if __name__ == "__main__":

    try:

        create_collection()

    finally:

        close()
