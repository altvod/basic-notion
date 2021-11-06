import pytest
from notion_client import Client

from basic_notion.query import Query
from tests.settings import TestSettings, load_settings_from_env
from tests.models import ReadingList, ReadingListItem


@pytest.fixture(scope='session')
def settings() -> TestSettings:
    return load_settings_from_env()


@pytest.fixture(scope='session')
def sync_client(settings) -> Client:
    return Client(auth=settings.api_token)


@pytest.fixture(scope='session')
def database_query(settings) -> Query:
    return Query(database_id=settings.database_id)


@pytest.fixture(scope='function')
def reading_list(sync_client, database_query) -> ReadingList:
    data = sync_client.databases.query(
        **database_query.filter(
            ReadingList.item.type.filter.equals('Book')
        ).sorts(
            ReadingList.item.name.sort.ascending
        ).serialize()
    )
    return ReadingList(data=data)


@pytest.fixture(scope='function')
def db_page_item(reading_list):
    return reading_list.items()[0]
