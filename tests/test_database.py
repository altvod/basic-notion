import uuid

from basic_notion.database import NotionDatabase
from basic_notion.property_schema import (
    MultiSelectPropertySchema, TitlePropertySchema, SelectPropertySchema,
)

from tests.models import ReadingListItem


def test_database_make():
    root_page_id = 'qwertysmth'
    title = f'The New Database'
    database = NotionDatabase.make(
        title=[title],
        parent={'page_id': root_page_id},
        properties=ReadingListItem.schema,
    )
    assert database.title.get_text() == title
    assert database.parent.page_id == root_page_id


def test_create_database(sync_client, settings):
    rand_uuid = str(uuid.uuid4())
    root_page_id = settings.root_page_id
    database = NotionDatabase.make(
        title=[f'The New Database {rand_uuid}'],
        parent={'page_id': root_page_id},
        properties=ReadingListItem.schema,
    )
    data = sync_client.databases.create(**database.data)
    database = NotionDatabase(data=data)
    assert database.id
    assert database.title.get_text() == f'The New Database {rand_uuid}'
    assert database.parent.norm_page_id == root_page_id.replace('-', '')
    schema = database.schema
    assert isinstance(schema['Name'], TitlePropertySchema)
    assert isinstance(schema['Type'], SelectPropertySchema)
    assert isinstance(schema['Author'], MultiSelectPropertySchema)
