from basic_notion.page import NotionPage
from basic_notion.field import TitleField


class TitledPage(NotionPage):
    title: TitleField = TitleField()
