import datetime

from basic_notion.parent import ParentDatabase

from tests.models import ReadingList, ReadingListItem
from tests.tools import get_id_list


def test_page_list_class():
    assert ReadingList.item is ReadingListItem


def test_page_list(reading_list):
    assert len(reading_list.items())
    for item in reading_list.items():
        assert isinstance(item, ReadingListItem)


def test_page_attrs(reading_list_item):
    page = reading_list_item

    # Attributes
    assert len(page.id) == 36
    assert page.created_time.replace(tzinfo=None) > datetime.datetime(2000, 1, 1)
    assert page.last_edited_time.replace(tzinfo=None) > datetime.datetime(2000, 1, 1)
    assert 'http' in page.url

    # Type (select)
    assert page.type.name
    assert page.type.color
    assert len(page.type.option_id) == 36

    # Name (title)
    assert page.name.get_text()

    # Authors (multi_select)
    assert page.authors.items[0].name
    assert page.authors.items[0].color
    assert len(page.authors.items[0].option_id) == 36
    assert page.authors.get_text()


def test_page_make():
    expected_data = {
        'object': 'page',
        'parent': {'database_id': 'qwerty'},
        'properties': {
            'Type': {'type': 'select', 'select': {'name': 'Book'}},
            'Name': {'type': 'title', 'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': 'The Best Book Ever',
                    }
                }
            ]},
            'Author': {'type': 'multi_select', 'multi_select': [{'name': 'John Doe'}]},
        }
    }
    data = ReadingListItem.make(
        parent={'database_id': 'qwerty'},
        type='Book',
        name=['The Best Book Ever'],
        authors=['John Doe'],
    ).data
    assert data == expected_data

    data = ReadingListItem.make(
        parent=ParentDatabase.make(
            database_id='qwerty'
        ),
        type='Book',
        name=['The Best Book Ever'],
        authors=['John Doe'],
    ).data
    assert data == expected_data


def test_create_and_archive_page(sync_client, rl_database):
    page_data = ReadingListItem.make(
        parent=ParentDatabase.make(database_id=rl_database.id),
        type='Book',
        name=['The Best Book Ever'],
        authors=['John Doe'],
    ).data
    response = sync_client.pages.create(**page_data)
    item = ReadingListItem(data=response)
    assert len(item.id) == 36
    assert item.type.name == 'Book'
    assert item.name.get_text() == 'The Best Book Ever'
    assert item.authors.get_text() == 'John Doe'

    id_list = get_id_list(sync_client=sync_client, list_model=ReadingList, database_id=rl_database.id)
    assert item.id in id_list

    # Now archive (delete) it
    item.archived = True
    sync_client.pages.update(page_id=item.id, **item.data)
    id_list = get_id_list(sync_client=sync_client, list_model=ReadingList, database_id=rl_database.id)
    assert item.id not in id_list
