import dialogflow


def make_text_input(text, lang_code):
	assert isinstance(lang_code, str)
	return dialogflow.types.TextInput(text=str(text), language_code=lang_code)


def make_query_input(text_input):
	assert isinstance(text_input, dialogflow.types.TextInput)
	return dialogflow.types.QueryInput(text=text_input)
