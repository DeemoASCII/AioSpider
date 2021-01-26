from typing import Optional

import pymongo
from motor import motor_asyncio

Mongo = 1


class Pipeline:
    broken_type: Optional[int] = 0
    broken_url: Optional[str] = 'mongodb://localhost:27017'

    def __init__(self, db=None, loop=None, *args, **kwargs):
        if self.broken_type == Mongo:
            self.db = motor_asyncio.AsyncIOMotorClient(self.broken_url, io_loop=loop)
            self.database = db

    async def mongo_insert(self, doc: dict):
        try:
            await self.db[self.database][self.database].insert_one(doc)
        except pymongo.errors.DuplicateKeyError:
            pass
        except Exception as e:
            raise e
