#nlp_keyword_extractor.py
import os
import logging
import xml
import xmltodict

from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer
from sentence_transformers import SentenceTransformer
from typing import List, Dict

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIRECTORY = "data"
SEED_TERMS = ["meditation", "meditate"]

class ModelBuilder:
    @staticmethod
    def build_models() -> tuple:
        try:
            sentence_transformer_model = SentenceTransformer("all-MiniLM-L6-v2")
            keybert_model = KeyBERT(model=sentence_transformer_model)
            count_vectorizer = KeyphraseCountVectorizer()
            return keybert_model, count_vectorizer
        except Exception as e:
            logger.error("Model initialization failed", exc_info=True)
            raise

class KeywordExtractor:
    def __init__(self, extraction_model: KeyBERT, vectorizer: KeyphraseCountVectorizer):
        self.extraction_model = extraction_model
        self.vectorizer = vectorizer

    def extract_keywords_from_content(self, content: str) -> List[Dict[str, float]]:
        return self.extraction_model.extract_keywords(
            content,
            vectorizer=self.vectorizer,
            use_mmr=True,
            use_maxsum=True,
            diversity=0.5,
            top_n=5,
            seed_keywords=SEED_TERMS,
        )


class XMLParser:
    @staticmethod
    def parse_xml_content(xml_content: str) -> str:
        try:
            data_dict = xmltodict.parse(xml_content)
            return XMLParser.extract_text_from_main(data_dict.get("doc", {}).get("main", {}))
        except xml.parsers.expat.ExpatError as e:
            logger.error("XML processing error: syntax error")
            return ""
        except Exception as e:
            logger.error(f"XML processing error: {e}", exc_info=True)
            return ""

    @staticmethod
    def extract_text_from_main(main_content: dict) -> str:
        return ' '.join([p.get("#text", "") if isinstance(p, dict) else p for p in main_content.get("p", [])]).strip()


class FileHandler:
    @staticmethod
    def read_content_from_file(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}", exc_info=True)
            return ""


class OutputFormatter:
    @staticmethod
    def display_keywords(file_name: str, extracted_keywords: List[Dict[str, float]]) -> None:
        keyword_str = f"File: {file_name}\nExtracted Keywords:\n"
        keyword_str += "\n".join([f"  {keyword}: {score}" for keyword, score in extracted_keywords])
        logger.info(keyword_str)

def process_files_and_extract_keywords():
    keybert_model, vectorizer_model = ModelBuilder.build_models()
    extractor = KeywordExtractor(keybert_model, vectorizer_model)

    for file_name in os.listdir(DATA_DIRECTORY):
        file_path = os.path.join(DATA_DIRECTORY, file_name)
        try:
            content = FileHandler.read_content_from_file(file_path)
            if content:
                parsed_content = XMLParser.parse_xml_content(content)
                keywords = extractor.extract_keywords_from_content(parsed_content)
                OutputFormatter.display_keywords(file_name, keywords)
        except Exception as e:
            logger.error(f"Error processing {file_name}: {e}", exc_info=True)



if __name__ == "__main__":
    process_files_and_extract_keywords()