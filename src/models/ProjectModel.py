from .BaseDataModel import BaseDataModel
from .db_schemes.project import Project

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection_name = "projects"
        self.collection = self.db_client[self.app_settings.MONGODB_NAME][self.collection_name]
        
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
        
        if (num_of_pages * page_size) // page_size != 0:
            total_pages_num += 1
            
        skip = (page_number - 1) * page_size
        cursor = self.collection.find().skip(skip).limit(page_size)
        
        projects = await cursor.to_list(length=page_size)
        
        return [Project(**project) for project in projects], total_pages_num
    