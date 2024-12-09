import asyncpraw
from abc import ABC, abstractmethod
from asyncpraw import Reddit

class AbstractCommand(ABC):
    def __init__(self, reddit: Reddit, sub_name:str, bot_name: str):
        self.reddit = reddit
        self.sub_name = sub_name
        self.bot_name = bot_name
        self._next_handler = None

    async def comment(self, comment: asyncpraw.models.Comment):
        handled = await self.handle_comment(comment)
        if not handled and self._next_handler:
            await self._next_handler.comment(comment)
    
    @abstractmethod
    async def handle_comment(self, comment: asyncpraw.models.Comment) -> bool:
        return False

    def __call__(self, new_handler):
        next_handler = self
        while next_handler._next_handler is not None:
            next_handler = next_handler._next_handler
            pass
        next_handler._next_handler = new_handler
        return self