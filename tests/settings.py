import os

import attr


@attr.s
class TestSettings:
    api_token: str = attr.ib(kw_only=True)
    root_page_id: str = attr.ib(kw_only=True)


def load_settings_from_env() -> TestSettings:
    return TestSettings(
        api_token=os.environ['NOTION_API_TOKEN'],
        root_page_id=os.environ['ROOT_PAGE_ID'],
    )
