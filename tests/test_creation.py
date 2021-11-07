from notion_client import Client

from basic_notion.query import Query

from tests.models import ReadingListItem, ReadingList


def get_id_list(sync_client: Client, database_query: Query) -> list[str]:
    data = sync_client.databases.query(
        **database_query.sorts(
            ReadingList.item.name.sort.ascending
        ).serialize()
    )
    reading_list = ReadingList(data=data)
    return [item.id for item in reading_list.items()]


def test_create_and_archive_page(sync_client, settings):
    page_data = ReadingListItem.generate(
        parent={'database_id': settings.database_id},
        type='Book',
        name=['The Best Book Ever'],
        authors=['John Doe'],
    )
    response = sync_client.pages.create(**page_data)
    item = ReadingListItem(data=response)
    assert len(item.id) == 36
    assert item.type.name == 'Book'
    assert item.name.get_text() == 'The Best Book Ever'
    assert item.authors.get_text() == 'John Doe'

    database_query = Query(database_id=settings.database_id)
    id_list = get_id_list(sync_client=sync_client, database_query=database_query)
    assert item.id in id_list

    # Now archive (delete) it
    item.archived = True
    sync_client.pages.update(page_id=item.id, **item.data)
    id_list = get_id_list(sync_client=sync_client, database_query=database_query)
    assert item.id not in id_list
