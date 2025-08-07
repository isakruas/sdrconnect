"""
Copyright 2025 Isak Ruas

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Base SDR client class.

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import numpy as np

from ..core.config import SDRConfig


class BaseSDRClient(ABC):
    """Abstract base class for all SDR clients."""

    def __init__(self, config: Optional[SDRConfig] = None):
        """Initialize SDR client with configuration."""
        self.config = config or SDRConfig()
        self.is_connected = False
        self.is_streaming = False
        self.device_info: Dict[str, Any] = {}

    @abstractmethod
    def connect(self) -> None:
        """Connect to the SDR device."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the SDR device."""
        pass

    @abstractmethod
    def set_frequency(self, frequency: int) -> None:
        """Set center frequency in Hz."""
        pass

    @abstractmethod
    def set_sample_rate(self, sample_rate: int) -> None:
        """Set sample rate in Hz."""
        pass

    @abstractmethod
    def set_gain(self, gain: Optional[int]) -> None:
        """Set gain. None for auto gain."""
        pass

    @abstractmethod
    def start_streaming(self) -> None:
        """Start IQ data streaming."""
        pass

    @abstractmethod
    def stop_streaming(self) -> None:
        """Stop IQ data streaming."""
        pass

    @abstractmethod
    def read_samples(self, num_samples: int) -> np.ndarray:
        """Read IQ samples."""
        pass

    @abstractmethod
    def read_samples_timeout(self, duration: float) -> np.ndarray:
        """Read IQ samples for specified duration."""
        pass

    def get_device_info(self) -> Dict[str, Any]:
        """Get device information."""
        return self.device_info.copy()

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.is_streaming:
            self.stop_streaming()
        if self.is_connected:
            self.disconnect()
