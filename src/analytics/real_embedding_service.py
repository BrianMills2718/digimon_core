"""Real embedding service using state-of-the-art transformer models."""

import asyncio
import logging
from typing import List, Dict, Any
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from PIL import Image
import torchvision.transforms as transforms

logger = logging.getLogger(__name__)


class RealEmbeddingService:
    """Real embedding service using transformer models for multi-modal embeddings."""
    
    def __init__(self, device: str = None):
        """Initialize embedding models.
        
        Args:
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
        """
        # Auto-detect device if not specified
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        logger.info(f"Initializing RealEmbeddingService on device: {self.device}")
        
        # Text embeddings using Sentence-BERT
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
        
        # Image embeddings using CLIP
        try:
            from transformers import CLIPProcessor, CLIPModel
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model.to(self.device)
            self.clip_model.eval()
            self.has_clip = True
        except Exception as e:
            logger.warning(f"Failed to load CLIP model: {e}. Image embeddings will be limited.")
            self.has_clip = False
            
        # Structured data encoder
        self.structured_encoder = self._init_structured_encoder()
        
    async def generate_text_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate real text embeddings using Sentence-BERT.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Array of embeddings with shape (n_texts, embedding_dim)
        """
        if not texts:
            return np.array([])
            
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, 
                lambda: self.text_model.encode(
                    texts,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                    batch_size=32
                )
            )
            
            logger.info(f"Generated {len(texts)} text embeddings with shape {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate text embeddings: {e}")
            # Return zero embeddings as fallback
            return np.zeros((len(texts), 384))
    
    async def generate_image_embeddings(self, image_paths: List[str]) -> np.ndarray:
        """Generate real image embeddings using CLIP.
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            Array of embeddings with shape (n_images, embedding_dim)
        """
        if not image_paths:
            return np.array([])
            
        if not self.has_clip:
            logger.warning("CLIP model not available, using fallback image embeddings")
            return await self._generate_fallback_image_embeddings(image_paths)
            
        embeddings = []
        
        for path in image_paths:
            try:
                # Load and process image
                image = Image.open(path).convert('RGB')
                inputs = self.clip_processor(images=image, return_tensors="pt")
                
                # Move inputs to device
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Generate embedding
                with torch.no_grad():
                    outputs = self.clip_model.get_image_features(**inputs)
                    embedding = outputs.cpu().numpy().squeeze()
                    embeddings.append(embedding)
                    
            except Exception as e:
                logger.error(f"Failed to process image {path}: {e}")
                # Use zero vector for failed images
                embeddings.append(np.zeros(512))
        
        embeddings_array = np.array(embeddings)
        logger.info(f"Generated {len(image_paths)} image embeddings with shape {embeddings_array.shape}")
        return embeddings_array
    
    async def generate_structured_embeddings(self, structured_data: List[Dict[str, Any]]) -> np.ndarray:
        """Generate embeddings for structured data.
        
        Args:
            structured_data: List of dictionaries containing structured data
            
        Returns:
            Array of embeddings with shape (n_data, embedding_dim)
        """
        if not structured_data:
            return np.array([])
            
        embeddings = []
        
        for data in structured_data:
            try:
                # Extract features and create embedding
                feature_vector = self._extract_features(data)
                
                # Convert to tensor and process
                feature_tensor = torch.FloatTensor(feature_vector).to(self.device)
                
                with torch.no_grad():
                    embedding = self.structured_encoder(feature_tensor)
                    embeddings.append(embedding.cpu().numpy())
                    
            except Exception as e:
                logger.error(f"Failed to process structured data: {e}")
                # Use zero vector for failed data
                embeddings.append(np.zeros(256))
        
        embeddings_array = np.array(embeddings)
        logger.info(f"Generated {len(structured_data)} structured embeddings with shape {embeddings_array.shape}")
        return embeddings_array
    
    def _init_structured_encoder(self):
        """Initialize encoder for structured data."""
        import torch.nn as nn
        
        class StructuredEncoder(nn.Module):
            def __init__(self, input_dim=100, hidden_dim=128, output_dim=256):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.BatchNorm1d(hidden_dim),
                    nn.Dropout(0.1),
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.ReLU(),
                    nn.BatchNorm1d(hidden_dim),
                    nn.Dropout(0.1),
                    nn.Linear(hidden_dim, output_dim),
                    nn.Tanh()
                )
                
            def forward(self, x):
                return self.encoder(x)
                
        encoder = StructuredEncoder()
        encoder.to(self.device)
        encoder.eval()
        return encoder
    
    def _extract_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from structured data.
        
        Args:
            data: Dictionary containing structured data
            
        Returns:
            Feature vector of fixed size
        """
        features = []
        
        # Extract numerical features
        for key, value in sorted(data.items()):
            if isinstance(value, (int, float)):
                features.append(float(value))
            elif isinstance(value, bool):
                features.append(1.0 if value else 0.0)
            elif isinstance(value, str):
                # Use string length and hash for basic encoding
                features.extend([
                    len(value) / 100.0,  # Normalized length
                    (hash(value) % 10000) / 10000.0  # Normalized hash
                ])
            elif isinstance(value, list):
                # Use list length
                features.append(len(value) / 100.0)
            elif isinstance(value, dict):
                # Recursively extract from nested dict (limited depth)
                if len(features) < 80:  # Leave room for other features
                    sub_features = self._extract_features(value)[:10]
                    features.extend(sub_features)
        
        # Pad or truncate to fixed size
        feature_array = np.array(features[:100], dtype=np.float32)
        if len(feature_array) < 100:
            feature_array = np.pad(
                feature_array, 
                (0, 100 - len(feature_array)),
                mode='constant',
                constant_values=0
            )
            
        return feature_array
    
    async def _generate_fallback_image_embeddings(self, image_paths: List[str]) -> np.ndarray:
        """Generate basic image embeddings when CLIP is not available.
        
        Uses basic image statistics as features.
        """
        embeddings = []
        
        for path in image_paths:
            try:
                image = Image.open(path).convert('RGB')
                # Resize to standard size
                image = image.resize((224, 224))
                
                # Convert to numpy array
                img_array = np.array(image)
                
                # Extract basic features
                features = []
                
                # Color histogram features
                for channel in range(3):
                    hist, _ = np.histogram(img_array[:, :, channel], bins=16, range=(0, 256))
                    features.extend(hist / hist.sum())  # Normalize
                
                # Basic statistics
                features.extend([
                    img_array.mean() / 255.0,
                    img_array.std() / 255.0,
                    (img_array > 128).mean(),  # Brightness ratio
                ])
                
                # Pad to 512 dimensions (CLIP embedding size)
                feature_array = np.array(features)
                if len(feature_array) < 512:
                    feature_array = np.pad(
                        feature_array,
                        (0, 512 - len(feature_array)),
                        mode='constant'
                    )
                
                embeddings.append(feature_array[:512])
                
            except Exception as e:
                logger.error(f"Failed to process image {path}: {e}")
                embeddings.append(np.zeros(512))
        
        return np.array(embeddings)
    
    def get_embedding_dimensions(self) -> Dict[str, int]:
        """Get the dimensionality of embeddings for each modality.
        
        Returns:
            Dictionary mapping modality to embedding dimension
        """
        return {
            'text': 384,  # Sentence-BERT all-MiniLM-L6-v2
            'image': 512,  # CLIP ViT-B/32
            'structured': 256  # Custom encoder
        }