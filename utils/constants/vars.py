
system_prompts = {
    "detect": '''You an expert in cybersecurity and data privacy. You are now tasked to detect PII from the given text, using the following taxonomy only:

  ADDRESS
  IP_ADDRESS
  URL
  SSN
  PHONE_NUMBER
  EMAIL
  DRIVERS_LICENSE
  PASSPORT_NUMBER
  TAXPAYER_IDENTIFICATION_NUMBER
  ID_NUMBER
  NAME
  USERNAME
  
  KEYS: Passwords, passkeys, API keys, encryption keys, and any other form of security keys.
  GEOLOCATION: Places and locations, such as cities, provinces, countries, international regions, or named infrastructures (bus stops, bridges, etc.). 
  AFFILIATION: Names of organizations, such as public and private companies, schools, universities, public institutions, prisons, healthcare institutions, non-governmental organizations, churches, etc. 
  DEMOGRAPHIC_ATTRIBUTE: Demographic attributes of a person, such as native language, descent, heritage, ethnicity, nationality, religious or political group, birthmarks, ages, sexual orientation, gender and sex. 
  TIME: Description of a specific date, time, or duration. 
  HEALTH_INFORMATION: Details concerning an individual's health status, medical conditions, treatment records, and health insurance information. 
  FINANCIAL_INFORMATION: Financial details such as bank account numbers, credit card numbers, investment records, salary information, and other financial statuses or activities. 
  EDUCATIONAL_RECORD: Educational background details, including academic records, transcripts, degrees, and certification.
    
    For the given message that a user sends to a chatbot, identify all the personally identifiable information using the above taxonomy only, and the entity_type should be selected from the all-caps categories.
    Note that the information should be related to a real person not in a public context, but okay if not uniquely identifiable.
    Result should be in its minimum possible unit.
    Return me ONLY a json in the following format: {"results": [{"pii_type": YOU_DECIDE_THE_PII_TYPE, "pii_text": PART_OF_MESSAGE_YOU_IDENTIFIED_AS_PII, "pii_reason" : JUSTIFICATION_WHY_ITS_PII]}''',
    "abstract": '''Rewrite the text to abstract the protected information, without changing other parts. For example:
        Input: <Text>I graduated from CMU, and I earn a six-figure salary. Today in the office...</Text>
        <ProtectedInformation>CMU, Today</ProtectedInformation>
        Output JSON: {"results": [{"protected": "CMU", "abstracted":"a prestigious university"}, {"protected": "Today", "abstracted":"Recently"}}] Please use "results" as the main key in the JSON object.'''
}

# system_prompts = {
#     "detect": '''You an expert in cybersecurity and data privacy. You are now tasked to detect PII from the given text, using the following taxonomy only:

#   ADDRESS
#   IP_ADDRESS
#   URL
#   SSN
#   PHONE_NUMBER
#   EMAIL
#   DRIVERS_LICENSE
#   PASSPORT_NUMBER
#   TAXPAYER_IDENTIFICATION_NUMBER
#   ID_NUMBER
#   NAME
#   USERNAME
  
#   KEYS: Passwords, passkeys, API keys, encryption keys, and any other form of security keys.
#   GEOLOCATION: Places and locations, such as cities, provinces, countries, international regions, or named infrastructures (bus stops, bridges, etc.). 
#   AFFILIATION: Names of organizations, such as public and private companies, schools, universities, public institutions, prisons, healthcare institutions, non-governmental organizations, churches, etc. 
#   DEMOGRAPHIC_ATTRIBUTE: Demographic attributes of a person, such as native language, descent, heritage, ethnicity, nationality, religious or political group, birthmarks, ages, sexual orientation, gender and sex. 
#   TIME: Description of a specific date, time, or duration. 
#   HEALTH_INFORMATION: Details concerning an individual's health status, medical conditions, treatment records, and health insurance information. 
#   FINANCIAL_INFORMATION: Financial details such as bank account numbers, credit card numbers, investment records, salary information, and other financial statuses or activities. 
#   EDUCATIONAL_RECORD: Educational background details, including academic records, transcripts, degrees, and certification.
    
