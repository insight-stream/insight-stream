import sys
import json
from metrics import rag
from typing import Dict, List
from client import ask

def get_metrics(
	data: Dict[str, any]
	):
	answer_relevance = rag.answer_relevance(
		question=data['question'],
		answer=data['summary']
	)
	context_relevance = rag.context_relevance(
		question = data['question'],
        retrieved_passages = [doc['pageContent'] for doc in data['retrived']]
	)
	groundedness = rag.groundedness(
		answer = data['summary'],
        retrieved_passages = [doc['pageContent'] for doc in data['retrived']]
	)
	data.update({
		'AnswerRelevance': answer_relevance,
		'ContextRelevance': context_relevance,
		'Groundedness': groundedness
	})
	return data

def batch_ask(
		bot_id: str,
		questions: List[str]
	) -> List[Dict[str, any]]:
	responces = [
		ask(bot_id, question)
		for question in questions
	]
	return [
		get_metrics(responce)
		for responce in responces
	]


if __name__ == '__main__':
	bot_id = sys.argv[1]
	if len(sys.argv) == 3:
		questions = [sys.argv[2]]
	else:
		questions = [question.strip() for question in sys.stdin.readlines()]

	try:
		data = batch_ask(bot_id, questions)
		if len(questions) == 1:
			data = data[0]
		with open('responce.json', 'w', encoding='utf-8') as f:
			json.dump(data, f)
	except:
		print(f'Произошла ошибка при обращении к боту {bot_id}')