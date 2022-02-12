import abc
from typing import ClassVar, Type

from basic_notion.block import (
    NotionBlock, ParagraphBlock,
    Heading1Block, Heading2Block, Heading3Block,
    CalloutBlock, BulletedListItemBlock, NumberedListItemBlock,
    ToDoBlock, ToggleBlock, CodeBlock,
    ChildPageBlock, ChildDatabaseBlock,
)


def test_nested_blocks(sync_client, titled_page):
    page = titled_page

    children_data = sync_client.blocks.children.append(
        **ParagraphBlock.make_as_children_data(
            block_id=page.id,
            text=['Parent block'],
        )
    )
    block_data = children_data['results'][0]
    parent_block = ParagraphBlock(data=block_data)

    nested_children_data = sync_client.blocks.children.append(
        **ParagraphBlock.make_as_children_data(
            block_id=parent_block.id,
            text=['Nested block'],
        )
    )
    nested_block_data = nested_children_data['results'][0]
    nested_block = ParagraphBlock(data=nested_block_data)

    loaded_parent_block_data = sync_client.blocks.retrieve(block_id=parent_block.id)
    loaded_parent_block = ParagraphBlock(data=loaded_parent_block_data)
    assert parent_block.id == loaded_parent_block.id

    loaded_parent_children_data = sync_client.blocks.children.list(block_id=parent_block.id)
    loaded_nested_block_data = loaded_parent_children_data['results'][0]
    loaded_nested_block = ParagraphBlock(data=loaded_nested_block_data)
    assert loaded_nested_block.id == nested_block.id


class BaseTestBlock(abc.ABC):
    BLOCK_CLS: ClassVar[Type[NotionBlock]]

    @abc.abstractmethod
    def make_block_data(self) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def check_block(self, block: NotionBlock) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def update_block(self, block: NotionBlock) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def check_updated_block(self, block: NotionBlock) -> None:
        raise NotImplementedError

    def test_block(self, sync_client, titled_page):
        page = titled_page

        # Create and check block
        raw_block_data = self.BLOCK_CLS.make_as_children_data(
            block_id=page.id,
            **self.make_block_data(),
        )
        children_data = sync_client.blocks.children.append(**raw_block_data)
        block_data = children_data['results'][0]
        block = self.BLOCK_CLS(data=block_data)
        self.check_block(block)

        # Update it and check again
        self.update_block(block)
        block_data = sync_client.blocks.update(block_id=block.id, **block.data)
        block = self.BLOCK_CLS(data=block_data)
        self.check_updated_block(block)

        # Delete it
        block.archived = True
        block_data = sync_client.blocks.update(block_id=block.id, **block.data)
        block = self.BLOCK_CLS(data=block_data)
        assert block.archived is True


class BaseTestTextBasedBlock(BaseTestBlock):
    def make_block_data(self) -> dict:
        return dict(
            text=['Old text'],
        )

    def check_block(self, block: NotionBlock) -> None:
        assert block.text.get_text() == 'Old text'

    def update_block(self, block: NotionBlock) -> None:
        block.text = 'New text'

    def check_updated_block(self, block: NotionBlock) -> None:
        assert block.text.get_text() == 'New text'


class TestParagraphBlock(BaseTestTextBasedBlock):
    BLOCK_CLS = ParagraphBlock


class TestHeading1Block(BaseTestTextBasedBlock):
    BLOCK_CLS = Heading1Block


class TestHeading2Block(BaseTestTextBasedBlock):
    BLOCK_CLS = Heading2Block


class TestHeading3Block(BaseTestTextBasedBlock):
    BLOCK_CLS = Heading3Block


class TestCalloutBlock(BaseTestTextBasedBlock):
    BLOCK_CLS = CalloutBlock


class TestBulletedListItemBlock(BaseTestTextBasedBlock):
    BLOCK_CLS = BulletedListItemBlock


class TestNumberedListItemBlock(BaseTestTextBasedBlock):
    BLOCK_CLS = NumberedListItemBlock


class TestToggleBlock(BaseTestTextBasedBlock):
    BLOCK_CLS = ToggleBlock


class TestToDoBlock(BaseTestTextBasedBlock):
    BLOCK_CLS = ToDoBlock

    def make_block_data(self) -> dict:
        return dict(
            text=['Old text'],
            checked=False,
        )

    def check_block(self, block: ToDoBlock) -> None:
        assert block.text.get_text() == 'Old text'
        assert block.checked is False

    def update_block(self, block: ToDoBlock) -> None:
        block.text = 'New text'
        block.checked = True

    def check_updated_block(self, block: ToDoBlock) -> None:
        assert block.text.get_text() == 'New text'
        assert block.checked is True


class TestCodeBlock(BaseTestTextBasedBlock):
    BLOCK_CLS = CodeBlock

    def make_block_data(self) -> dict:
        return dict(
            text=['Old text'],
            language='python',
        )

    def check_block(self, block: CodeBlock) -> None:
        assert block.text.get_text() == 'Old text'
        assert block.language == 'python'

    def update_block(self, block: CodeBlock) -> None:
        block.text = 'New text'
        block.language = 'html'

    def check_updated_block(self, block: CodeBlock) -> None:
        assert block.text.get_text() == 'New text'
        assert block.language == 'html'


class ChildPageBlockBlock(BaseTestBlock):
    BLOCK_CLS = ChildPageBlock

    def make_block_data(self) -> dict:
        return dict(
            title='Old text',
        )

    def check_block(self, block: ChildPageBlock) -> None:
        assert block.title == 'Old text'

    def update_block(self, block: ChildPageBlock) -> None:
        block.title = 'New text'

    def check_updated_block(self, block: ChildPageBlock) -> None:
        assert block.title == 'New text'
