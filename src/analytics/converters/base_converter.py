#!/usr/bin/env python3
"""
Base Converter - Abstract base class for cross-modal converters

Defines the interface that all cross-modal converters must implement
for consistent behavior across different format transformations.
"""

from abc import ABC, abstractmethod
from typing import Any, List

from ..cross_modal_types import DataFormat


class BaseConverter(ABC):
    """Abstract base class for format converters"""
    
    @abstractmethod
    async def convert(self, data: Any, target_format: DataFormat, **kwargs) -> Any:
        """
        Convert data to target format
        
        Args:
            data: Input data to convert
            target_format: Target format for conversion
            **kwargs: Additional conversion parameters
            
        Returns:
            Converted data
        """
        pass
    
    @abstractmethod
    async def validate_input(self, data: Any) -> bool:
        """
        Validate input data for conversion
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid for conversion
        """
        pass
    
    @abstractmethod
    def get_supported_targets(self) -> List[DataFormat]:
        """
        Get list of supported target formats
        
        Returns:
            List of supported DataFormat values
        """
        pass