from tests.models import ReadingList, ReadingListItem


def test_page_list_class():
    assert ReadingList.item is ReadingListItem


def test_page_list(reading_list):
    assert len(reading_list.items())
    for item in reading_list.items():
        assert isinstance(item, ReadingListItem)


def test_page(db_page_item):
    page = db_page_item

    # Attributes
    assert len(page.id) == 36
    assert page.created_time > '1900'
    assert page.last_edited_time > '1900'
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
