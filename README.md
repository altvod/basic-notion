# basic-notion
Client-agnostic model wrapper for Notion API.

This library does not do any interaction over the network itself,
so it can be used with any existing client that exposes as output
and accepts as input raw JSONable data.

Note that this project is in active development, so major changes
in its structure and API are quite possible in the near future.

## Installation

Just like any other python package out there, it can be installed via `pip`:

```bash
pip install basic-notion
```

## Basic Examples

### Defining Models

All of the examples assume that you put the following code
in a file and name it `models.py`:

```python
from basic_notion.page import NotionPage, NotionPageList
from basic_notion.field import SelectField, TitleField, MultiSelectField


class ReadingListItem(NotionPage):
    type = SelectField(property_name='Type')
    name = TitleField(property_name='Name')
    status = SelectField(property_name='Status')
    authors = MultiSelectField(property_name='Author')


class ReadingList(NotionPageList[ReadingListItem]):
    ITEM_CLS = ReadingListItem
```

All the other examples are using the `notion-client` package
for sending and fetching data.
See the package's [homepage on GitHub](https://github.com/ramnes/notion-sdk-py)

### Fetching a page list from a database

(assuming you put the contents of previous example in `models.py`)

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

### Creating a new page

```python
from notion_client import Client
from models import ReadingListItem

def create_page(client: Client, database_id: str) -> ReadingListItem:
    page = ReadingListItem.make(
        parent={'database_id': database_id},
        type='Book',
        name=['The Best Book Ever'],
        authors=['John Doe'],
    )
    response = client.pages.create(**page.data)
    item = ReadingListItem(data=response)
    # assert len(item.id) == 36
    # assert item.type.name == 'Book'
    # assert item.name.get_text() == 'The Best Book Ever'
    # assert item.authors.get_text() == 'John Doe'
    # assert not item.name[0].bold
    return item
```

### Creating a new database

```python
from notion_client import Client
from basic_notion.database import NotionDatabase
from models import ReadingListItem

def create_database(client: Client, parent_page_id: str) -> NotionDatabase:
    database = NotionDatabase.make(
        title=['My New Shiny Database'],
        parent={'page_id': parent_page_id},
        properties=ReadingListItem.schema,
    )
    response = client.pages.create(**database.data)
    created_database = NotionDatabase(data=response)
    return created_database
```

You can also see the files in `tests/` for more examples
and more thorough usage of the various attributes and properties

## Development and Testing

### Configuring the test environment

Install

```bash
pip install -Ue .[testing]
```

Create file `.env` with the following content:

```
NOTION_API_TOKEN=<your-notion-token>
ROOT_PAGE_ID=<your-page-id>
```

Where:
- `<your-notion-token>` is your Notion API developer's token.
  You will need to create a Notion integration for this:
  visit https://www.notion.so/my-integrations.
- `<your-page-id>` is the ID of a page where the tests will
  create new child pages and databases.
  It must have read/write permissions for your access token.

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
