"""
Similarity Calculator for multi-modal document similarity computation.

This module computes similarity between documents using various modalities
including content, metadata, temporal, and structural features.
"""

import asyncio
import logging
import re
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class SimilarityFeatures:
    """Features extracted for similarity computation"""
    content_vector: np.ndarray
    metadata_features: Dict[str, Any]
    temporal_features: Dict[str, Any]
    structural_features: Dict[str, Any]


class SimilarityCalculator:
    """Calculates multi-modal similarity between documents"""
    
    def __init__(self):
        self.logger = logger
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9
        )
        self._fitted_tfidf = False
        
    async def calculate_content_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate similarity based on textual content"""
        content1 = doc1.get("content", "")
        content2 = doc2.get("content", "")
        
        if not content1 or not content2:
            return 0.0
            
        # Try multiple approaches for better similarity detection
        try:
            # First try TF-IDF
            texts = [content1, content2]
            
            # Use more lenient TF-IDF settings
            vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=1.0,  # Allow all terms
                token_pattern=r'\b\w+\b',  # Simple word pattern
                lowercase=True
            )
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            tfidf_similarity = similarity_matrix[0, 1]
            
            # Also calculate word overlap similarity
            word_overlap_sim = self._calculate_word_overlap_similarity(content1, content2)
            
            # Also calculate keyword similarity
            keyword_sim = self._calculate_keyword_similarity(content1, content2)
            
            # Combine similarities
            combined_similarity = max(tfidf_similarity, word_overlap_sim * 0.7, keyword_sim * 0.8)
            
            self.logger.debug(f"Content similarity - TF-IDF: {tfidf_similarity:.3f}, "
                            f"Word overlap: {word_overlap_sim:.3f}, "
                            f"Keyword: {keyword_sim:.3f}, "
                            f"Combined: {combined_similarity:.3f}")
            
            return float(combined_similarity)
            
        except Exception as e:
            self.logger.warning(f"Error calculating content similarity: {e}")
            # Fallback to simple word overlap
            return self._calculate_word_overlap_similarity(content1, content2)
    
    def _calculate_word_overlap_similarity(self, text1: str, text2: str) -> float:
        """Fallback similarity based on word overlap"""
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_keyword_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity based on key terms and concepts"""
        # Define important AI/ML/tech keywords
        ai_keywords = {
            'artificial', 'intelligence', 'machine', 'learning', 'neural', 'networks', 
            'deep', 'ai', 'ml', 'algorithm', 'model', 'data', 'computer', 'vision'
        }
        
        climate_keywords = {
            'climate', 'change', 'environment', 'sustainability', 'renewable', 
            'energy', 'carbon', 'emissions', 'global', 'warming', 'green'
        }
        
        blockchain_keywords = {
            'blockchain', 'cryptocurrency', 'bitcoin', 'smart', 'contracts', 
            'crypto', 'digital', 'currency', 'decentralized'
        }
        
        healthcare_keywords = {
            'healthcare', 'medical', 'health', 'medicine', 'diagnosis', 
            'treatment', 'patient', 'disease', 'clinical'
        }
        
        # Extract words from both texts
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        # Calculate keyword category matches
        similarities = []
        
        for keyword_set in [ai_keywords, climate_keywords, blockchain_keywords, healthcare_keywords]:
            matches1 = len(words1.intersection(keyword_set))
            matches2 = len(words2.intersection(keyword_set))
            
            if matches1 > 0 and matches2 > 0:
                # Both texts have keywords from this category
                category_sim = min(matches1, matches2) / max(matches1, matches2)
                similarities.append(category_sim)
        
        # Return highest category similarity
        return max(similarities) if similarities else 0.0
    
    async def calculate_metadata_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate similarity based on metadata"""
        metadata1 = doc1.get("metadata", {})
        metadata2 = doc2.get("metadata", {})
        
        if not metadata1 or not metadata2:
            return 0.0
        
        similarity_scores = []
        
        # Author similarity
        authors1 = set(metadata1.get("authors", []))
        authors2 = set(metadata2.get("authors", []))
        if authors1 or authors2:
            author_intersection = authors1.intersection(authors2)
            author_union = authors1.union(authors2)
            author_sim = len(author_intersection) / len(author_union) if author_union else 0.0
            similarity_scores.append(author_sim * 0.3)  # Weight: 30%
        
        # Keyword similarity (improved with semantic matching)
        keywords1 = set(kw.lower() for kw in metadata1.get("keywords", []))
        keywords2 = set(kw.lower() for kw in metadata2.get("keywords", []))
        if keywords1 or keywords2:
            # Direct intersection
            keyword_intersection = keywords1.intersection(keywords2)
            keyword_union = keywords1.union(keywords2)
            direct_sim = len(keyword_intersection) / len(keyword_union) if keyword_union else 0.0
            
            # Semantic similarity for related keywords
            semantic_matches = 0
            related_keywords = {
                'ai': ['artificial intelligence', 'machine learning', 'ml'],
                'healthcare': ['medical', 'health', 'medicine'],
                'climate': ['environment', 'environmental', 'sustainability'],
                'energy': ['renewable', 'solar', 'wind']
            }
            
            for kw1 in keywords1:
                for kw2 in keywords2:
                    if kw1 != kw2:  # Don't double count exact matches
                        for main_kw, related in related_keywords.items():
                            if (kw1 == main_kw and kw2 in related) or (kw2 == main_kw and kw1 in related) or (kw1 in related and kw2 in related):
                                semantic_matches += 1
                                break
            
            # Combine direct and semantic similarities
            semantic_bonus = min(0.5, semantic_matches * 0.3)  # Increased semantic bonus
            keyword_sim = direct_sim + semantic_bonus
            
            # Boost score if there's any keyword overlap
            if keyword_intersection or semantic_matches:
                # Higher boost for combination of direct and semantic matches
                if keyword_intersection and semantic_matches:
                    keyword_sim = max(keyword_sim, 0.8)  # 80% for both types
                else:
                    keyword_sim = max(keyword_sim, 0.6)  # 60% for one type
            
            similarity_scores.append(keyword_sim * 0.5)  # Weight: 50% (increased from 40%)
        
        # Reference similarity
        refs1 = set(metadata1.get("references", []))
        refs2 = set(metadata2.get("references", []))
        if refs1 or refs2:
            ref_intersection = refs1.intersection(refs2)
            ref_union = refs1.union(refs2)
            ref_sim = len(ref_intersection) / len(ref_union) if ref_union else 0.0
            similarity_scores.append(ref_sim * 0.15)  # Weight: 15%
        
        # Temporal similarity (same date/time period)
        date1 = metadata1.get("date", "")
        date2 = metadata2.get("date", "")
        if date1 and date2:
            # Simple date similarity - same month/year
            date_sim = 1.0 if date1[:7] == date2[:7] else 0.0  # Compare YYYY-MM
            similarity_scores.append(date_sim * 0.05)  # Weight: 5%
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    async def calculate_temporal_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate similarity based on temporal features"""
        metadata1 = doc1.get("metadata", {})
        metadata2 = doc2.get("metadata", {})
        
        date1 = metadata1.get("date", "")
        date2 = metadata2.get("date", "")
        
        if not date1 or not date2:
            return 0.0
        
        try:
            # Parse dates (assuming YYYY-MM-DD format)
            year1, month1 = date1.split("-")[:2]
            year2, month2 = date2.split("-")[:2]
            
            year_diff = abs(int(year1) - int(year2))
            month_diff = abs(int(month1) - int(month2))
            
            # Calculate temporal similarity (closer dates = higher similarity)
            if year_diff == 0:
                if month_diff == 0:
                    return 1.0  # Same month
                elif month_diff <= 3:
                    return 0.8  # Same quarter
                else:
                    return 0.6  # Same year
            elif year_diff == 1:
                return 0.4  # Adjacent years
            elif year_diff <= 3:
                return 0.2  # Within 3 years
            else:
                return 0.0  # Too far apart
                
        except (ValueError, IndexError):
            self.logger.warning(f"Failed to parse dates: {date1}, {date2}")
            return 0.0
    
    async def calculate_structural_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate similarity based on document structure"""
        content1 = doc1.get("content", "")
        content2 = doc2.get("content", "")
        
        if not content1 or not content2:
            return 0.0
        
        # Extract structural features
        features1 = self._extract_structural_features(content1)
        features2 = self._extract_structural_features(content2)
        
        similarity_scores = []
        
        # Heading similarity
        headings1 = set(features1["headings"])
        headings2 = set(features2["headings"])
        if headings1 or headings2:
            heading_intersection = headings1.intersection(headings2)
            heading_union = headings1.union(headings2)
            heading_sim = len(heading_intersection) / len(heading_union) if heading_union else 0.0
            similarity_scores.append(heading_sim * 0.4)
        
        # Structure type similarity
        if features1["structure_type"] == features2["structure_type"]:
            similarity_scores.append(0.3)
        
        # Length similarity
        len1, len2 = features1["length"], features2["length"]
        if len1 > 0 and len2 > 0:
            length_ratio = min(len1, len2) / max(len1, len2)
            similarity_scores.append(length_ratio * 0.2)
        
        # Formatting similarity
        format1 = set(features1["formatting"])
        format2 = set(features2["formatting"])
        if format1 or format2:
            format_intersection = format1.intersection(format2)
            format_union = format1.union(format2)
            format_sim = len(format_intersection) / len(format_union) if format_union else 0.0
            similarity_scores.append(format_sim * 0.1)
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _extract_structural_features(self, content: str) -> Dict[str, Any]:
        """Extract structural features from document content"""
        features = {
            "headings": [],
            "structure_type": "unknown",
            "length": len(content),
            "formatting": []
        }
        
        # Extract headings
        heading_matches = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        features["headings"] = [h.lower().strip() for h in heading_matches]
        
        # Determine structure type
        content_lower = content.lower()
        if any(word in content_lower for word in ["abstract", "introduction", "conclusion", "references"]):
            features["structure_type"] = "academic_paper"
        elif any(word in content_lower for word in ["experiment", "data", "results", "analysis"]):
            features["structure_type"] = "research_report"
        elif "review" in content_lower or "survey" in content_lower:
            features["structure_type"] = "review_article"
        else:
            features["structure_type"] = "general_document"
        
        # Extract formatting features
        if re.search(r'\*\*.*?\*\*', content):
            features["formatting"].append("bold")
        if re.search(r'\*.*?\*', content):
            features["formatting"].append("italic")
        if re.search(r'^\s*[-*]\s+', content, re.MULTILINE):
            features["formatting"].append("bullet_list")
        if re.search(r'^\s*\d+\.\s+', content, re.MULTILINE):
            features["formatting"].append("numbered_list")
        
        return features
    
    async def calculate_combined_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate weighted combination of all similarity types"""
        # Calculate individual similarities
        content_sim = await self.calculate_content_similarity(doc1, doc2)
        metadata_sim = await self.calculate_metadata_similarity(doc1, doc2)
        temporal_sim = await self.calculate_temporal_similarity(doc1, doc2)
        structural_sim = await self.calculate_structural_similarity(doc1, doc2)
        
        # Weighted combination
        weights = {
            "content": 0.5,
            "metadata": 0.25,
            "temporal": 0.1,
            "structural": 0.15
        }
        
        combined_similarity = (
            content_sim * weights["content"] +
            metadata_sim * weights["metadata"] +
            temporal_sim * weights["temporal"] +
            structural_sim * weights["structural"]
        )
        
        self.logger.debug(f"Combined similarity: content={content_sim:.3f}, metadata={metadata_sim:.3f}, "
                         f"temporal={temporal_sim:.3f}, structural={structural_sim:.3f}, "
                         f"combined={combined_similarity:.3f}")
        
        return combined_similarity
    
    async def compute_similarity_matrix(self, documents: List[Dict[str, Any]]) -> np.ndarray:
        """Compute similarity matrix for all document pairs"""
        n_docs = len(documents)
        similarity_matrix = np.zeros((n_docs, n_docs))
        
        # Fill diagonal with 1.0 (documents are identical to themselves)
        np.fill_diagonal(similarity_matrix, 1.0)
        
        # Compute pairwise similarities
        for i in range(n_docs):
            for j in range(i + 1, n_docs):
                similarity = await self.calculate_combined_similarity(documents[i], documents[j])
                similarity_matrix[i, j] = similarity
                similarity_matrix[j, i] = similarity  # Matrix is symmetric
        
        return similarity_matrix
    
    async def extract_features(self, documents: List[Dict[str, Any]]) -> List[SimilarityFeatures]:
        """Extract features from documents for similarity computation"""
        features_list = []
        
        # Prepare content for TF-IDF
        contents = [doc.get("content", "") for doc in documents]
        
        try:
            if contents and any(content.strip() for content in contents):
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(contents)
                self._fitted_tfidf = True
            else:
                # Handle empty content case
                tfidf_matrix = np.zeros((len(documents), 1))
        except Exception as e:
            self.logger.warning(f"Error in TF-IDF processing: {e}")
            tfidf_matrix = np.zeros((len(documents), 100))  # Default feature size
        
        for i, doc in enumerate(documents):
            # Content vector
            if hasattr(tfidf_matrix, 'toarray'):
                content_vector = tfidf_matrix[i].toarray().flatten()
            else:
                content_vector = tfidf_matrix[i] if isinstance(tfidf_matrix, np.ndarray) else np.zeros(100)
            
            # Metadata features
            metadata = doc.get("metadata", {})
            metadata_features = {
                "num_authors": len(metadata.get("authors", [])),
                "num_keywords": len(metadata.get("keywords", [])),
                "num_references": len(metadata.get("references", [])),
                "has_date": bool(metadata.get("date"))
            }
            
            # Temporal features
            temporal_features = {
                "date": metadata.get("date", ""),
                "year": self._extract_year(metadata.get("date", "")),
                "month": self._extract_month(metadata.get("date", ""))
            }
            
            # Structural features
            content = doc.get("content", "")
            structural_features = self._extract_structural_features(content)
            
            features = SimilarityFeatures(
                content_vector=content_vector,
                metadata_features=metadata_features,
                temporal_features=temporal_features,
                structural_features=structural_features
            )
            
            features_list.append(features)
        
        return features_list
    
    def _extract_year(self, date_str: str) -> int:
        """Extract year from date string"""
        try:
            return int(date_str.split("-")[0]) if date_str else 0
        except (ValueError, IndexError):
            return 0
    
    def _extract_month(self, date_str: str) -> int:
        """Extract month from date string"""
        try:
            return int(date_str.split("-")[1]) if date_str and len(date_str.split("-")) > 1 else 0
        except (ValueError, IndexError):
            return 0