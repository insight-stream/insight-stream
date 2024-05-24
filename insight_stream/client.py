from typing import Dict, List, Optional
import json
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.qdrant import Qdrant
from qdrant_client import QdrantClient, models
from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import TokenTextSplitter
import requests
import urllib.parse

TOKEN = os.getenv('TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_KEY = os.getenv('QDRANT_KEY')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE')
SERVER_NAME = os.getenv('SERVER_NAME')

embedding = OpenAIEmbeddings(model='text-embedding-ada-002', 
							 api_key=OPENAI_API_KEY, 
							 openai_api_base=OPENAI_API_BASE)
clientQdrant=QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)

def ask(
		bot_id: str,
		question: str
	) -> Optional[Dict[str, any]]:
	""""Получение ответа бота на вопрос пользователя"""
	
	request = requests.post(
		f'https://{SERVER_NAME}/v.1.0/{bot_id}', 
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
	
def _add_documents(index_id: str, documents: List[Document], file_path: str = 'file') -> List[Document]: #значения по умолчанию для folder_name и file_path
	"""Добавляем в квадрант документы, являющиеся чанками для одного файла из папки"""
	try:
		clientQdrant.create_collection(
				collection_name=index_id,
				vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE)
			)
	except:
		pass
	qdrant = Qdrant(client=clientQdrant, collection_name=index_id, embeddings=embedding)

	docs_for_qdrant = []
	for doc in documents:
		new_doc = Document(page_content=doc.page_content, metadata = {
			"topic": os.path.splitext(os.path.basename(file_path))[0], 
			"url": urllib.parse.quote(f'https://{SERVER_NAME}/documents/{os.path.basename(file_path)}', safe=":/")})
		docs_for_qdrant.append(new_doc)

	qdrant.add_documents(docs_for_qdrant)
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


def upload_doc(index_id: str, path: str):
	"""Загрузка документов в индекс квадранта и на сервер"""

	loader = UnstructuredFileLoader(path)

	token_text_splitter = TokenTextSplitter(         
		model_name='gpt-3.5-turbo',
		chunk_size = 512, 
		chunk_overlap = 50
	)

	chunks = loader.load_and_split(text_splitter=token_text_splitter)

	#загрузка чанков документа в квадрант
	docs = _add_documents(index_id, chunks, path)
	print(f"Документы загружены в квадрант, index_id {index_id}")

	#загрузка файла на сервер
	url = _load_file_to_server(path)
	
	return docs

def upload_dir(index_id: str, path: str):
	"""Множественная загрузка документов в индекс квадранта и на  сервер"""

	#загрузка файлов на сервер
	urls = _load_dir_to_server(path)

	for file in os.listdir(path):
		file_path = os.path.join(path, file)
		if os.path.isfile(file_path):
			chunks = upload_doc(index_id, file_path)
			yield from chunks

def _load_file_to_server(file_path: str) -> str:
	"""Добавление файла на сервера"""

	url = f"https://{SERVER_NAME}/documents/{os.path.basename(file_path)}"
	file_url = urllib.parse.quote(url, safe=":/")

	headers = {'Authorization': f'Bearer {TOKEN}'}
	files = {'file': open(file_path, 'rb')}
    
	response = requests.put(url, headers=headers, files=files)
    
	if response.status_code == 201:
		print(f"Успешно загружен файл {os.path.basename(file_path)}!")
		return file_url
	else:
		print("Загрузка не удалась")
		return ''
	
def _del_file_from_server(url: str):
	"""Удаление файла с сервера"""

	headers = {'Authorization': f'Bearer {TOKEN}'}
	response = requests.delete(url, headers=headers)
    
	if response.status_code == 204:
		print(f"Успешно удален файл {url}!")
	else:
		print("Ошибка при удалении")
	

def _load_dir_to_server(path: str) -> List[str]:
	"""Множественная загрузка файлов на сервер"""

	urls = []
    
	if os.path.isfile(path):
		urls.append(_load_file_to_server(path))
	elif os.path.isdir(path):
		for file in os.listdir(path):
			file_path = os.path.join(path, file)
			if os.path.isfile(file_path):
				urls.append(_load_file_to_server(file_path))
    
	return urls