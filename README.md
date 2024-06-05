# insight_stream python client
Питон клиент для проекта insight stream

В файл .env занести следующие значения:   
QDRANT_KEY=...   
QDRANT_URL=https://...qdrant.io:6333   
QDRANT_VECTOR_SIZE=...   

OPENAI_API_KEY=sk-...    
OPENAI_API_BASE=...   
EMBED_MODEL=...   
ENCODING_FORMAT=...  
TIKTOKEN_MODEL=...   
TIKTOKEN_ENABLED=...   

SERVER_NAME=https://...   
TOKEN=...   


Для OpenAI файл .env должен выглядеть так:   
QDRANT_KEY=...   
QDRANT_URL=https://...qdrant.io:6333   
QDRANT_VECTOR_SIZE=1536   (значение зафисит от выбранной модели EMBED_MODEL)   

OPENAI_API_KEY=sk-...    
OPENAI_API_BASE=https://api.openai.com/v1   
EMBED_MODEL=text-embedding-ada-002  
ENCODING_FORMAT=float   
TIKTOKEN_ENABLED=True   

SERVER_NAME=https://...   
TOKEN=...   

Значение TIKTOKEN_MODEL не устанавливается.   


# Установка   
pip install git+https://github.com/insight-stream/insight_stream.git    

# Использование:   
from insight_stream.client import delete_documents, upload_dir, ask, upload_doc

Файлы будут сохранятся на сервере <SERVER_NAME>   
с помощью POST <SERVER_NAME>/documents/<file_name>   

И после сохранения будут доступны по следующему URL:   
<SERVER_NAME>/documents/<file_name>   
