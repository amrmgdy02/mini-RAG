from .BaseDataModel import BaseDataModel
from .db_schemes.project import Project
import logging

logger = logging.getLogger('uvicorn.error')

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection_name = "projects"
        self.db_client = db_client
        self.collection = self.db_client[self.app_settings.MONGODB_NAME][self.collection_name]
        
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collection_names = await self.db_client[self.app_settings.MONGODB_NAME].list_collection_names()
        logger.info(f"Existing collections: {all_collection_names}")
        
        # create index only when creating the collection first time
        if "projects" not in all_collection_names:
            logger.info("Projects collection doesn't exist - creating indexes")
            indexes = Project.get_indexes()
            logger.info(f"Indexes to create: {indexes}")
            
            for index in indexes:
                logger.info(f"Creating index: {index['name']}")
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )
                logger.info(f"Successfully created index: {index['name']}")
        else:
            logger.info("Projects collection exists - skipping index creation")
    
    async def get_collection_indexes(self):
        """Get all indexes for the projects collection"""
        try:
            indexes = await self.collection.list_indexes().to_list(None)
            return indexes
        except Exception as e:
            logger.error(f"Error getting indexes: {e}")
            return []
        
    async def create_project(self, project: Project):
        # Use by_alias=True to convert 'id' to '_id' for MongoDB
        project_data = project.model_dump(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(project_data)
        project.id = result.inserted_id
        return project
    
    async def find_project_or_create_one(self, project_id: str, description: str = None):
        project_doc = await self.collection.find_one({"project_id": project_id})
        
        if not project_doc:
            new_project = Project(
                project_id=project_id,
                description=description
            )
            return await self.create_project(new_project)
        
        # MongoDB returns '_id', populate_by_name allows Pydantic to accept it
        return Project(**project_doc)
    
    async def get_all_projects(self, page_number: int = 1, page_size: int = 10):
        
        num_of_pages = await self.collection.count_documents({})
        total_pages_num = (num_of_pages * page_size) // page_size
        
        if (num_of_pages * page_size) % page_size != 0:
            total_pages_num = total_pages_num + 1
            
        skip = (page_number - 1) * page_size
        cursor = self.collection.find().skip(skip).limit(page_size)
        
        projects = await cursor.to_list(length=page_size)
        
        return [Project(**project) for project in projects], total_pages_num
    