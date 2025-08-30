from celery import Celery
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from stores.llms.LLMFactory import LLMFactory
from stores.VectorDB.VectorDBFactory import VectorDBFactory

settings = get_settings()

async def get_setup():
    mongodb_client = AsyncIOMotorClient(settings.MONGO_URL)
    mongodb_connection = mongodb_client[settings.MONGODB_NAME]
    
    LLM_factory = LLMFactory(config=settings)
    generation_llm = LLM_factory.create(settings.LLM_PROVIDER)
    embedding_llm = LLM_factory.create(settings.LLM_PROVIDER)

    generation_llm.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    embedding_llm.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_SIZE)
    
    vectordb_factory = VectorDBFactory(settings)
    vector_db_client = vectordb_factory.create("QDRANT")
    vector_db_client.init_connection()
    
    return (
        mongodb_client,
        mongodb_connection,
        generation_llm,
        embedding_llm,
        vector_db_client
    )

celery_app = Celery(
    "minirag",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
     include=[
         "tasks.file_processing",
    #     "tasks.data_indexing",
    #     "tasks.process_workflow",
    #     "tasks.maintenance",
     ]
)

celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=[
        settings.CELERY_TASK_SERIALIZER
    ],

    task_acks_late=settings.CELERY_TASK_ACKS_LATE,

    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,

    task_ignore_result=False,
    result_expires=3600,

    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,

    # Connection settings for better reliability
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    worker_cancel_long_running_tasks_on_connection_loss=True,

     task_routes={
         "tasks.file_processing.chunk_file": {"queue": "file_processing"},
         "tasks.file_processing.embed_chunks": {"queue": "file_processing"},
    #     "tasks.data_indexing.index_data_content": {"queue": "data_indexing"},
    #     "tasks.process_workflow.process_and_push_workflow": {"queue": "file_processing"},
    #     "tasks.maintenance.clean_celery_executions_table": {"queue": "default"},
     },

    # beat_schedule={
    #     'cleanup-old-task-records': {
    #         'task': "tasks.maintenance.clean_celery_executions_table",
    #         'schedule': 10,
    #         'args': ()
    #     }
    # },

    timezone='UTC',

)

celery_app.conf.task_default_queue = "default"