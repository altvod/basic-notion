import uuid
from typing import Type

from notion_client import Client

from basic_notion.database import NotionDatabase
from basic_notion.page import NotionPage, NotionPageList
from basic_notion.query import Query


def create_database_from_model(
        sync_client: Client,
        model: Type[NotionPage],
        title: str,
        parent_page_id: str,
) -> NotionDatabase:
    database = NotionDatabase.make(
        title=[title],
        parent={'page_id': parent_page_id},
        properties=model.schema,
    )
    data = sync_client.databases.create(**database.data)
    created_database = NotionDatabase(data=data)
    return created_database


_DB_REGISTRY: dict[Type[NotionPage], NotionDatabase] = {}


def get_database_from_model(
        sync_client: Client,
        model: Type[NotionPage],
        parent_page_id: str,
) -> NotionDatabase:
    if model in _DB_REGISTRY:
        return _DB_REGISTRY[model]

    title = f'Test Database {str(uuid.uuid4())}'
    database = create_database_from_model(
        sync_client=sync_client, model=model, title=title,
        parent_page_id=parent_page_id,
    )
    return database


def get_id_list(sync_client: Client, list_model: Type[NotionPageList], database_id: str) -> list[str]:
    # Get the model class of the item
    model = list_model.item
    # Get any property (to sort the query, which is required)
    any_prop = next(iter(model.schema.properties.values()))
    data = sync_client.databases.query(
        **Query(database_id=database_id).sorts(
            any_prop.sort.ascending
        ).serialize()
    )
    item_list = list_model(data=data)
    return [item.id for item in item_list.items()]
