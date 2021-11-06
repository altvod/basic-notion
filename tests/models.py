from basic_notion.page import NotionPageList, NotionPage
from basic_notion.field import SelectField, TitleField, MultiSelectField


class ReadingListItem(NotionPage):
    type: SelectField = SelectField(property_name='Type')
    name: TitleField = TitleField(property_name='Name')
    status: SelectField = SelectField(property_name='Status')
    authors: MultiSelectField = MultiSelectField(property_name='Author')


class ReadingList(NotionPageList[ReadingListItem]):
    _ITEM_CLS = ReadingListItem
