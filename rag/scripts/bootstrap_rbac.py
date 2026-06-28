from connection import get_client, close
from config import (
    WEAVIATE_ADMIN_API_KEY,
    WEAVIATE_RAG_USER
)


def main():

    try:

        client = get_client(WEAVIATE_ADMIN_API_KEY)

        roles = client.users.db.get_assigned_roles(
            user_id=WEAVIATE_RAG_USER,
        )

        check = "viewer" in roles.keys()

        if not check:

            client.users.db.assign_roles(
                user_id=WEAVIATE_RAG_USER,
                role_names=["viewer"]
            )

            roles = client.users.db.get_assigned_roles(
                user_id=WEAVIATE_RAG_USER,
            )

            check = "viewer" in roles.keys()

            print(
                f"Assigning 'viewer' role to '{WEAVIATE_RAG_USER}': {check}."
            )

        else:

            print(
                f"Role 'viewer' already assigned to '{WEAVIATE_RAG_USER}'."
            )

    finally:

        close()


if __name__ == "__main__":
    main()
