import abc
from typing import ClassVar, Type

from basic_notion.block import NotionBlock, ParagraphBlock


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


class TestBlockParagraph(BaseTestBlock):
    BLOCK_CLS = ParagraphBlock

    def make_block_data(self) -> dict:
        return dict(
            text=['Block text'],
        )

    def check_block(self, block: ParagraphBlock) -> None:
        assert block.text.get_text() == 'Block text'

    def update_block(self, block: ParagraphBlock) -> None:
        block.text = 'New text'

    def check_updated_block(self, block: ParagraphBlock) -> None:
        assert block.text.get_text() == 'New text'
