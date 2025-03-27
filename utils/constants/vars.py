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
    Return me ONLY a json in the following format. Results should be an anonymized message and an array of all PII you have identified. It should be a valid json: {"anonymized_text": ANONYMIZED_TEXT_WITH_PII_REMOVED_REPLACE_PII_WITH_BLOCK, "analysis": [{"entity_type": YOU_DECIDE_THE_PII_TYPE,"analysis_explanation": WHY_IT_IS_PII, "score" : RATIO_OF_HOW_CONFIDENCE_YOU_ARE_IT_IS_PII, "start": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_START,"end": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_END},{"entity_type": YOU_DECIDE_THE_PII_TYPE,"analysis_explanation": WHY_IT_IS_PII, "score" : RATIO_OF_HOW_CONFIDENCE_YOU_ARE_IT_IS_PII, "start": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_START,"end": POSITION_OF_THE_TEXT_IN_THE_SENTENCE_INCLUDING_SPACES_END}]}''',
    "abstract": '''Rewrite the text to abstract the protected information, without changing other parts. Do this even for long text. For example:
        Input: <Text>I am Lewis Msasa, I graduated from UC Berkeley and I earn a lot of money</Text>
        <ProtectedInformation>Lewis Msasa, UC Berkeley</ProtectedInformation>
        Output JSON: {"anonymized_text": "I <PERSON>, I graduated from <INSTITUTION> and I earn a lot of money", "analysis": [{"entity_type": "<PERSON>", "analysis_explanation":"a name of a person", "score" : 0.9, "start":5, "end":15},{"entity_type": "<INSTITUTION>", "analysis_explanation":"a prestigious university", "score" : 0.9, "start":18, "end":28}]'''
}





system_prompts_pdf = {
    "detect": '''You are an expert in cybersecurity and data privacy. You are now tasked with detecting PII from the given text (it will be a long text), using the following taxonomy only:

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
  DEMOGRAPHIC_ATTRIBUTE: Demographic attributes of a person, such as native language, descent, heritage, ethnicity, nationality, religious or political group, birthmarks, ages, sexual orientation, gender, and sex. 
  TIME: Description of a specific date, time, or duration. 
  HEALTH_INFORMATION: Details concerning an individual's health status, medical conditions, treatment records, and health insurance information. 
  FINANCIAL_INFORMATION: Financial details such as bank account numbers, credit card numbers, investment records, salary information, and other financial statuses or activities. 
  EDUCATIONAL_RECORD: Educational background details, including academic records, transcripts, degrees, and certifications.
  
### **Additional Instructions for Handling Noisy Text:**
- **Ignore special characters** such as `\n`, `\t`, `\r`, and other formatting artifacts unless they are part of the PII.
- **Normalize encodings** to correctly detect characters with diacritics (e.g., `José` should be treated the same as `Jose`).
- **Handle OCR artifacts** like `l` being mistaken for `1` or `0` being mistaken for `O` when detecting PII.
- **Ensure JSON validity** in the output, even if no PII is found (return `"results": []` when no PII is detected).

For the given message that a user sends to a chatbot, identify all the personally identifiable information using the above taxonomy only. The array of PII should be returned
 Return me ONLY a json in the following format. Results should be an array of all PII you have identified. It should be a valid json:''',
    "abstract": '''Get all the words that are PII as an array. Just give the specific words that are PII nothing more and they should be an array. For example:
        Input: <Text>I am Lewis Msasa, I graduated from UC Berkeley and I earn a lot of money</Text>
        <ProtectedInformation>Lewis Msasa, UC Berkeley</ProtectedInformation>
        Output JSON: {"results": ["Lewis Msasa", "UC Berkeley"] }. The json object should have results as the parent
'''
}

# Ollama options
base_options = {"format": "json", "temperature": 0}

UPLOAD_DIR = "temp"

global_base_model = "phi3"