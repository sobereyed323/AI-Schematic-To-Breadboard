"""
GPT-4 Vision Integration

This module provides integration with OpenAI's GPT-4 Vision API for advanced
schematic analysis, component identification, and circuit validation.
"""

import os
import time
import json
import base64
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import logging

try:
    from openai import OpenAI
    from openai import APIError as OpenAIAPIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAIAPIError = Exception

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raised when API calls fail."""
    pass


@dataclass
class ValidationResult:
    """Result of circuit validation.
    
    Attributes:
        is_valid: Whether the circuit is valid
        warnings: List of warnings
        errors: List of errors
        suggestions: List of improvement suggestions
    """
    is_valid: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        """String representation of validation result."""
        status = "Valid" if self.is_valid else "Invalid"
        parts = [f"Circuit Validation: {status}"]
        
        if self.errors:
            parts.append(f"Errors ({len(self.errors)}):")
            for error in self.errors:
                parts.append(f"  - {error}")
        
        if self.warnings:
            parts.append(f"Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                parts.append(f"  - {warning}")
        
        if self.suggestions:
            parts.append(f"Suggestions ({len(self.suggestions)}):")
            for suggestion in self.suggestions:
                parts.append(f"  - {suggestion}")
        
        return "\n".join(parts)


class SchematicAnalyzer:
    """Class for analyzing schematics using GPT-4 Vision API.
    
    This class provides methods to analyze circuit schematics, identify
    components, extract connections, and validate circuits using OpenAI's
    GPT-4 Vision API.
    
    Attributes:
        api_key: OpenAI API key
        model: Model name (default: "gpt-4-vision-preview")
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
    
    Example:
        >>> analyzer = SchematicAnalyzer(api_key=os.getenv("OPENAI_API_KEY"))
        >>> result = analyzer.analyze_schematic("schematic.png")
        >>> print(f"Found {len(result['components'])} components")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-vision-preview",
        max_retries: int = 3,
        timeout: int = 30
    ):
        """Initialize the schematic analyzer.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (default: "gpt-4-vision-preview")
            max_retries: Maximum number of retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 30)
        
        Raises:
            ImportError: If openai package is not installed
            ValueError: If API key is not provided
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )
        
        if not PIL_AVAILABLE:
            raise ImportError(
                "Pillow package is required. Install with: pip install pillow"
            )
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided or set in OPENAI_API_KEY environment variable"
            )
        
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Cache for API responses
        self._cache: Dict[str, Any] = {}
    
    def analyze_schematic(
        self,
        image: Union[str, Image.Image],
        detail: str = "high"
    ) -> Dict[str, Any]:
        """Analyze a schematic image and extract components and connections.
        
        Args:
            image: Image file path or PIL Image object
            detail: Analysis detail level ("low" or "high")
        
        Returns:
            Dictionary containing:
                - components: List of identified components
                - connections: List of connections
                - metadata: Additional analysis metadata
        
        Raises:
            APIError: If API call fails
        """
        logger.info("Analyzing schematic with GPT-4 Vision")
        
        # Load and prepare image
        image_data = self._prepare_image(image)
        
        # Check cache
        cache_key = self._get_cache_key(image_data)
        if cache_key in self._cache:
            logger.info("Using cached result")
            return self._cache[cache_key]
        
        # Construct prompt
        prompt = self._construct_analysis_prompt()
        
        # Make API call with retry logic
        response = self._call_api_with_retry(image_data, prompt, detail)
        
        # Parse response
        result = self._parse_analysis_response(response)
        
        # Cache result
        self._cache[cache_key] = result
        
        return result
    
    def identify_components(
        self,
        image: Union[str, Image.Image]
    ) -> List[Dict[str, Any]]:
        """Identify individual components in the schematic.
        
        Args:
            image: Image file path or PIL Image object
        
        Returns:
            List of component dictionaries with type, value, position info
        """
        logger.info("Identifying components")
        
        image_data = self._prepare_image(image)
        prompt = self._construct_component_prompt()
        
        response = self._call_api_with_retry(image_data, prompt, detail="high")
        result = self._parse_component_response(response)
        
        return result
    
    def extract_connections(
        self,
        image: Union[str, Image.Image]
    ) -> List[Dict[str, Any]]:
        """Extract connection information from the schematic.
        
        Args:
            image: Image file path or PIL Image object
        
        Returns:
            List of connection dictionaries
        """
        logger.info("Extracting connections")
        
        image_data = self._prepare_image(image)
        prompt = self._construct_connection_prompt()
        
        response = self._call_api_with_retry(image_data, prompt, detail="high")
        result = self._parse_connection_response(response)
        
        return result
    
    def validate_circuit(
        self,
        components: List[Dict[str, Any]],
        connections: List[Dict[str, Any]]
    ) -> ValidationResult:
        """Validate the circuit for correctness and safety.
        
        Args:
            components: List of components
            connections: List of connections
        
        Returns:
            ValidationResult with warnings, errors, and suggestions
        """
        logger.info("Validating circuit")
        
        # Construct validation prompt
        circuit_description = {
            "components": components,
            "connections": connections
        }
        
        prompt = self._construct_validation_prompt(circuit_description)
        
        # For validation, we don't need image, just text prompt
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use standard GPT-4 for text-only
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert electronics engineer who validates circuits."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                timeout=self.timeout
            )
            
            result_text = response.choices[0].message.content
            return self._parse_validation_response(result_text)
        
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation API call failed: {str(e)}"]
            )
    
    def _prepare_image(
        self,
        image: Union[str, Image.Image]
    ) -> str:
        """Prepare image for API submission.
        
        Args:
            image: Image file path or PIL Image object
        
        Returns:
            Base64-encoded image string
        """
        # Load image if path provided
        if isinstance(image, str):
            image = Image.open(image)
        
        # Resize if too large (max 2048x2048 for GPT-4 Vision)
        max_size = 2048
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save to bytes and encode
        import io
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        image_bytes = buffer.getvalue()
        
        # Encode to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        return f"data:image/jpeg;base64,{image_base64}"
    
    def _construct_analysis_prompt(self) -> str:
        """Construct prompt for full schematic analysis."""
        return """Analyze this electronic schematic and provide a detailed JSON response with:
