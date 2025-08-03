#!/usr/bin/env python3
"""
Text Preprocessing and Quality Assessment System

Provides comprehensive text preprocessing capabilities including cleaning, normalization,
language detection, quality assessment, and optimization for downstream NLP tasks.
Includes specialized preprocessing for different document types and domains.
"""

import logging
import re
import string
import unicodedata
import time
from typing import Dict, List, Optional, Any, Tuple, Union, Set, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import Counter, defaultdict
from abc import ABC, abstractmethod
from enum import Enum
import statistics

# NLP and text processing libraries
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.chunk import ne_chunk
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from langdetect import detect, detect_langs, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

logger = logging.getLogger(__name__)


class TextQuality(Enum):
    """Text quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNUSABLE = "unusable"


class ProcessingLevel(Enum):
    """Text preprocessing levels"""
    MINIMAL = "minimal"           # Basic cleaning only
    STANDARD = "standard"         # Standard NLP preprocessing
    AGGRESSIVE = "aggressive"     # Comprehensive preprocessing
    DOMAIN_SPECIFIC = "domain_specific"  # Domain-aware preprocessing


@dataclass
class TextQualityMetrics:
    """Comprehensive text quality assessment metrics"""
    # Basic metrics
    character_count: int = 0
    word_count: int = 0
    sentence_count: int = 0 
    paragraph_count: int = 0
    
    # Language metrics
    detected_language: Optional[str] = None
    language_confidence: float = 0.0
    
    # Readability metrics
    flesch_reading_ease: Optional[float] = None
    flesch_kincaid_grade: Optional[float] = None
    automated_readability_index: Optional[float] = None
    
    # Content quality indicators
    average_word_length: float = 0.0
    average_sentence_length: float = 0.0
    lexical_diversity: float = 0.0  # Type-token ratio
    
    # Structure quality
    has_proper_sentences: bool = False
    has_proper_capitalization: bool = False
    has_proper_punctuation: bool = False
    
    # Noise indicators
    special_character_ratio: float = 0.0
    numeric_character_ratio: float = 0.0
    uppercase_ratio: float = 0.0
    
    # Content coherence
    repetition_score: float = 0.0
    coherence_score: float = 0.0
    
    # Overall assessment
    overall_quality: TextQuality = TextQuality.UNUSABLE
    quality_score: float = 0.0  # 0-100 score
    
    # Processing metadata
    assessment_time: float = 0.0
    assessment_method: str = "unknown"


@dataclass
class PreprocessingResult:
    """Result of text preprocessing"""
    # Processed text versions
    original_text: str = ""
    cleaned_text: str = ""
    normalized_text: str = ""
    tokenized_text: List[str] = field(default_factory=list)
    
    # Linguistic analysis
    sentences: List[str] = field(default_factory=list)
    paragraphs: List[str] = field(default_factory=list)
    named_entities: List[Dict[str, Any]] = field(default_factory=list)
    pos_tags: List[Tuple[str, str]] = field(default_factory=list)
    
    # Extracted elements
    removed_elements: Dict[str, List[str]] = field(default_factory=dict)
    preserved_elements: Dict[str, List[str]] = field(default_factory=dict)
    
    # Quality assessment
    quality_metrics: TextQualityMetrics = field(default_factory=TextQualityMetrics)
    
    # Processing metadata
    processing_level: ProcessingLevel = ProcessingLevel.MINIMAL
    processing_time: float = 0.0
    processing_steps: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def get_best_text(self) -> str:
        """Get the best available processed text"""
        if self.normalized_text:
            return self.normalized_text
        elif self.cleaned_text:
            return self.cleaned_text
        else:
            return self.original_text


class TextProcessor(ABC):
    """Abstract base class for text processors"""
    
    @abstractmethod
    def process(self, text: str, **kwargs) -> str:
        """Process text and return cleaned version"""
        pass
    
    @abstractmethod
    def get_processor_info(self) -> Dict[str, Any]:
        """Get information about this processor"""
        pass


class BasicTextCleaner(TextProcessor):
    """Basic text cleaning operations"""
    
    def __init__(self):
        self.name = "BasicTextCleaner"
        
        # Common noise patterns
        self.noise_patterns = [
            r'\x00-\x1f',      # Control characters
            r'\x7f-\x9f',      # More control characters
            r'\ufeff',         # Byte order mark
            r'\u200b',         # Zero width space
            r'\u2060',         # Word joiner
            r'\u00ad',         # Soft hyphen
        ]
        
        # Email and URL patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        
    def process(self, text: str, **kwargs) -> str:
        """Basic text cleaning"""
        if not text:
            return ""
        
        # Remove control characters and noise
        for pattern in self.noise_patterns:
            text = re.sub(pattern, '', text)
        
        # Normalize Unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Fix common encoding issues
        text = text.replace('\x92', "'")  # Smart quote
        text = text.replace('\x93', '"')  # Smart quote
        text = text.replace('\x94', '"')  # Smart quote
        text = text.replace('\x96', '–')  # En dash
        text = text.replace('\x97', '—')  # Em dash
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def remove_emails(self, text: str) -> Tuple[str, List[str]]:
        """Remove email addresses and return them separately"""
        emails = re.findall(self.email_pattern, text)
        cleaned_text = re.sub(self.email_pattern, '[EMAIL]', text)
        return cleaned_text, emails
    
    def remove_urls(self, text: str) -> Tuple[str, List[str]]:
        """Remove URLs and return them separately"""
        urls = re.findall(self.url_pattern, text)
        cleaned_text = re.sub(self.url_pattern, '[URL]', text)
        return cleaned_text, urls
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get processor information"""
        return {
            "processor_name": self.name,
            "capabilities": [
                "unicode_normalization",
                "control_character_removal", 
                "whitespace_normalization",
                "email_detection",
                "url_detection"
            ]
        }


