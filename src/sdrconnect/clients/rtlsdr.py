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

# RTL-SDR client (placeholder implementation).

from typing import Optional

import numpy as np

from ..core.config import SDRConfig
from .base import BaseSDRClient


class RTLSDRClient(BaseSDRClient):
    """RTL-SDR client (placeholder implementation)."""

    def __init__(self, device_index: int = 0, config: Optional[SDRConfig] = None):
        """Initialize RTL-SDR client."""
        super().__init__(config)
        self.device_index = device_index

    def connect(self) -> None:
        """Connect to RTL-SDR device."""
        raise NotImplementedError("RTL-SDR implementation coming soon")

    def disconnect(self) -> None:
        """Disconnect from RTL-SDR device."""
        raise NotImplementedError("RTL-SDR implementation coming soon")

    def set_frequency(self, frequency: int) -> None:
        """Set center frequency."""
        raise NotImplementedError("RTL-SDR implementation coming soon")

    def set_sample_rate(self, sample_rate: int) -> None:
        """Set sample rate."""
        raise NotImplementedError("RTL-SDR implementation coming soon")

    def set_gain(self, gain: Optional[int]) -> None:
        """Set gain."""
        raise NotImplementedError("RTL-SDR implementation coming soon")

    def start_streaming(self) -> None:
        """Start streaming."""
        raise NotImplementedError("RTL-SDR implementation coming soon")

    def stop_streaming(self) -> None:
        """Stop streaming."""
        raise NotImplementedError("RTL-SDR implementation coming soon")

    def read_samples(self, num_samples: int) -> np.ndarray:
        """Read samples."""
        raise NotImplementedError("RTL-SDR implementation coming soon")

    def read_samples_timeout(self, duration: float) -> np.ndarray:
        """Read samples with timeout."""
        raise NotImplementedError("RTL-SDR implementation coming soon")
