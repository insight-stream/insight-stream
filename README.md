# python_client
Питон клиент для проекта insight-stream

В файл .env занести следующие значения:   
QDRANT_KEY=...   
QDRANT_URL=https://...qdrant.io:6333   
QDRANT_VECTOR_SIZE=...
OPENAI_API_KEY=sk-...    
OPENAI_API_BASE=...   
EMBED_MODEL=...   
SERVER_NAME=https://...   
TOKEN=...   

# Установка   
pip install -e /полный/путь/к/папке/python_client    

# Использование:   
from insight_stream.client import delete_documents, upload_dir, ask, upload_doc

Файлы будут сохранятся на сервере <SERVER_NAME>   
в папку /media/documents/<file_name>   
с помощью POST <SERVER_NAME>/documents/<file_name>   

И после сохранения будут доступны по следующему URL:   
<SERVER_NAME>/documents/<file_name>   