class AdvancedTextNormalizer(TextProcessor):
    """Advanced text normalization with linguistic processing"""
    
    def __init__(self):
        self.name = "AdvancedTextNormalizer"
        self.basic_cleaner = BasicTextCleaner()
        
        # Initialize NLTK data if available
        if NLTK_AVAILABLE:
            self._ensure_nltk_data()
        
        # Initialize spaCy model if available
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {e}")
    
    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        try:
            import nltk
            required_data = [
                'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger',
                'maxent_ne_chunker', 'words'
            ]
            
            for data_name in required_data:
                try:
                    nltk.data.find(f'tokenizers/{data_name}')
                except LookupError:
                    try:
                        nltk.download(data_name, quiet=True)
                    except Exception as e:
                        logger.warning(f"Failed to download NLTK data {data_name}: {e}")
        except Exception as e:
            logger.warning(f"NLTK data setup failed: {e}")
    
    def process(self, text: str, **kwargs) -> str:
        """Advanced text normalization"""
        if not text:
            return ""
        
        # Basic cleaning first
        text = self.basic_cleaner.process(text)
        
        # Advanced normalization options
        lowercase = kwargs.get('lowercase', False)
        remove_punctuation = kwargs.get('remove_punctuation', False)
        remove_stopwords = kwargs.get('remove_stopwords', False)
        lemmatize = kwargs.get('lemmatize', False)
        stem = kwargs.get('stem', False)
        
        # Apply transformations
        if lowercase:
            text = text.lower()
        
        if remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenization and linguistic processing
        if NLTK_AVAILABLE and (remove_stopwords or lemmatize or stem):
            tokens = word_tokenize(text)
            
            if remove_stopwords:
                stop_words = set(stopwords.words('english'))
                tokens = [token for token in tokens if token.lower() not in stop_words]
            
            if lemmatize:
                lemmatizer = WordNetLemmatizer()
                tokens = [lemmatizer.lemmatize(token) for token in tokens]
            
            elif stem:  # Don't stem if we're lemmatizing
                stemmer = PorterStemmer()
                tokens = [stemmer.stem(token) for token in tokens]
            
            text = ' '.join(tokens)
        
        return text
    
    def extract_named_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using available NLP libraries"""
        entities = []
        
        # Try spaCy first (usually better)
        if self.nlp:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "method": "spacy"
                    })
                return entities
            except Exception as e:
                logger.warning(f"spaCy NER failed: {e}")
        
        # Fallback to NLTK
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)
                named_entities = ne_chunk(pos_tags)
                
                current_entity = []
                current_label = None
                
                for item in named_entities:
                    if hasattr(item, 'label'):  # Named entity
                        if current_label != item.label():
                            if current_entity:
                                entities.append({
                                    "text": " ".join([token for token, pos in current_entity]),
                                    "label": current_label,
                                    "method": "nltk"
                                })
                            current_entity = []
                            current_label = item.label()
                        
                        for token, pos in item:
                            current_entity.append((token, pos))
                    else:
                        if current_entity:
                            entities.append({
                                "text": " ".join([token for token, pos in current_entity]),
                                "label": current_label,
                                "method": "nltk"
                            })
                            current_entity = []
                            current_label = None
                
                # Handle final entity
                if current_entity:
                    entities.append({
                        "text": " ".join([token for token, pos in current_entity]),
                        "label": current_label,
                        "method": "nltk"
                    })
                
            except Exception as e:
                logger.warning(f"NLTK NER failed: {e}")
        
        return entities
    
    def get_pos_tags(self, text: str) -> List[Tuple[str, str]]:
        """Get part-of-speech tags"""
        if not NLTK_AVAILABLE:
            return []
        
        try:
            tokens = word_tokenize(text)
            return pos_tag(tokens)
        except Exception as e:
            logger.warning(f"POS tagging failed: {e}")
            return []
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get processor information"""
        return {
            "processor_name": self.name,
            "nltk_available": NLTK_AVAILABLE,
            "spacy_available": self.nlp is not None,
            "capabilities": [
                "advanced_normalization",
                "named_entity_recognition", 
                "pos_tagging",
                "lemmatization",
                "stemming",
                "stopword_removal"
            ]
        }


