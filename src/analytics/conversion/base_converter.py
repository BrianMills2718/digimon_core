#!/usr/bin/env python3
"""
Base converter interface for cross-modal conversion.

Defines the abstract interface that all specific format converters must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, List

from .models import DataFormat


class BaseConverter(ABC):
    """Abstract base class for format converters"""
    
    @abstractmethod
    async def convert(self, data: Any, target_format: DataFormat, **kwargs) -> Any:
        """Convert data to target format"""
        pass
    
    @abstractmethod
    async def validate_input(self, data: Any) -> bool:
        """Validate input data for conversion"""
        pass
    
    @abstractmethod
    def get_supported_targets(self) -> List[DataFormat]:
        """Get list of supported target formats"""
        pass