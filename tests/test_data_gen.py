from basic_notion.parent import ParentDatabase

from tests.models import ReadingListItem


def test_page_make():
    expected_data = {
        'object': 'page',
        'parent': {'database_id': 'qwerty'},
        'properties': {
            'Type': {'type': 'select', 'select': {'name': 'Book'}},
            'Name': {'type': 'title', 'title': [{'type': 'text', 'text': {'content': 'The Best Book Ever'}}]},
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
