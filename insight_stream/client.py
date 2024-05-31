from typing import Dict, List, Optional
import json
import os
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient, models
from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredFileLoader
import requests
import urllib.parse
import socket

OPENAI_BASE = os.getenv('OPENAI_BASE')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBED_MODEL = os.getenv('EMBED_MODEL')
ENCODING_FORMAT = os.getenv('ENCODING_FORMAT')
TIKTOKEN_MODEL = os.getenv('TIKTOKEN_MODEL')
TIKTOKEN_ENABLED = bool(os.getenv('TIKTOKEN_ENABLED'))


QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_KEY = os.getenv('QDRANT_KEY')
QDRANT_VECTOR_SIZE = int(os.getenv('QDRANT_VECTOR_SIZE', 1536))

SERVER_NAME = os.getenv('SERVER_NAME')
TOKEN = os.getenv('TOKEN')

embeddings = OpenAIEmbeddings(model=EMBED_MODEL,
                              openai_api_base=OPENAI_BASE,
                              openai_api_key=OPENAI_API_KEY,
                              model_kwargs={"encoding_format": ENCODING_FORMAT},
                              tiktoken_enabled=TIKTOKEN_ENABLED,
                              tiktoken_model_name=TIKTOKEN_MODEL,
                              )

clientQdrant=QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)

def ask(
		bot_id: str,
		question: str
	) -> Optional[Dict[str, any]]:
	""""Получение ответа бота на вопрос пользователя"""
	request = requests.post(
		f'{SERVER_NAME}/v.1.0/{bot_id}',
		data=json.dumps({ "question": question }),
		headers={
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {TOKEN}'
		}
	)
	if request.status_code == 200:
		return request.json()
	else:
		return None
	
def _add_documents(index_id: str, documents: List[Document], file_path: str) -> List[Document]:
	"""Добавляем в квадрант документы, являющиеся чанками для одного файла из папки"""
	try:
		clientQdrant.create_collection(
				collection_name=index_id,
				vectors_config=models.VectorParams(size=QDRANT_VECTOR_SIZE, distance=models.Distance.COSINE)
			)
	except:
		pass
	qdrant = Qdrant(client=clientQdrant, collection_name=index_id, embeddings=embedding)

	docs_for_qdrant = []
	for doc in documents:
		new_doc = Document(page_content=doc.page_content, metadata = {
			"topic": os.path.splitext(os.path.basename(file_path))[0], 
			"url": urllib.parse.quote(f'{SERVER_NAME}/documents/{os.path.basename(file_path)}', safe=":/")})
		docs_for_qdrant.append(new_doc)
		
	try:
		qdrant.add_documents(docs_for_qdrant)
	except Exception as e:
		print(e)
	return docs_for_qdrant


def delete_documents(index_id: str, documents: List[Document]):
	"""Удаление документов с сервера и из коллекции квадранта"""

	#удаление коллекции целиком
	clientQdrant.delete_collection(collection_name=index_id)

	#удаление соотвестующих документов на сервере
	urls_for_del = []
	for doc in documents:
		url = doc.metadata.get("url")
		if url and url not in urls_for_del:
			urls_for_del.append(url)

	for url in urls_for_del:
		_del_file_from_server(url)


def upload_doc(index_id: str, path: str) -> List[Document]:
	"""Загрузка документов в индекс квадранта и на сервер"""

	loader = UnstructuredFileLoader(path)
	chunks = loader.load_and_split()

	#загрузка чанков документа в квадрант
	docs = _add_documents(index_id, chunks, path)
	print(f"Файл {os.path.basename(path)} загружен в квадрант, index_id {index_id}")

	#загрузка файла на сервер
	url = _load_file_to_server(path)
	
	return docs

def upload_dir(index_id: str, path: str) -> List[Document]:
	"""Множественная загрузка документов в индекс квадранта и на сервер"""

	docs = []

	for file in os.listdir(path):
		file_path = os.path.join(path, file)
		if os.path.isfile(file_path):
			chunks = upload_doc(index_id, file_path)
			docs.extend(chunks)

	return docs

def _check_server_availability() -> bool:
	"Проверка доступности сервера"

	server_url = urllib.parse.urlparse(SERVER_NAME)
	host = server_url.hostname
	port = server_url.port
	try:
		socket.create_connection((host, port), timeout=5)
		return True
	except socket.error:
		return False

def _load_file_to_server(file_path: str) -> str:
	"""Добавление файла на сервера"""

	if not _check_server_availability():
		print("Сервер для загрузки документов недоступен")
		return ''

	url = f"{SERVER_NAME}/documents/{os.path.basename(file_path)}"
	file_url = urllib.parse.quote(url, safe=":/")

	headers = {'Authorization': f'Bearer {TOKEN}'}
	files = {'file': open(file_path, 'rb')}
    
	response = requests.put(url, headers=headers, files=files)
    
	if response.status_code == 201:
		print(f"Успешно загружен файл {os.path.basename(file_path)} на сервер!")
		return file_url
	else:
		print(f"Загрузка файла {os.path.basename(file_path)} на сервер не удалась")
		return ''
	
def _del_file_from_server(url: str):
	"""Удаление файла с сервера"""

	if not _check_server_availability():
		print("Сервер недоступен")
		return ''

	headers = {'Authorization': f'Bearer {TOKEN}'}
	response = requests.delete(url, headers=headers)
    
	if response.status_code == 204:
		print(f"Успешно удален файл {url}!")
	else:
		print("Ошибка при удалении")
