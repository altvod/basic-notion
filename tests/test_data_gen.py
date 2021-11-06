from basic_notion.parent import ParentDatabase
from tests.models import ReadingListItem


def test_page_generate():
    data = ReadingListItem.generate(
        parent=ParentDatabase.generate(
            database_id='qwerty'
        ),
        type='Book',
        name=['The Best Book Ever'],
        authors=['John Doe'],
    )
    assert data == {
        'parent': {'database_id': 'qwerty'},
        'properties': {
            'Type': {'select': {'name': 'Book'}},
            'Name': {'title': [{'text': {'content': 'The Best Book Ever'}}]},
            'Author': {'multi_select': [{'name': 'John Doe'}]},
        }
    }