1. All components (type, value, approximate position)
2. All connections between components
3. Power supply information
4. Any special notes or warnings

Return ONLY valid JSON in this format:
{
    "components": [
        {"id": "R1", "type": "resistor", "value": "220Ω", "position": {"x": 0, "y": 0}},
        ...
    ],
    "connections": [
        {"from": "R1", "to": "LED1", "net": "signal"},
        ...
    ],
    "power_supply": {"voltage": "5V", "type": "DC"},
    "notes": ["..."]
}"""
    
    def _construct_component_prompt(self) -> str:
        """Construct prompt for component identification."""
        return """Identify all electronic components in this schematic.
For each component, provide:
- Type (resistor, capacitor, LED, IC, etc.)
- Value/rating if visible
- Approximate position

Return ONLY valid JSON array:
[
    {"type": "resistor", "value": "220Ω", "position": {"x": 0, "y": 0}},
    ...
]"""
    
    def _construct_connection_prompt(self) -> str:
        """Construct prompt for connection extraction."""
        return """Extract all connections between components in this schematic.
Return ONLY valid JSON array:
[
    {"from": "component1", "to": "component2", "type": "wire"},
    ...
]"""
    
    def _construct_validation_prompt(
        self,
        circuit_description: Dict[str, Any]
    ) -> str:
        """Construct prompt for circuit validation."""
        circuit_json = json.dumps(circuit_description, indent=2)
        return f"""Validate this electronic circuit for correctness and safety:

{circuit_json}

Check for:
1. Short circuits
2. Missing connections
3. Incorrect component values
4. Polarity issues
5. Power supply problems

Return ONLY valid JSON:
{{
    "is_valid": true/false,
    "errors": ["..."],
    "warnings": ["..."],
    "suggestions": ["..."]
}}"""
    
    def _call_api_with_retry(
        self,
        image_data: str,
        prompt: str,
        detail: str = "high"
    ) -> str:
        """Call GPT-4 Vision API with retry logic.
        
        Args:
            image_data: Base64-encoded image
            prompt: Analysis prompt
            detail: Detail level
        
        Returns:
            API response content
        
        Raises:
            APIError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"API call attempt {attempt + 1}/{self.max_retries}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_data,
                                        "detail": detail
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=2000,
                    timeout=self.timeout
                )
                
                return response.choices[0].message.content
            
            except OpenAIAPIError as e:
                last_error = e
                logger.warning(f"API call failed (attempt {attempt + 1}): {e}")
                
                # Exponential backoff
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
            
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {e}")
                break
        
        raise APIError(f"API call failed after {self.max_retries} attempts: {last_error}")
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse full analysis response."""
        try:
            # Extract JSON from response (may have markdown code blocks)
            json_str = self._extract_json(response)
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response: {response}")
            return {
                "components": [],
                "connections": [],
                "error": "Failed to parse API response"
            }
    
    def _parse_component_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse component identification response."""
        try:
            json_str = self._extract_json(response)
            components = json.loads(json_str)
            return components if isinstance(components, list) else []
        except json.JSONDecodeError:
            return []
    
    def _parse_connection_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse connection extraction response."""
        try:
            json_str = self._extract_json(response)
            connections = json.loads(json_str)
            return connections if isinstance(connections, list) else []
        except json.JSONDecodeError:
            return []
    
    def _parse_validation_response(self, response: str) -> ValidationResult:
        """Parse validation response."""
        try:
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            
            return ValidationResult(
                is_valid=data.get("is_valid", False),
                errors=data.get("errors", []),
                warnings=data.get("warnings", []),
                suggestions=data.get("suggestions", [])
            )
        except json.JSONDecodeError:
            return ValidationResult(
                is_valid=False,
                errors=["Failed to parse validation response"]
            )
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from text that may contain markdown code blocks.
        
        Args:
            text: Text potentially containing JSON
        
        Returns:
            Extracted JSON string
        """
        # Remove markdown code blocks if present
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        
        # Try to find JSON object or array
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start = text.find(start_char)
            end = text.rfind(end_char)
            if start != -1 and end != -1:
                return text[start:end + 1]
        
        return text.strip()
    
    def _get_cache_key(self, image_data: str) -> str:
        """Generate cache key from image data.
        
        Args:
            image_data: Base64-encoded image
        
        Returns:
            Hash string for caching
        """
        import hashlib
        return hashlib.md5(image_data.encode()).hexdigest()
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()
        logger.info("Cache cleared")