class TextQualityAssessor:
    """Comprehensive text quality assessment"""
    
    def __init__(self):
        self.name = "TextQualityAssessor"
        
        # Initialize language detection
        self.lang_detector_available = LANGDETECT_AVAILABLE
        
        # Initialize readability tools
        self.textstat_available = TEXTSTAT_AVAILABLE
        
        # Common indicators of poor quality text
        self.noise_indicators = [
            r'[^\w\s\.\,\!\?\;\:\-\(\)]',  # Excessive special characters
            r'\d{4,}',  # Long number sequences
            r'[A-Z]{10,}',  # Long uppercase sequences
            r'(.)\1{4,}',  # Repeated characters (5+)
        ]
    
    def assess_quality(self, text: str) -> TextQualityMetrics:
        """Comprehensive text quality assessment"""
        start_time = time.time()
        
        if not text or not text.strip():
            return TextQualityMetrics(
                overall_quality=TextQuality.UNUSABLE,
                quality_score=0.0,
                assessment_time=time.time() - start_time,
                assessment_method=self.name
            )
        
        metrics = TextQualityMetrics()
        
        # Basic metrics
        metrics.character_count = len(text)
        metrics.word_count = len(text.split())
        
        # Sentence and paragraph counting
        if NLTK_AVAILABLE:
            try:
                metrics.sentence_count = len(sent_tokenize(text))
            except Exception:
                metrics.sentence_count = len(re.split(r'[.!?]+', text))
        else:
            metrics.sentence_count = len(re.split(r'[.!?]+', text))
        
        metrics.paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # Language detection
        if self.lang_detector_available:
            try:
                detected_langs = detect_langs(text)
                if detected_langs:
                    metrics.detected_language = detected_langs[0].lang
                    metrics.language_confidence = detected_langs[0].prob
            except LangDetectException:
                pass
        
        # Readability metrics
        if self.textstat_available and metrics.word_count > 10:
            try:
                metrics.flesch_reading_ease = textstat.flesch_reading_ease(text)
                metrics.flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
                metrics.automated_readability_index = textstat.automated_readability_index(text)
            except Exception as e:
                logger.warning(f"Readability calculation failed: {e}")
        
        # Content quality indicators
        words = text.split()
        if words:
            metrics.average_word_length = sum(len(word) for word in words) / len(words)
        
        if metrics.sentence_count > 0:
            metrics.average_sentence_length = metrics.word_count / metrics.sentence_count
        
        # Lexical diversity (type-token ratio)
        if words:
            unique_words = set(word.lower() for word in words)
            metrics.lexical_diversity = len(unique_words) / len(words)
        
        # Structure quality checks
        metrics.has_proper_sentences = bool(re.search(r'[.!?]', text))
        metrics.has_proper_capitalization = bool(re.search(r'[A-Z]', text))
        metrics.has_proper_punctuation = bool(re.search(r'[.!?,;:]', text))
        
        # Noise indicators
        total_chars = len(text)
        if total_chars > 0:
            special_chars = len(re.findall(r'[^\w\s]', text))
            metrics.special_character_ratio = special_chars / total_chars
            
            numeric_chars = len(re.findall(r'\d', text))
            metrics.numeric_character_ratio = numeric_chars / total_chars
            
            uppercase_chars = len(re.findall(r'[A-Z]', text))
            metrics.uppercase_ratio = uppercase_chars / total_chars
        
        # Repetition analysis
        metrics.repetition_score = self._calculate_repetition_score(text)
        
        # Coherence analysis
        metrics.coherence_score = self._calculate_coherence_score(text)
        
        # Overall quality assessment
        metrics.quality_score = self._calculate_overall_quality_score(metrics)
        metrics.overall_quality = self._classify_quality(metrics.quality_score)
        
        metrics.assessment_time = time.time() - start_time
        metrics.assessment_method = self.name
        
        return metrics
    
    def _calculate_repetition_score(self, text: str) -> float:
        """Calculate text repetition score (0=no repetition, 1=highly repetitive)"""
        try:
            words = text.lower().split()
            if len(words) < 10:
                return 0.0
            
            # Count word frequencies
            word_counts = Counter(words)
            
            # Calculate repetition based on most common words
            most_common = word_counts.most_common(5)
            repetition_score = 0.0
            
            for word, count in most_common:
                if len(word) > 3:  # Ignore very short words
                    repetition_ratio = count / len(words)
                    repetition_score += repetition_ratio * repetition_ratio
            
            return min(repetition_score, 1.0)
            
        except Exception:
            return 0.0
    
    def _calculate_coherence_score(self, text: str) -> float:
        """Calculate text coherence score (0=incoherent, 1=coherent)"""
        try:
            # Simple coherence indicators
            coherence_indicators = 0
            total_checks = 0
            
            # Check for transition words
            transition_words = [
                'however', 'therefore', 'furthermore', 'moreover', 'consequently',
                'additionally', 'meanwhile', 'similarly', 'in contrast', 'on the other hand'
            ]
            
            transition_count = sum(1 for word in transition_words if word in text.lower())
            sentence_count = max(1, len(re.split(r'[.!?]+', text)))
            
            # Normalize transition word usage
            if sentence_count > 2:
                transition_ratio = transition_count / sentence_count
                coherence_indicators += min(transition_ratio * 2, 1.0)
                total_checks += 1
            
            # Check for consistent tense (simplified)
            past_tense_indicators = len(re.findall(r'\b\w+ed\b', text))
            present_tense_indicators = len(re.findall(r'\b\w+s\b', text))
            
            if past_tense_indicators + present_tense_indicators > 0:
                tense_consistency = abs(past_tense_indicators - present_tense_indicators) / (past_tense_indicators + present_tense_indicators)
                coherence_indicators += (1.0 - tense_consistency)
                total_checks += 1
            
            # Check for proper paragraph structure
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            if len(paragraphs) > 1:
                avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
                if 20 <= avg_paragraph_length <= 200:  # Reasonable paragraph length
                    coherence_indicators += 1.0
                total_checks += 1
            
            return coherence_indicators / max(1, total_checks)
            
        except Exception:
            return 0.5  # Default moderate coherence
    
    def _calculate_overall_quality_score(self, metrics: TextQualityMetrics) -> float:
        """Calculate overall quality score (0-100)"""
        try:
            score = 0.0
            weights = {}
            
            # Length indicators (20% weight)
            if metrics.word_count >= 50:
                length_score = min(metrics.word_count / 200, 1.0)  # Optimal around 200 words
            else:
                length_score = metrics.word_count / 50  # Penalty for very short texts
            
            score += length_score * 20
            weights['length'] = 20
            
            # Structure indicators (25% weight)
            structure_score = 0.0
            structure_checks = 0
            
            if metrics.has_proper_sentences:
                structure_score += 1.0
            structure_checks += 1
            
            if metrics.has_proper_capitalization:
                structure_score += 1.0
            structure_checks += 1
            
            if metrics.has_proper_punctuation:
                structure_score += 1.0
            structure_checks += 1
            
            # Sentence length check
            if 5 <= metrics.average_sentence_length <= 25:
                structure_score += 1.0
            structure_checks += 1
            
            if structure_checks > 0:
                score += (structure_score / structure_checks) * 25
                weights['structure'] = 25
            
            # Content quality (25% weight)
            content_score = 0.0
            
            # Lexical diversity
            if metrics.lexical_diversity > 0.3:
                content_score += min(metrics.lexical_diversity * 2, 1.0)
            
            # Average word length
            if 4 <= metrics.average_word_length <= 7:
                content_score += 1.0
            
            # Language detection confidence
            if metrics.language_confidence > 0.8:
                content_score += 1.0
            
            score += (content_score / 3) * 25
            weights['content'] = 25
            
            # Noise penalties (15% weight)
            noise_score = 1.0
            
            # Special character penalty
            if metrics.special_character_ratio > 0.1:
                noise_score -= min(metrics.special_character_ratio * 2, 0.5)
            
            # Uppercase penalty
            if metrics.uppercase_ratio > 0.2:
                noise_score -= min((metrics.uppercase_ratio - 0.2) * 2, 0.3)
            
            # Repetition penalty
            if metrics.repetition_score > 0.3:
                noise_score -= min(metrics.repetition_score, 0.5)
            
            score += max(noise_score, 0) * 15
            weights['noise'] = 15
            
            # Coherence bonus (15% weight)
            score += metrics.coherence_score * 15
            weights['coherence'] = 15
            
            return min(max(score, 0), 100)
            
        except Exception as e:
            logger.warning(f"Quality score calculation failed: {e}")
            return 50.0  # Default moderate quality
    
    def _classify_quality(self, score: float) -> TextQuality:
        """Classify quality based on score"""
        if score >= 80:
            return TextQuality.EXCELLENT
        elif score >= 60:
            return TextQuality.GOOD
        elif score >= 40:
            return TextQuality.FAIR
        elif score >= 20:
            return TextQuality.POOR
        else:
            return TextQuality.UNUSABLE


