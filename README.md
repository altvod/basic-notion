# basic-notion
Client-agnostic model wrapper for Notion API.

This library does not do any interaction over the network itself,
so it can be used with any existing client that exposes as output
and accepts as input raw JSONable data.

Note that this project is at its infancy stage, so major changes
in its structure and API are quite possible and even probable
in the near future.

## Installation

Just like any other python package out there, it can be installed via `pip`:

```bash
pip install basic-notion
```

## Basic Examples

### Describing Models
```python
from basic_notion.page import NotionPage, NotionPageList
from basic_notion.field import SelectField, TitleField, MultiSelectField


class ReadingListItem(NotionPage):
    type: SelectField = SelectField(property_name='Type')
    name: TitleField = TitleField(property_name='Name')
    status: SelectField = SelectField(property_name='Status')
    authors: MultiSelectField = MultiSelectField(property_name='Author')


class ReadingList(NotionPageList[ReadingListItem]):
    ITEM_CLS = ReadingListItem
```

### Using With `notion-sdk-py`

Fetching a list of pages from a database

```python
import asyncio
import os

from notion_client import AsyncClient
from basic_notion.query import Query

from models import ReadingList


async def get_reading_list() -> ReadingList:
    database_id = os.environ['DATABASE_ID']
    notion_token = os.environ['NOTION_TOKEN']
    notion = AsyncClient(auth=notion_token)
    data = await notion.databases.query(
        **Query.database(
            database_id
        ).filter(
            # Construct filter using model's field
            # (only one filter expression is supported)
            ReadingList.item.type.filter.equals('Book')
        ).sorts(
            # And, similarly, the result's sorting
            # (multiple fields can be listed here)
            ReadingList.item.name.sort.ascending
        ).serialize()
    )
    return ReadingList(data=data)


def print_reading_list(reading_list: ReadingList) -> None:
    for item in reading_list.items():
        print(f'[{item.type.name}] {item.name.one_item.content}')


async def main() -> None:
    reading_list = await get_reading_list()
    print_reading_list(reading_list)


asyncio.run(main())
```
(assuming you put the previous code in `models.py`)

Creating a new page

```python
from notion_client import Client
from models import ReadingListItem

def create_page(client: Client, database_id: str) -> ReadingListItem:
    page_data = ReadingListItem.generate(
        parent={'database_id': database_id},
        type='Book',
        name=['The Best Book Ever'],
        authors=['John Doe'],
    )
    response = client.pages.create(**page_data)
    item = ReadingListItem(data=response)
    # assert len(item.id) == 36
    # assert item.type.name == 'Book'
    # assert item.name.get_text() == 'The Best Book Ever'
    # assert item.authors.get_text() == 'John Doe'
    return item
```

See `notion-sdk-py`'s homepage for more info on the client: https://github.com/ramnes/notion-sdk-py

You can also see the files in `tests/` for more examples
and more thorough usage of attributes and properties

## Development and Testing

### Configuring the test environment

Install

```bash
pip install -Ue .[testing]
```

Create file `.env` with the following content:

```
NOTION_API_TOKEN=<your-notion-token>
DATABASE_ID=<your-database-id>
ROOT_PAGE_ID=<your-page-id>
```

Where:
- `<your-notion-token>` is your Notion API developer's token
  (you will need to create a Notion integration for this: https://www.notion.so/my-integrations);
- `<your-database-id>` is a database that you can use for test purposes
  (with read/write access and a schema corresponding to the model structure
  from `tests/models.py` - Notion's default Reading List will do);
- `<your-page-id>` is the ID of a page where the tests will create new pages.

### Testing

Run the tests:

```bash
pytest tests
```

And always validate typing:

```bash
mypy src/basic_notion
```

Or simply

```bash
make test
```

(it will run all test commands)

## Links

Homepage on GitHub: https://github.com/altvod/basic-notion

Project's page on PyPi: https://pypi.org/project/basic-notion/

Notion API: https://developers.notion.com/
