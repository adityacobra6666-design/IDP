from typing import Optional, Any, Dict

class NeuroTrackException(Exception):
    """Base exception class for NeuroTrack AI application."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ResourceNotFoundException(NeuroTrackException):
    """Raised when a requested resource (child, session, task) is not found."""
    pass

class VideoProcessingException(NeuroTrackException):
    """Raised when video file validation or decoding fails."""
    pass

class QualityAssessmentFailedException(NeuroTrackException):
    """Raised when input quality is insufficient for analysis."""
    pass

class AnalysisException(NeuroTrackException):
    """Raised when feature extraction or task analysis fails."""
    pass