#     For the given message that a user sends to a chatbot, identify all the personally identifiable information using the above taxonomy only, and the entity_type should be selected from the all-caps categories.
#     Note that the information should be related to a real person not in a public context, but okay if not uniquely identifiable.
#     Result should be in its minimum possible unit.
#     Return me ONLY a json in the following format. Results should be an anonymized message and an array of all PII you have identified. It should be a valid json: {"anonymized_text": ANONYMIZED_TEXT_WITH_PII_REMOVED_REPLACE_PII_WITH_PII_TYPE_BLOCK, "analysis": [{"id": A_UNIQUE_NUMBER,"entity_type": YOU_DECIDE_THE_PII_TYPE,"pii": THE_PII_REMOVED,"analysis_explanation": WHY_IT_IS_PII, "score" : RATIO_OF_HOW_CONFIDENCE_YOU_ARE_IT_IS_PII, "start": INDEX_START_POSITION_OF_THE_PII_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES,"end": INDEX_END_POSITION_OF_THE_PII_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES},{"id": A_UNIQUE_NUMBER,"entity_type": YOU_DECIDE_THE_PII_TYPE,"pii": THE_PII_REMOVED,"analysis_explanation": WHY_IT_IS_PII, "score" : RATIO_OF_HOW_CONFIDENCE_YOU_ARE_IT_IS_PII, "start": INDEX_START_POSITION_OF_THE_PII_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES,"end": INDEX_END_POSITION_OF_THE_PII_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES}]}
#     Here is an example, 
#     Input is: I am Lewis Msasa, I graduated from UC Berkeley and I earn a lot of money
#     The output json is {"anonymized_text": "I <PERSON>, I graduated from <INSTITUTION> and I earn a lot of money", "analysis": [{"id": 12345,"entity_type": "<PERSON>","pii": "Lewis Msasa", "analysis_explanation":"a name of a person", "score" : 0.9, "start":5, "end":15},{"id": 1234543,"entity_type": "<INSTITUTION>", "pii": "UC Berkeley", "analysis_explanation":"a prestigious university", "score" : 0.9, "start":18, "end":28}]
#     Please apply this same logic on the prompt you will receive from the user.
#     ''',
#     "abstract": '''Rewrite the text to abstract the protected information, without changing other parts. Do this even for long text. For example:
#         Input: <Text>I am Lewis Msasa, I graduated from UC Berkeley and I earn a lot of money</Text>
#         <ProtectedInformation>Lewis Msasa, UC Berkeley</ProtectedInformation>
#         Output JSON: {"anonymized_text": "I <PERSON>, I graduated from <INSTITUTION> and I earn a lot of money", "analysis": [{"id": 12345,"entity_type": "<PERSON>","pii": "Lewis Msasa", "analysis_explanation":"a name of a person", "score" : 0.9, "start":5, "end":15},{"id": 1234543,"entity_type": "<INSTITUTION>", "pii": "UC Berkeley", "analysis_explanation":"a prestigious university", "score" : 0.9, "start":18, "end":28}]'''
# }





# system_prompts_pdf = {
#     "detect": '''You an expert in cybersecurity and data privacy. You are now tasked to detect PII from the given text, using the following taxonomy only:

#   ADDRESS
#   IP_ADDRESS
#   URL
#   SSN
#   PHONE_NUMBER
#   EMAIL
#   DRIVERS_LICENSE
#   PASSPORT_NUMBER
#   TAXPAYER_IDENTIFICATION_NUMBER
#   ID_NUMBER
#   NAME
#   USERNAME
  
#   KEYS: Passwords, passkeys, API keys, encryption keys, and any other form of security keys.
#   GEOLOCATION: Places and locations, such as cities, provinces, countries, international regions, or named infrastructures (bus stops, bridges, etc.). 
#   AFFILIATION: Names of organizations, such as public and private companies, schools, universities, public institutions, prisons, healthcare institutions, non-governmental organizations, churches, etc. 
#   DEMOGRAPHIC_ATTRIBUTE: Demographic attributes of a person, such as native language, descent, heritage, ethnicity, nationality, religious or political group, birthmarks, ages, sexual orientation, gender and sex. 
#   TIME: Description of a specific date, time, or duration. 
#   HEALTH_INFORMATION: Details concerning an individual's health status, medical conditions, treatment records, and health insurance information. 
#   FINANCIAL_INFORMATION: Financial details such as bank account numbers, credit card numbers, investment records, salary information, and other financial statuses or activities. 
#   EDUCATIONAL_RECORD: Educational background details, including academic records, transcripts, degrees, and certification.
    
