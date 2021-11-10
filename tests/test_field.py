import abc
from typing import Any, ClassVar, Type, TypeVar

import pytest
from notion_client import Client

from basic_notion.page import NotionPage
from basic_notion.database import NotionDatabase
from basic_notion.property import (
    PageProperty, TitleProperty, NumberProperty, CheckboxProperty,
    EmailProperty, UrlProperty, PhoneNumberProperty,
    SelectProperty, MultiSelectProperty
)
from basic_notion.field import (
    NotionField, TitleField, NumberField, CheckboxField,
    EmailField, UrlField, PhoneNumberField,
    SelectField, MultiSelectField
)

from tests.tools import get_database_from_model


_PROP_TV = TypeVar('_PROP_TV', bound=PageProperty)


@pytest.fixture(scope='session', autouse=True)
def setup_base(sync_client, settings):
    BaseTestField._sync_client = sync_client
    BaseTestField._parent_page_id = settings.root_page_id


class IgnoreCheck(Exception):
    pass


class BaseTestField(abc.ABC):
    FIELD_CLS: ClassVar[Type[NotionField]]

    # Initialized by `setup_base`
    _sync_client: ClassVar[Client]
    _parent_page_id: ClassVar[str]
    _database: ClassVar[NotionDatabase]

    @classmethod
    def get_database(cls, model: Type[NotionPage]) -> NotionDatabase:
        return get_database_from_model(
            sync_client=cls._sync_client,
            model=model,
            parent_page_id=cls._parent_page_id,
        )

    @abc.abstractmethod
    def make_value(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def check_property(self, prop: PageProperty) -> None:
        raise NotImplementedError

    def update_property(self, prop) -> None:
        raise IgnoreCheck()

    def check_updated_property(self, prop: PageProperty) -> None:
        pass

    def test_property(self):
        Model: Type[NotionPage]
        if self.FIELD_CLS is TitleField:
            # Two title fields in one model are not allowed
            class Model(NotionPage):
                prop = self.FIELD_CLS()
        else:
            class Model(NotionPage):
                title = TitleField()
                prop = self.FIELD_CLS()

        database = self.get_database(model=Model)

        page = Model.make(
            parent=database.as_parent(),
            title=['The Title'],  # will be ignored if field doesn't exist
            prop=self.make_value(),
        )
        data = self._sync_client.pages.create(**page.data)
        page = Model(data=data)
        self.check_property(page.prop)

        try:
            self.update_property(page.prop)
        except IgnoreCheck:
            return

        data = self._sync_client.pages.update(page_id=page.id, **page.data)
        page = Model(data=data)
        self.check_updated_property(page.prop)


class TestNumberField(BaseTestField):
    FIELD_CLS = NumberField

    def make_value(self) -> Any:
        return 123

    def check_property(self, prop: NumberProperty) -> None:
        assert prop.number == 123
        assert prop.get_text() == '123'

    def update_property(self, prop: NumberProperty) -> None:
        prop.number = 456.789

    def check_updated_property(self, prop: NumberProperty) -> None:
        assert prop.number == 456.789


class TestCheckboxField(BaseTestField):
    FIELD_CLS = CheckboxField

    def make_value(self) -> Any:
        return True

    def check_property(self, prop: CheckboxProperty) -> None:
        assert prop.checkbox

    def update_property(self, prop: CheckboxProperty) -> None:
        prop.checkbox = False

    def check_updated_property(self, prop: CheckboxProperty) -> None:
        assert not prop.checkbox


class TestTitleField(BaseTestField):
    FIELD_CLS = TitleField

    def make_value(self) -> Any:
        return ['My Text']

    def check_property(self, prop: TitleProperty) -> None:
        assert prop.items[0].content == 'My Text'
        assert prop.items[0].plain_text == 'My Text'
        assert not prop.items[0].bold
        assert not prop.items[0].strikethrough
        assert prop.get_text() == 'My Text'

    def update_property(self, prop: TitleProperty) -> Any:
        prop.items[0].bold = True
        prop.items[0].strikethrough = True

    def check_updated_property(self, prop: TitleProperty) -> None:
        assert prop.items[0].content == 'My Text'
        assert prop.items[0].plain_text == 'My Text'
        assert prop.items[0].bold
        assert prop.items[0].strikethrough


class TestUrlField(BaseTestField):
    FIELD_CLS = UrlField

    def make_value(self) -> Any:
        return 'http://www.google.com'

    def check_property(self, prop: UrlProperty) -> None:
        assert prop.url == 'http://www.google.com'
        assert prop.get_text() == 'http://www.google.com'

    def update_property(self, prop: UrlProperty) -> Any:
        prop.url = 'http://www.yahoo.com'

    def check_updated_property(self, prop: UrlProperty) -> None:
        assert prop.url == 'http://www.yahoo.com'


class TestEmailField(BaseTestField):
    FIELD_CLS = EmailField

    def make_value(self) -> Any:
        return 'my@email.com'

    def check_property(self, prop: EmailProperty) -> None:
        assert prop.email == 'my@email.com'
        assert prop.get_text() == 'my@email.com'

    def update_property(self, prop: EmailProperty) -> Any:
        prop.email = 'your@email.com'

    def check_updated_property(self, prop: EmailProperty) -> None:
        assert prop.email == 'your@email.com'


class TestPhoneNumberField(BaseTestField):
    FIELD_CLS = PhoneNumberField

    def make_value(self) -> Any:
        return '+1234567890'

    def check_property(self, prop: PhoneNumberProperty) -> None:
        assert prop.phone_number == '+1234567890'
        assert prop.get_text() == '+1234567890'

    def update_property(self, prop: PhoneNumberProperty) -> Any:
        prop.phone_number = '+0987654321'

    def check_updated_property(self, prop: PhoneNumberProperty) -> None:
        assert prop.phone_number == '+0987654321'


class TestSelectField(BaseTestField):
    FIELD_CLS = SelectField

    def make_value(self) -> Any:
        return 'Book'

    def check_property(self, prop: SelectProperty) -> None:
        assert prop.name == 'Book'
        assert prop.option_id
        self._old_option_id = prop.option_id
        assert prop.color
        assert prop.get_text() == 'Book'

    def update_property(self, prop: SelectProperty) -> Any:
        prop.name = 'Article'

    def check_updated_property(self, prop: SelectProperty) -> None:
        assert prop.name == 'Article'
        assert prop.option_id != self._old_option_id


class TestMultiSelectField(BaseTestField):
    FIELD_CLS = MultiSelectField

    def make_value(self) -> Any:
        return ['June', 'October']

    def check_property(self, prop: MultiSelectProperty) -> None:
        assert [item.name for item in prop.items] == ['June', 'October']
        assert all([item.id for item in prop.items])
        self._old_option_ids = set([item.option_id for item in prop.items])
        assert all([item.color for item in prop.items])
        assert prop.get_text() == 'June, October'

    def update_property(self, prop: MultiSelectProperty) -> Any:
        return prop.set_names(['December', 'May', 'November'])

    def check_updated_property(self, prop: MultiSelectProperty) -> None:
        assert [item.name for item in prop.items] == ['December', 'May', 'November']