class TextPreprocessor:
    """Main text preprocessing coordinator"""
    
    def __init__(self):
        # Initialize processors
        self.basic_cleaner = BasicTextCleaner()
        self.advanced_normalizer = AdvancedTextNormalizer()
        self.quality_assessor = TextQualityAssessor()
        
        # Processing statistics
        self.processing_stats = {
            'total_texts': 0,
            'successful_processing': 0,
            'total_processing_time': 0.0,
            'quality_distribution': Counter(),
            'processing_levels': Counter()
        }
        
        logger.info("TextPreprocessor initialized with all components")
    
    def preprocess(self, text: str, 
                  level: ProcessingLevel = ProcessingLevel.STANDARD,
                  **kwargs) -> PreprocessingResult:
        """Comprehensive text preprocessing"""
        start_time = time.time()
        
        result = PreprocessingResult(
            original_text=text,
            processing_level=level
        )
        
        if not text or not text.strip():
            result.warnings.append("Empty or whitespace-only text provided")
            result.processing_time = time.time() - start_time
            return result
        
        try:
            # Step 1: Quality assessment of original text
            result.processing_steps.append("quality_assessment")
            original_quality = self.quality_assessor.assess_quality(text)
            result.quality_metrics = original_quality
            
            # Step 2: Basic cleaning
            result.processing_steps.append("basic_cleaning")
            cleaned_text = self.basic_cleaner.process(text)
            result.cleaned_text = cleaned_text
            
            # Extract and preserve important elements
            cleaned_text, emails = self.basic_cleaner.remove_emails(cleaned_text)
            if emails:
                result.removed_elements['emails'] = emails
            
            cleaned_text, urls = self.basic_cleaner.remove_urls(cleaned_text)
            if urls:
                result.removed_elements['urls'] = urls
            
            # Step 3: Advanced processing based on level
            processed_text = cleaned_text
            
            if level in [ProcessingLevel.STANDARD, ProcessingLevel.AGGRESSIVE, ProcessingLevel.DOMAIN_SPECIFIC]:
                result.processing_steps.append("advanced_normalization")
                
                # Standard normalization options
                norm_options = {
                    'lowercase': kwargs.get('lowercase', level == ProcessingLevel.AGGRESSIVE),
                    'remove_punctuation': kwargs.get('remove_punctuation', False),
                    'remove_stopwords': kwargs.get('remove_stopwords', level == ProcessingLevel.AGGRESSIVE),
                    'lemmatize': kwargs.get('lemmatize', level in [ProcessingLevel.STANDARD, ProcessingLevel.AGGRESSIVE]),
                    'stem': kwargs.get('stem', False)
                }
                
                processed_text = self.advanced_normalizer.process(processed_text, **norm_options)
                result.normalized_text = processed_text
                
                # Extract linguistic features
                if NLTK_AVAILABLE:
                    result.processing_steps.append("linguistic_analysis")
                    
                    # Sentence tokenization
                    try:
                        result.sentences = sent_tokenize(cleaned_text)  # Use cleaned but not normalized text
                    except Exception as e:
                        result.warnings.append(f"Sentence tokenization failed: {e}")
                    
                    # Word tokenization
                    try:
                        result.tokenized_text = word_tokenize(processed_text)
                    except Exception as e:
                        result.warnings.append(f"Word tokenization failed: {e}")
                    
                    # POS tagging
                    if level in [ProcessingLevel.AGGRESSIVE, ProcessingLevel.DOMAIN_SPECIFIC]:
                        try:
                            result.pos_tags = self.advanced_normalizer.get_pos_tags(cleaned_text)
                        except Exception as e:
                            result.warnings.append(f"POS tagging failed: {e}")
                
                # Named entity recognition
                if level in [ProcessingLevel.AGGRESSIVE, ProcessingLevel.DOMAIN_SPECIFIC]:
                    result.processing_steps.append("named_entity_recognition")
                    try:
                        result.named_entities = self.advanced_normalizer.extract_named_entities(cleaned_text)
                    except Exception as e:
                        result.warnings.append(f"Named entity recognition failed: {e}")
            
            # Step 4: Domain-specific processing
            if level == ProcessingLevel.DOMAIN_SPECIFIC:
                domain = kwargs.get('domain', 'general')
                processed_text = self._apply_domain_specific_processing(processed_text, domain, result)
            
            # Step 5: Final quality assessment
            if processed_text != text:
                result.processing_steps.append("final_quality_assessment")
                final_quality = self.quality_assessor.assess_quality(processed_text)
                
                # Update quality metrics if processing improved quality
                if final_quality.quality_score > result.quality_metrics.quality_score:
                    result.quality_metrics = final_quality
            
            # Step 6: Extract paragraphs from best available text
            best_text = result.get_best_text()
            result.paragraphs = [p.strip() for p in best_text.split('\n\n') if p.strip()]
            
            # Update statistics
            self.processing_stats['total_texts'] += 1
            self.processing_stats['successful_processing'] += 1
            self.processing_stats['quality_distribution'][result.quality_metrics.overall_quality.value] += 1
            self.processing_stats['processing_levels'][level.value] += 1
            
        except Exception as e:
            result.warnings.append(f"Processing failed: {e}")
            logger.error(f"Text preprocessing failed: {e}")
        
        result.processing_time = time.time() - start_time
        self.processing_stats['total_processing_time'] += result.processing_time
        
        return result
    
    def _apply_domain_specific_processing(self, text: str, domain: str, 
                                        result: PreprocessingResult) -> str:
        """Apply domain-specific preprocessing"""
        result.processing_steps.append(f"domain_specific_{domain}")
        
        if domain == 'academic':
            # Academic text preprocessing
            # Remove citation patterns
            text = re.sub(r'\([^)]*\d{4}[^)]*\)', '', text)  # Remove citations
            text = re.sub(r'\[\d+\]', '', text)  # Remove reference numbers
            
        elif domain == 'legal':
            # Legal text preprocessing
            # Preserve case for legal terms
            legal_terms = ['plaintiff', 'defendant', 'whereas', 'heretofore', 'aforementioned']
            # More sophisticated legal text processing would go here
            
        elif domain == 'medical':
            # Medical text preprocessing
            # Preserve medical terminology
            # Remove patient identifiers while preserving medical content
            text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)  # SSN pattern
            
        elif domain == 'news':
            # News text preprocessing
            # Remove datelines, bylines
            text = re.sub(r'^[A-Z\s]+ \([A-Z]+\) -- ', '', text)  # Remove datelines
            
        elif domain == 'social_media':
            # Social media preprocessing
            # Handle hashtags, mentions
            hashtags = re.findall(r'#\w+', text)
            if hashtags:
                result.preserved_elements['hashtags'] = hashtags
            
            mentions = re.findall(r'@\w+', text)
            if mentions:
                result.preserved_elements['mentions'] = mentions
            
            # Replace with placeholders
            text = re.sub(r'#\w+', '[HASHTAG]', text)
            text = re.sub(r'@\w+', '[MENTION]', text)
        
        return text
    
    def preprocess_batch(self, texts: List[str], 
                        level: ProcessingLevel = ProcessingLevel.STANDARD,
                        max_workers: int = 4,
                        **kwargs) -> List[PreprocessingResult]:
        """Preprocess multiple texts in parallel"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all processing tasks
            future_to_text = {
                executor.submit(self.preprocess, text, level, **kwargs): i 
                for i, text in enumerate(texts)
            }
            
            # Collect results in order
            ordered_results = [None] * len(texts)
            
            for future in as_completed(future_to_text):
                index = future_to_text[future]
                try:
                    result = future.result()
                    ordered_results[index] = result
                except Exception as e:
                    logger.error(f"Batch preprocessing failed for text {index}: {e}")
                    # Create failed result
                    failed_result = PreprocessingResult(
                        original_text=texts[index] if index < len(texts) else "",
                        processing_level=level
                    )
                    failed_result.warnings.append(f"Batch processing failed: {e}")
                    ordered_results[index] = failed_result
        
        results = [r for r in ordered_results if r is not None]
        
        logger.info(f"Batch preprocessing completed: {len(results)} texts processed")
        
        return results
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get preprocessing statistics"""
        stats = dict(self.processing_stats)
        
        # Convert Counters to regular dicts
        stats['quality_distribution'] = dict(stats['quality_distribution'])
        stats['processing_levels'] = dict(stats['processing_levels'])
        
        # Calculate derived metrics
        if stats['total_texts'] > 0:
            stats['success_rate'] = stats['successful_processing'] / stats['total_texts']
            stats['average_processing_time'] = stats['total_processing_time'] / stats['total_texts']
        else:
            stats['success_rate'] = 0.0
            stats['average_processing_time'] = 0.0
        
        # Add component information
        stats['components'] = {
            'basic_cleaner': self.basic_cleaner.get_processor_info(),
            'advanced_normalizer': self.advanced_normalizer.get_processor_info(),
            'quality_assessor': {
                'name': self.quality_assessor.name,
                'langdetect_available': self.quality_assessor.lang_detector_available,
                'textstat_available': self.quality_assessor.textstat_available
            }
        }
        
        return stats
    
    def export_processing_results(self, results: List[PreprocessingResult], 
                                export_path: str) -> bool:
        """Export preprocessing results to JSON file"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_results": len(results),
                "processing_stats": self.get_processing_stats(),
                "results": []
            }
            
            for i, result in enumerate(results):
                result_data = {
                    "index": i,
                    "processing_level": result.processing_level.value,
                    "processing_time": result.processing_time,
                    "processing_steps": result.processing_steps,
                    "warnings": result.warnings,
                    "quality_metrics": asdict(result.quality_metrics),
                    "text_stats": {
                        "original_length": len(result.original_text),
                        "cleaned_length": len(result.cleaned_text),
                        "normalized_length": len(result.normalized_text),
                        "sentence_count": len(result.sentences),
                        "paragraph_count": len(result.paragraphs),
                        "token_count": len(result.tokenized_text),
                        "named_entities": len(result.named_entities),
                        "pos_tags": len(result.pos_tags)
                    },
                    "removed_elements": result.removed_elements,
                    "preserved_elements": result.preserved_elements,
                    # Include first 500 characters for preview
                    "text_preview": result.get_best_text()[:500]
                }
                
                export_data["results"].append(result_data)
            
            # Write to file
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(f"Exported preprocessing results to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export preprocessing results: {e}")
            return False


# Factory functions for common use cases
def create_text_preprocessor() -> TextPreprocessor:
    """Create text preprocessor with all available components"""
    return TextPreprocessor()


def preprocess_text_simple(text: str, level: ProcessingLevel = ProcessingLevel.STANDARD) -> str:
    """Simple preprocessing function that returns cleaned text only"""
    preprocessor = create_text_preprocessor()
    result = preprocessor.preprocess(text, level)
    return result.get_best_text()


# Example usage and testing
if __name__ == "__main__":
    def test_text_preprocessing():
        # Create preprocessor
        preprocessor = create_text_preprocessor()
        
        print("Text Preprocessing and Quality Assessment Test")
        print("=" * 60)
        
        # Test texts with different quality levels
        test_texts = [
            # High quality text
            """
            This is a well-written academic paper excerpt that demonstrates proper structure, 
            grammar, and coherent argumentation. The sentences are well-constructed with 
            appropriate length and complexity. Furthermore, it uses transition words effectively 
            to maintain coherence throughout the text.
            """,
            
            # Medium quality text
            """
            this text has some issues with capitalization and structure but its still readable
            and has decent content overall there are no major grammatical errors but the 
            formatting could be better
            """,
            
            # Poor quality text
            """
            txt msg w/ lots of abbrevs & symbols!!! not much structure here... random chars @#$%
            very short sents. no flow. lots of noise 12345 XYZ ABC repeated repeated repeated
            """,
            
            # Very short text
            "Short text.",
            
            # Empty text
            ""
        ]
        
        # Test different processing levels
        levels = [
            ProcessingLevel.MINIMAL,
            ProcessingLevel.STANDARD, 
            ProcessingLevel.AGGRESSIVE
        ]
        
        for i, text in enumerate(test_texts):
            print(f"\nTest Text {i+1}:")
            print("-" * 40)
            print(f"Original: {repr(text[:100])}...")
            
            for level in levels:
                result = preprocessor.preprocess(text.strip(), level)
                
                print(f"\nProcessing Level: {level.value}")
                print(f"  Quality: {result.quality_metrics.overall_quality.value} (score: {result.quality_metrics.quality_score:.1f})")
                print(f"  Processing time: {result.processing_time:.3f}s")
                print(f"  Steps: {', '.join(result.processing_steps)}")
                
                if result.warnings:
                    print(f"  Warnings: {', '.join(result.warnings)}")
                
                print(f"  Language: {result.quality_metrics.detected_language} (conf: {result.quality_metrics.language_confidence:.2f})")
                print(f"  Text lengths: orig={len(result.original_text)}, clean={len(result.cleaned_text)}, norm={len(result.normalized_text)}")
                
                if result.named_entities:
                    entities = [f"{ent['text']}({ent['label']})" for ent in result.named_entities[:3]]
                    print(f"  Named entities: {', '.join(entities)}")
                
                if result.removed_elements:
                    print(f"  Removed elements: {list(result.removed_elements.keys())}")
                
                best_text = result.get_best_text()
                if best_text != text.strip():
                    print(f"  Processed: {repr(best_text[:100])}...")
        
        # Show overall statistics
        print("\n" + "=" * 60)
        print("Processing Statistics:")
        stats = preprocessor.get_processing_stats()
        
        print(f"  Total texts processed: {stats['total_texts']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Average processing time: {stats['average_processing_time']:.3f}s")
        print(f"  Quality distribution: {stats['quality_distribution']}")
        print(f"  Processing levels used: {stats['processing_levels']}")
        
        # Test batch processing
        print(f"\nTesting batch processing with {len(test_texts)} texts...")
        batch_results = preprocessor.preprocess_batch(
            [t.strip() for t in test_texts if t.strip()], 
            ProcessingLevel.STANDARD
        )
        
        print(f"Batch processing completed: {len(batch_results)} results")
        
        # Export results
        if preprocessor.export_processing_results(batch_results, "test_preprocessing_results.json"):
            print("Results exported to test_preprocessing_results.json")
    
    test_text_preprocessing()