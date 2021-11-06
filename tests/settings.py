import os

import attr


@attr.s
class TestSettings:
    api_token: str = attr.ib(kw_only=True)
    database_id: str = attr.ib(kw_only=True)
    root_page_id: str = attr.ib(kw_only=True, default='')


def load_settings_from_env() -> TestSettings:
    return TestSettings(
        api_token=os.environ['NOTION_API_TOKEN'],
        database_id=os.environ['DATABASE_ID'],
        root_page_id=os.environ['ROOT_PAGE_ID'],
    )
