import pytest
from notion_client import Client

from basic_notion.parent import ParentDatabase
from basic_notion.database import NotionDatabase
from basic_notion.query import Query

from tests.settings import TestSettings, load_settings_from_env
from tests.models import ReadingList, ReadingListItem
from tests.tools import get_database_from_model


@pytest.fixture(scope='session')
def settings() -> TestSettings:
    return load_settings_from_env()


@pytest.fixture(scope='session')
def sync_client(settings) -> Client:
    return Client(auth=settings.api_token)


@pytest.fixture(scope='session')
def rl_database(settings, sync_client) -> NotionDatabase:
    database = get_database_from_model(
        sync_client=sync_client, model=ReadingListItem,
        parent_page_id=settings.root_page_id,
    )
    page = ReadingListItem.make(
        parent=ParentDatabase.make(database_id=database.id),
        type='Book',
        name=['The Best Book Ever'],
        authors=['John Doe'],
    )
    # TODO: Insert several books
    sync_client.pages.create(**page.data)
    return database


@pytest.fixture(scope='session')
def rl_database_query(rl_database) -> Query:
    return Query(database_id=rl_database.id)


@pytest.fixture(scope='function')
def reading_list(sync_client, rl_database_query, settings) -> ReadingList:
    query_data = rl_database_query.filter(
        ReadingList.item.type.filter.equals('Book')
    ).sorts(
        ReadingList.item.name.sort.ascending
    ).serialize()
    data = sync_client.databases.query(**query_data)
    return ReadingList(data=data)


@pytest.fixture(scope='function')
def reading_list_item(reading_list):
    return reading_list.items()[0]
