from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from PIL import Image
from pdf2image import convert_from_path
from PIL import Image
from faker import Faker
import fitz
import os
import base64
import json
import pytesseract
from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, BatchAnonymizerEngine
from presidio_image_redactor import ImageRedactorEngine, ImageAnalyzerEngine
import en_core_web_sm
from presidio_analyzer.nlp_engine import  SpacyNlpEngine
from presidio_anonymizer.entities import OperatorConfig


class PresidioAnonymizer():

    def __init__(self):
            nlp = en_core_web_sm.load()
            nlp_config = {"nlp_engine_name": "spacy", "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]}
            nlp_engine = SpacyNlpEngine(nlp_config)
            nlp_engine.nlp = {"en": nlp}
            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
            self.anonymizer = AnonymizerEngine()
            self.use_fake=True
            self.fake = Faker()
            self.language="en"
       
            self.image_engine = ImageRedactorEngine(image_analyzer_engine=ImageAnalyzerEngine(analyzer_engine=self.analyzer))

    def redact_image(self,image, target_path, fill=(0, 0, 0)):
        redacted_image = self.image_engine.redact(image, fill)
        redacted_image.save(target_path)
        return target_path
    def anonymize_batch_text(self,texts, language="en"):
        analyzer = BatchAnalyzerEngine(analyzer_engine=AnalyzerEngine())
        anonymizer = BatchAnonymizerEngine(anonymizer_engine=AnonymizerEngine())
        analyzed_results = list(analyzer.analyze_texts(texts, language=language))
        anonymized_results = anonymizer.anonymize(texts, analyzed_results)
        return zip(texts, anonymized_results)


    def pdf_to_images(self,pdf_path, output_dir="temp_images"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        images = convert_from_path(pdf_path)
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"page_{i+1}.png")
            image.save(image_path, "PNG")
            image_paths.append(image_path)
        return image_paths
    def redact_images(self,image_paths, redacted_dir="redacted_images"):
        if not os.path.exists(redacted_dir):
            os.makedirs(redacted_dir)
        engine = ImageRedactorEngine()
        redacted_image_paths = []
        for image_path in image_paths:
            image = Image.open(image_path)
            redacted_image = engine.redact(image, fill=(255, 0, 0))  # Red fill for redaction (customizable)
            redacted_image_path = os.path.join(redacted_dir, os.path.basename(image_path))
            redacted_image.save(redacted_image_path)
            redacted_image_paths.append(redacted_image_path)
        return redacted_image_paths


    def analyze_image_and_show_results(self,image):
    
        extracted_text = pytesseract.image_to_string(image)
        analysis_results = self.analyzer.analyze(text=extracted_text, language="en")
        
        # Display the detected entities
        analysis_json = []
        if analysis_results:
            for result in analysis_results:
                entity_text = extracted_text[result.start:result.end]
                print(f"- Type: {result.entity_type}, Value: '{entity_text}', Position: {result.start}-{result.end}, Confidence: {result.score:.2f}")
                json_data = {
                    "entity_type":result.entity_type,
                    "value": entity_text,
                    "position": {"start": int(result.start), "end": int(result.end)},
                    "confidence": float(result.score)
                }
                analysis_json.append(json_data)
        else:
            return None
        
        return analysis_json
    # async def anonymize_pdf(self,filepath, output_path,fill=(0,0,0), **kwargs):
    #     # Convert PDF to images
        
    #     images = convert_from_path(filepath)
        
    #     redacted_images = []
    #     analyzed_results = []
    #     for i, image in enumerate(images):
    #         analysis = self.analyze_image_and_show_results(image)
    #         redacted_image = self.image_engine.redact(image,fill=fill)
    #         redacted_images.append(redacted_image)
    #         if analysis:
    #             analyzed_results.append(analysis)
        
    #     if redacted_images:
    #         try:
    #             #os.makedirs(os.path.dirname(output_path), exist_ok=True)
    #             redacted_images[0].save(
    #                     output_path,
    #                     save_all=True,
    #                     append_images=redacted_images[1:] if len(redacted_images) > 1 else [],
    #                     format="PDF"
    #                 )
    #             print(f"Successfully saved to {output_path}")
    #         except Exception as e:
    #             print("no file output",e)
    #     return output_path, analyzed_results
        
    def redact_pdf(self,pdf_path, output_path, sensitive_words,fill=(0,0,0), **kwargs):
        pass
    def underline_pdf(self,pdf_path, output_path, sensitive_words,fill=(0,0,0), **kwargs):
        pass
    def anonymize_pdf(self,pdf_path, output_path,fill=(0,0,0), **kwargs):
       
        doc = fitz.open(pdf_path)
        for page in doc:
            text = page.get_text()
            results = self.analyzer.analyze(text=text, language=self.language)
            for result in results:
                entity_text = text[result.start:result.end]
                for rect in page.search_for(entity_text):
                    page.add_redact_annot(rect, fill=fill)  
            page.apply_redactions()
        doc.save(output_path)
        return output_path, ""
 
    
    def get_pdf_text(self,pdf_path, **kwargs):
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text() for page in doc])
        return text
    async def anonymize_text(self,text, **kwargs):
        results = self.analyzer.analyze(text=text, language=self.language)
       
        operators = {}
        if False:
            for result in results:
              
                entity_type = result.entity_type
                if entity_type == "PERSON":
                    operators[entity_type] = OperatorConfig("replace", {"new_value": self.fake.name().split(" ")[0]})
                elif entity_type == "EMAIL_ADDRESS":
                    operators[entity_type] = OperatorConfig("replace", {"new_value": self.fake.email()})
                elif entity_type == "PHONE_NUMBER":
                    operators[entity_type] = OperatorConfig("replace", {"new_value": self.fake.phone_number()})
        anonymized_text = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )

        yield json.dumps({ "anonymized_text": anonymized_text.text, "analysis": [result.to_dict() for result in results]})



