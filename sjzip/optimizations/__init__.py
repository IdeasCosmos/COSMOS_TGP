"""
SJZIP Optimization Modules
===========================

Advanced compression optimizations with security hardening.
"""

__version__ = "2.0.0"

from .hilbert_optimizer import HilbertCurve3D
from .integer_scaler import IntegerCoordinateScaler, ScalingConfig
from .quaternion_optimizer import QuaternionSpiralEncoder, QuaternionOptimizedMapper
from .optimized_sjzip import OptimizedSJZIPCodec, OptimizedDotRecord

__all__ = [
    'HilbertCurve3D',
    'IntegerCoordinateScaler',
    'ScalingConfig',
    'QuaternionSpiralEncoder',
    'QuaternionOptimizedMapper',
    'OptimizedSJZIPCodec',
    'OptimizedDotRecord',
]