#     For the given message that a user sends to a chatbot, identify all the personally identifiable information using the above taxonomy only, and the entity_type should be selected from the all-caps categories.
#     Note that the information should be related to a real person not in a public context, but okay if not uniquely identifiable.
#     Result should be in its minimum possible unit.
#     Return me ONLY a json in the following format. Results should be an anonymized message and an array of all PII words you have identified. It should be a valid json: {"results": ["some pii word", "another pii word"], "analysis": [{"entity_type": YOU_DECIDE_THE_PII_TYPE,"analysis_explanation": WHY_IT_IS_PII, "score" : RATIO_OF_HOW_CONFIDENCE_YOU_ARE_IT_IS_PII, "start": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_START,"end": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_END},{"entity_type": YOU_DECIDE_THE_PII_TYPE,"analysis_explanation": WHY_IT_IS_PII, "score" : RATIO_OF_HOW_CONFIDENCE_YOU_ARE_IT_IS_PII, "start": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_START,"end": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_END}]}''',
#     "abstract": '''Rewrite the text to abstract the protected information, without changing other parts. Do this even for long text. For example:
#         Input: <Text>I am Lewis Msasa, I graduated from UC Berkeley and I earn a lot of money</Text>
#         <ProtectedInformation>Lewis Msasa, UC Berkeley</ProtectedInformation>
#         Output JSON: {"results": ["Lewis Msasa", "UC Berkeley"], "analysis": [{"entity_type": "<PERSON>", "analysis_explanation":"a name of a person", "score" : 0.9, "start":5, "end":15},{"entity_type": "<INSTITUTION>", "analysis_explanation":"a prestigious university", "score" : 0.9, "start":18, "end":28}]}'''
# }


system_prompts_pdf = {
    "detect": '''You an expert in cybersecurity and data privacy. You are now tasked to detect PII from the given text, using the following taxonomy only:

  ADDRESS
  IP_ADDRESS
  URL
  SSN
  PHONE_NUMBER
  EMAIL
  DRIVERS_LICENSE
  PASSPORT_NUMBER
  TAXPAYER_IDENTIFICATION_NUMBER
  ID_NUMBER
  NAME
  USERNAME
  
  KEYS: Passwords, passkeys, API keys, encryption keys, and any other form of security keys.
  GEOLOCATION: Places and locations, such as cities, provinces, countries, international regions, or named infrastructures (bus stops, bridges, etc.). 
  AFFILIATION: Names of organizations, such as public and private companies, schools, universities, public institutions, prisons, healthcare institutions, non-governmental organizations, churches, etc. 
  DEMOGRAPHIC_ATTRIBUTE: Demographic attributes of a person, such as native language, descent, heritage, ethnicity, nationality, religious or political group, birthmarks, ages, sexual orientation, gender and sex. 
  TIME: Description of a specific date, time, or duration. 
  HEALTH_INFORMATION: Details concerning an individual's health status, medical conditions, treatment records, and health insurance information. 
  FINANCIAL_INFORMATION: Financial details such as bank account numbers, credit card numbers, investment records, salary information, and other financial statuses or activities. 
  EDUCATIONAL_RECORD: Educational background details, including academic records, transcripts, degrees, and certification.
    
    For the given message that a user sends to a chatbot, identify all the personally identifiable information using the above taxonomy only, and the entity_type should be selected from the all-caps categories.
    Note that the information should be related to a real person not in a public context, but okay if not uniquely identifiable.
    Result should be in its minimum possible unit.
    Return me ONLY a json in the following format. Results should be an anonymized message and an array of all PII you have identified. It should be a valid json: {"anonymized_text": ANONYMIZED_TEXT_WITH_PII_REMOVED_REPLACE_PII_WITH_PII_TYPE_BLOCK, "analysis": [{"entity_type": YOU_DECIDE_THE_PII_TYPE,"pii": THE_PII_REMOVED,"analysis_explanation": WHY_IT_IS_PII, "score" : RATIO_OF_HOW_CONFIDENCE_YOU_ARE_IT_IS_PII, "start": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_START,"end": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_END},{"entity_type": YOU_DECIDE_THE_PII_TYPE,"pii": THE_PII_REMOVED,"analysis_explanation": WHY_IT_IS_PII, "score" : RATIO_OF_HOW_CONFIDENCE_YOU_ARE_IT_IS_PII, "start": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_START,"end": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_END}]}''',
    "abstract": '''Rewrite the text to abstract the protected information, without changing other parts. Do this even for long text. For example:
        Input: <Text>I am Lewis Msasa, I graduated from UC Berkeley and I earn a lot of money</Text>
        <ProtectedInformation>Lewis Msasa, UC Berkeley</ProtectedInformation>
        Output JSON: {"anonymized_text": "I <PERSON>, I graduated from <INSTITUTION> and I earn a lot of money", "analysis": [{"entity_type": "<PERSON>","pii": "Lewis Msasa", "analysis_explanation":"a name of a person", "score" : 0.9, "start":5, "end":15},{"entity_type": "<INSTITUTION>", "pii": "UC Berkeley", "analysis_explanation":"a prestigious university", "score" : 0.9, "start":18, "end":28}]'''
}

# Ollama options
base_options = {"format": "json", "temperature": 0}

UPLOAD_DIR = "temp"

global_base_model = "phi3"