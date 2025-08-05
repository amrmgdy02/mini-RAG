from .BaseDataModel import BaseDataModel
from .db_schemes.DataChunk import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne

class DataChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection_name = "data_chunks"
        self.collection = self.db_client[self.app_settings.MONGODB_NAME][self.collection_name]
        
    async def get_chunk_by_id(self, chunk_id: str):
        """
        Retrieve a DataChunk by its ID.
        """
        chunk_doc = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if chunk_doc:
            return DataChunk(**chunk_doc)
        return None
    
    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int=100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)
        
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count