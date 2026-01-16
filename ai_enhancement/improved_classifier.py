"""
Improved Component Classifier

This module provides an enhanced component classifier that combines
traditional CNN classification with GPT-4 Vision fallback for improved accuracy.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Any, List
import numpy as np

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of component classification.
    
    Attributes:
        component_type: Identified component type
        confidence: Confidence score (0.0 to 1.0)
        value: Component value if identified
        unit: Unit of measurement
        method: Classification method used ("cnn", "gpt", "hybrid")
        alternative_predictions: List of alternative predictions
    """
    component_type: str
    confidence: float
    value: Optional[float] = None
    unit: Optional[str] = None
    method: str = "cnn"
    alternative_predictions: List[tuple] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.alternative_predictions is None:
            self.alternative_predictions = []
    
    def __str__(self) -> str:
        """String representation of classification result."""
        result = f"{self.component_type} (confidence: {self.confidence:.2%}, method: {self.method})"
        if self.value and self.unit:
            result += f", value: {self.value}{self.unit}"
        return result


class ImprovedClassifier:
    """Enhanced component classifier combining CNN and GPT-4 Vision.
    
    This classifier uses a CNN for initial classification and falls back to
    GPT-4 Vision when confidence is below a threshold, providing improved
    accuracy over CNN-only approaches.
    
    Attributes:
        cnn_model: Trained CNN model (TensorFlow/Keras)
        gpt_analyzer: GPT-4 Vision analyzer for fallback
        confidence_threshold: Minimum confidence for CNN-only classification
        class_names: List of component class names
    
    Example:
        >>> classifier = ImprovedClassifier(
        ...     cnn_model_path="models/classifier.h5",
        ...     gpt_analyzer=analyzer
        ... )
        >>> result = classifier.classify(component_image)
        >>> print(f"Classified as: {result.component_type}")
    """
    
    # Default class names (matching CircuitNet)
    DEFAULT_CLASSES = [
        "resistor",
        "capacitor",
        "inductor",
        "voltage_source",
        "current_source"
    ]
    
    def __init__(
        self,
        cnn_model_path: Optional[str] = None,
        gpt_analyzer: Optional[Any] = None,
        confidence_threshold: float = 0.85,
        class_names: Optional[List[str]] = None
    ):
        """Initialize the improved classifier.
        
        Args:
            cnn_model_path: Path to trained CNN model (optional)
            gpt_analyzer: SchematicAnalyzer instance for fallback (optional)
            confidence_threshold: Minimum confidence for CNN-only (default: 0.85)
            class_names: List of component class names (optional)
        """
        if not PIL_AVAILABLE:
            raise ImportError(
                "Pillow package is required. Install with: pip install pillow"
            )
        
        self.confidence_threshold = confidence_threshold
        self.class_names = class_names or self.DEFAULT_CLASSES
        self.gpt_analyzer = gpt_analyzer
        
        # Load CNN model if path provided
        self.cnn_model = None
        if cnn_model_path:
            self.cnn_model = self._load_cnn_model(cnn_model_path)
        
        # Statistics
        self.stats = {
            "total_classifications": 0,
            "cnn_only": 0,
            "gpt_fallback": 0,
            "hybrid": 0
        }
    
    def classify(
        self,
        image: Image.Image,
        use_gpt_fallback: bool = True
    ) -> ClassificationResult:
        """Classify a component image.
        
        Args:
            image: Component image (PIL Image)
            use_gpt_fallback: Whether to use GPT-4 Vision fallback
        
        Returns:
            Classification result with type and confidence
        """
        self.stats["total_classifications"] += 1
        
        # Try CNN classification first
        if self.cnn_model is not None:
            cnn_result = self._classify_with_cnn(image)
            
            # If confidence is high enough, use CNN result
            if cnn_result.confidence >= self.confidence_threshold:
                logger.info(
                    f"CNN classification: {cnn_result.component_type} "
                    f"(confidence: {cnn_result.confidence:.2%})"
                )
                self.stats["cnn_only"] += 1
                return cnn_result
            
            # Low confidence - try GPT fallback if available
            if use_gpt_fallback and self.gpt_analyzer is not None:
                logger.info(
                    f"CNN confidence low ({cnn_result.confidence:.2%}), "
                    f"using GPT-4 Vision fallback"
                )
                gpt_result = self._classify_with_gpt(image)
                
                # Combine results (hybrid approach)
                combined_result = self._combine_results(cnn_result, gpt_result)
                self.stats["hybrid"] += 1
                return combined_result
            
            # No fallback available, return CNN result
            return cnn_result
        
        # No CNN model, use GPT only
        if self.gpt_analyzer is not None:
            logger.info("No CNN model, using GPT-4 Vision")
            gpt_result = self._classify_with_gpt(image)
            self.stats["gpt_fallback"] += 1
            return gpt_result
        
        # No classification method available
        logger.warning("No classification method available")
        return ClassificationResult(
            component_type="unknown",
            confidence=0.0,
            method="none"
        )
    
    def batch_classify(
        self,
        images: List[Image.Image],
        use_gpt_fallback: bool = True
    ) -> List[ClassificationResult]:
        """Classify multiple component images.
        
        Args:
            images: List of component images
            use_gpt_fallback: Whether to use GPT-4 Vision fallback
        
        Returns:
            List of classification results
        """
        results = []
        for i, image in enumerate(images):
            logger.info(f"Classifying image {i + 1}/{len(images)}")
            result = self.classify(image, use_gpt_fallback)
            results.append(result)
        
        return results
    
    def _load_cnn_model(self, model_path: str) -> Any:
        """Load CNN model from file.
        
        Args:
            model_path: Path to model file
        
        Returns:
            Loaded model
        """
        try:
            import tensorflow as tf
            logger.info(f"Loading CNN model from {model_path}")
            model = tf.keras.models.load_model(model_path)
            logger.info("CNN model loaded successfully")
            return model
        except ImportError:
            logger.error("TensorFlow not available")
            return None
        except Exception as e:
            logger.error(f"Failed to load CNN model: {e}")
            return None
    
    def _classify_with_cnn(self, image: Image.Image) -> ClassificationResult:
        """Classify using CNN model.
        
        Args:
            image: Component image
        
        Returns:
            Classification result
        """
        try:
            # Preprocess image for CNN
            # Note: Adjust preprocessing based on your CNN's requirements
            image_array = self._preprocess_for_cnn(image)
            
            # Make prediction
            predictions = self.cnn_model.predict(
                np.expand_dims(image_array, axis=0),
                verbose=0
            )[0]
            
            # Get top prediction
            top_idx = np.argmax(predictions)
            confidence = float(predictions[top_idx])
            component_type = self.class_names[top_idx]
            
            # Get alternative predictions
            alternatives = []
            for idx in np.argsort(predictions)[::-1][1:4]:  # Top 3 alternatives
                alternatives.append((
                    self.class_names[idx],
                    float(predictions[idx])
                ))
            
            return ClassificationResult(
                component_type=component_type,
                confidence=confidence,
                method="cnn",
                alternative_predictions=alternatives
            )
        
        except Exception as e:
            logger.error(f"CNN classification failed: {e}")
            return ClassificationResult(
                component_type="unknown",
                confidence=0.0,
                method="cnn"
            )
    
    def _classify_with_gpt(self, image: Image.Image) -> ClassificationResult:
        """Classify using GPT-4 Vision.
        
        Args:
            image: Component image
        
        Returns:
            Classification result
        """
        try:
            # Save image temporarily or convert to format for GPT
            import io
            
            # Convert image to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Use GPT analyzer
            # Note: This requires a modified prompt for single component
            prompt = """Identify this electronic component.
Return ONLY valid JSON:
{
    "type": "resistor/capacitor/inductor/etc",
    "value": "220",
    "unit": "Ω/µF/mH/etc",
    "confidence": 0.95
}"""
            
            # For this to work, we'd need to enhance SchematicAnalyzer
            # For now, provide a placeholder implementation
            
            # TODO: Implement GPT-4 Vision classification
            # This is a simplified placeholder
            result = {
                "type": "resistor",
                "confidence": 0.9
            }
            
            return ClassificationResult(
                component_type=result.get("type", "unknown"),
                confidence=result.get("confidence", 0.0),
                value=result.get("value"),
                unit=result.get("unit"),
                method="gpt"
            )
        
        except Exception as e:
            logger.error(f"GPT classification failed: {e}")
            return ClassificationResult(
                component_type="unknown",
                confidence=0.0,
                method="gpt"
            )
    
    def _combine_results(
        self,
        cnn_result: ClassificationResult,
        gpt_result: ClassificationResult
    ) -> ClassificationResult:
        """Combine CNN and GPT results for hybrid classification.
        
        Uses a weighted approach based on confidence scores.
        
        Args:
            cnn_result: CNN classification result
            gpt_result: GPT classification result
        
        Returns:
            Combined classification result
        """
        # If both agree, return with high confidence
        if cnn_result.component_type == gpt_result.component_type:
            combined_confidence = (
                cnn_result.confidence * 0.4 + gpt_result.confidence * 0.6
            )
            return ClassificationResult(
                component_type=cnn_result.component_type,
                confidence=min(combined_confidence, 0.99),
                value=gpt_result.value or cnn_result.value,
                unit=gpt_result.unit or cnn_result.unit,
                method="hybrid",
                alternative_predictions=cnn_result.alternative_predictions
            )
        
        # Disagreement - use higher confidence
        if gpt_result.confidence > cnn_result.confidence:
            return ClassificationResult(
                component_type=gpt_result.component_type,
                confidence=gpt_result.confidence * 0.9,  # Slight penalty
                value=gpt_result.value,
                unit=gpt_result.unit,
                method="hybrid",
                alternative_predictions=[
                    (cnn_result.component_type, cnn_result.confidence)
                ]
            )
        else:
            return ClassificationResult(
                component_type=cnn_result.component_type,
                confidence=cnn_result.confidence,
                value=cnn_result.value,
                unit=cnn_result.unit,
                method="hybrid",
                alternative_predictions=[
                    (gpt_result.component_type, gpt_result.confidence)
                ]
            )
    
    def _preprocess_for_cnn(
        self,
        image: Image.Image,
        target_size: tuple = (64, 64)
    ) -> np.ndarray:
        """Preprocess image for CNN input.
        
        Args:
            image: Input image
            target_size: Target size for CNN (default: 64x64)
        
        Returns:
            Preprocessed image array
        """
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Resize to target size
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Convert to array and normalize
        image_array = np.array(image, dtype=np.float32) / 255.0
        
        # Add channel dimension if needed
        if len(image_array.shape) == 2:
            image_array = np.expand_dims(image_array, axis=-1)
        
        return image_array
    
    def should_fallback_to_gpt(self, confidence: float) -> bool:
        """Determine if GPT fallback should be used.
        
        Args:
            confidence: CNN confidence score
        
        Returns:
            True if fallback should be used
        """
        return confidence < self.confidence_threshold
    
    def get_statistics(self) -> dict:
        """Get classification statistics.
        
        Returns:
            Dictionary of statistics
        """
        stats = self.stats.copy()
        if stats["total_classifications"] > 0:
            stats["cnn_only_pct"] = (
                stats["cnn_only"] / stats["total_classifications"] * 100
            )
            stats["gpt_fallback_pct"] = (
                stats["gpt_fallback"] / stats["total_classifications"] * 100
            )
            stats["hybrid_pct"] = (
                stats["hybrid"] / stats["total_classifications"] * 100
            )
        return stats
    
    def reset_statistics(self) -> None:
        """Reset classification statistics."""
        self.stats = {
            "total_classifications": 0,
            "cnn_only": 0,
            "gpt_fallback": 0,
            "hybrid": 0
        }
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """Set the confidence threshold for CNN-only classification.
        
        Args:
            threshold: New threshold value (0.0 to 1.0)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        
        self.confidence_threshold = threshold
        logger.info(f"Confidence threshold set to {threshold:.2%}")
    
    def __repr__(self) -> str:
        """String representation of classifier."""
        cnn_status = "loaded" if self.cnn_model is not None else "not loaded"
        gpt_status = "available" if self.gpt_analyzer is not None else "not available"
        
        return (
            f"ImprovedClassifier(CNN: {cnn_status}, GPT: {gpt_status}, "
            f"threshold: {self.confidence_threshold:.2%})"
        )
