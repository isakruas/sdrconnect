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

# SDR configuration class.

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class SDRConfig:
    """Configuration class for SDR connections."""

    # Connection settings
    host: str = "localhost"
    port: int = 5555
    timeout: float = 10.0

    # RF settings
    frequency: int = 100_000_000  # 100 MHz
    sample_rate: int = 2_048_000  # 2.048 MHz
    gain: Optional[int] = None  # Auto gain if None

    # Data format
    iq_format: str = "complex64"  # complex64, complex128, uint8
    decimation: int = 1

    # Advanced settings
    bandwidth: Optional[int] = None
    bias_tee: bool = False
    dc_offset_correction: bool = True
    iq_balance_correction: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "timeout": self.timeout,
            "frequency": self.frequency,
            "sample_rate": self.sample_rate,
            "gain": self.gain,
            "iq_format": self.iq_format,
            "decimation": self.decimation,
            "bandwidth": self.bandwidth,
            "bias_tee": self.bias_tee,
            "dc_offset_correction": self.dc_offset_correction,
            "iq_balance_correction": self.iq_balance_correction,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SDRConfig":
        """Create config from dictionary."""
        return cls(**data)

    def save(self, filepath: str) -> None:
        """Save config to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "SDRConfig":
        """Load config from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.frequency <= 0:
            raise ValueError("Frequency must be positive")
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        if self.iq_format not in ["complex64", "complex128", "uint8"]:
            raise ValueError("Invalid IQ format")
