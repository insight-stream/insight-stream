from langchain_core.embeddings import Embeddings
from typing import List
import requests


class СustomEmbeddings(Embeddings):
    """Получение эмбедингов с помощью post запросов на base_url. Перед использованием установить корректные значения base_url и model"""
    model: str = 'model_name'
    base_url: str = 'https://some-server/v1/embeddings'
    
	#TODO: нужна проверка на корректную длинну текста для запроса

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            embedding = self.embed_query(text)
            embeddings.append(embedding)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "input": text
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        if response.status_code == 200:
            answ_data = response.json()            
            embeddings = answ_data["data"][0]["embedding"]
            return embeddings
        else:
            print(f"Ошибка получения эмбединга {response.status_code}")
            return []

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            embedding = await self.aembed_query(text)
            embeddings.append(embedding)
        return embeddings

    async def aembed_query(self, text: str) -> List[float]:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "input": text
        }
        response = await requests.post(self.base_url, headers=headers, json=data)
        if response.status_code == 200:
            answ_data = response.json()
            embeddings = answ_data["data"][0]["embedding"]
            return embeddings
        else:
            print(f"Ошибка получения эмбединга {response.status_code}")
            return []