from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from PIL import Image
import pydicom
from faker import Faker
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import img2pdf
import pytesseract
import os
import base64
from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, BatchAnonymizerEngine
from presidio_analyzer import Pattern, PatternRecognizer
from presidio_image_redactor import ImageRedactorEngine, DicomImageRedactorEngine, ImageAnalyzerEngine
import spacy
import en_core_web_sm
from presidio_analyzer.nlp_engine import NlpEngine, SpacyNlpEngine

nlp = en_core_web_sm.load()
nlp_config = {"nlp_engine_name": "spacy", "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]}
nlp_engine = SpacyNlpEngine(nlp_config)
nlp_engine.nlp = {"en": nlp}
analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

anonymizer = AnonymizerEngine()

image_engine = ImageRedactorEngine(image_analyzer_engine=ImageAnalyzerEngine(analyzer_engine=analyzer))

def redact_image(image, target_path, fill=(0, 0, 0)):
    redacted_image = image_engine.redact(image, fill)
    redacted_image.save(target_path)
    return target_path
def anonymize_batch_text(texts, language="en"):
    analyzer = BatchAnalyzerEngine(analyzer_engine=AnalyzerEngine())
    anonymizer = BatchAnonymizerEngine(anonymizer_engine=AnonymizerEngine())
    analyzed_results = list(analyzer.analyze_texts(texts, language=language))
    anonymized_results = anonymizer.anonymize(texts, analyzed_results)
    return zip(texts, anonymized_results)


def pdf_to_images(pdf_path, output_dir="temp_images"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{i+1}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)
    return image_paths
def redact_images(image_paths, redacted_dir="redacted_images"):
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
def images_to_pdf(image_paths, output_pdf_path):
    with open(output_pdf_path, "wb") as f:
        print("outro", output_pdf_path)
        f.write(img2pdf.convert(image_paths))
        print("done")

async def anonymize_pdf_2(pdf_path, output_pdf_path):
    # Convert PDF to images
    image_paths = pdf_to_images(pdf_path)
    print(f"Converted PDF to {len(image_paths)} images.")

    # Redact sensitive information
    redacted_image_paths = redact_images(image_paths)
    print(f"Redacted {len(redacted_image_paths)} images.")

    # Convert back to PDF
    images_to_pdf(redacted_image_paths, output_pdf_path)
    print(f"Saved redacted PDF to {output_pdf_path}")

    # Optional: Clean up temporary files
    for path in image_paths + redacted_image_paths:
        os.remove(path)
    os.rmdir("temp_images")
    os.rmdir("redacted_images")
    return output_pdf_path

def anonymize_pdf(filepath, output_path,fill=(0,0,0)):
     # Convert PDF to images
     
    images = convert_from_path(filepath)
    
    redacted_images = []
    for i, image in enumerate(images):
        redacted_image = image_engine.redact(image,fill=fill)
        redacted_images.append(redacted_image)
    
    if redacted_images:
        try:
            print("within", output_path)
            #os.makedirs(os.path.dirname(output_path), exist_ok=True)
            redacted_images[0].save(
                    output_path,
                    save_all=True,
                    append_images=redacted_images[1:] if len(redacted_images) > 1 else [],
                    format="PDF"
                )
            print(f"Successfully saved to {output_path}")
        except Exception as e:
            print("no file output",e)
    return output_path
     


def anonymize_text(text, use_fake=True,language="en"):
    results = analyzer.analyze(text=text, language=language)
    operators = {}
    if use_fake:
        for result in results:
            entity_type = result["entity_type"]
            if entity_type == "PERSON":
                operators[entity_type] = {"type": "replace", "new_value": fake.name().split(" ")[0]}
            elif entity_type == "EMAIL_ADDRESS":
                operators[entity_type] = {"type": "replace", "new_value": fake.email()}
            elif entity_type == "PHONE_NUMBER":
                operators[entity_type] = {"type": "replace", "new_value": fake.phone_number()}
    anonymized_text = anonymizer.anonymize(
    text=text,
    analyzer_results=results,
    operators=operators
    )
    return anonymized_text.text



