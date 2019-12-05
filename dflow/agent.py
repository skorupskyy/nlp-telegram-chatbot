import uuid
import requests

import dialogflow

from dflow import helpers
from app.settings import DIALOGFLOW_DEV_TOKEN


# Agent is a wrapper for DialogFlow API.
class Agent:
	
	def __init__(self, project_id, lang_code, client):
		assert isinstance(project_id, str)
		self.project_id = project_id
		
		assert isinstance(lang_code, str)
		self.lang_code = lang_code
		
		self.session_id = uuid.uuid4()
		
		assert isinstance(client, dialogflow.SessionsClient)
		self.client = client
		
		self.session = self.client.session_path(self.project_id, self.session_id)
	
	def __str__(self):
		return '<Agent: id={}>'.format(self.session_id)
	
	def __repr__(self):
		return str(self)
	
	def detect_intent(self, text_to_analyze):
		response = self.client.detect_intent(
			session=self.session,
			query_input=helpers.make_query_input(
				text_input=helpers.make_text_input(text_to_analyze, self.lang_code)
			)
		)
		fields = dict(response.query_result.parameters.fields)
		parameters = {}
		for p_key, p_value in fields.items():
			if len(p_value.string_value) > 0:
				parameters[p_key] = p_value.string_value
			else:
				parameters[p_key] = [actual_val.string_value for actual_val in p_value.list_value.values]
		return {
			'query_text': response.query_result.query_text,
			'name': response.query_result.intent.display_name,
			'fulfillment_text': response.query_result.fulfillment_text,
			'parameters': parameters
		}


def get_sessions_client():
	return dialogflow.SessionsClient()


# !ATTENTION! Manual use only!!! #TODO
def configure_crypto_currency_entity():
	url = 'https://api.dialogflow.com/v1'
	headers = {
		'Authorization': 'Bearer {}'.format(DIALOGFLOW_DEV_TOKEN),
		'Content-Type': 'application/json'
	}
	resp = requests.get(url + '/entities', headers=headers)
	entity_id = resp.json()[0]['id']

	resp = requests.post(url + '/entities/' + entity_id + '/entries', headers=headers, json=[
		{
			'synonyms': ['Tether', 'USDT', 'usdt', 'Usdt', 'tether'],
			'value': 'Tether'
		},
	])
	print(resp.json())


# TODO: temporary driver program!
if __name__ == '__main__':
	pass
	# configure_crypto_currency_entity()
	# from app.settings import DIALOGFLOW_PROJECT_ID, DIALOGFLOW_LANGUAGE_CODE
	# a = Agent(DIALOGFLOW_PROJECT_ID, DIALOGFLOW_LANGUAGE_CODE, get_sessions_client())
	# result = a.detect_intent('list Bitcoin, Ethereum and Tron to EUR')
	# print()
