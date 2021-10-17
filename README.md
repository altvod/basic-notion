# basic-notion
Client-agnostic model wrapper for Notion API

##Installation

Just like any othjer python package out there, it can be installed via `pip`

```bash
pip install basic-notion
```

## Basic Examples

### Describing Models
```python
from basic_notion.base import NotionPage, NotionList
from basic_notion.field import SelectField, TitleField 


class ReadingListItem(NotionPage):
    type: SelectField = SelectField(property_name='Type')
    name: TitleField = TitleField(property_name='Name')


class ReadingList(NotionList[ReadingListItem]):
    _ITEM_CLS = ReadingListItem

```

### Using With `notion-sdk-py`

```python
import asyncio
import os

from notion_client import AsyncClient
from basic_notion.query import Query

from models import ReadingList


async def get_reading_list() -> ReadingList:
    database_id = os.environ.get('DATABASE_ID')
    notion_token = os.environ.get('NOTION_TOKEN')
    notion = AsyncClient(auth=notion_token)
    data = await notion.databases.query(
        **Query(database_id).filter(
            ReadingList.item.type.filter.equals('Book')
        ).serialize()
    )
    return ReadingList(data=data)


def print_reading_list(reading_list: ReadingList) -> None:
    for item in reading_list.items:
        print(f'[{item.type.name}] {item.name.one_item.content}')


async def main() -> None:
    reading_list = await get_reading_list()
    print_reading_list(reading_list)


asyncio.run(main())
```
(assuming you put the previous code in `models.py`)

See `notion-sdk-py`'s homepage for more info on the client: https://github.com/ramnes/notion-sdk-py

## Links

Homepage on GitHub: https://github.com/altvod/basic-notion

Project's page on PyPi: https://pypi.org/project/basic-notion/

Notion API: https://developers.notion.com/
