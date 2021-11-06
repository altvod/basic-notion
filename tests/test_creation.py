from tests.models import ReadingListItem


def test_create_page(sync_client, settings):
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
