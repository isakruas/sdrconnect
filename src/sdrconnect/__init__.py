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

# SDRConnect: A Python package for connecting to and managing Software Defined Radio (SDR) devices.

__version__ = "0.1.1"
__author__ = "Isak Ruas"
__email__ = "isakruas@gmail.com"

from .clients.rtlsdr import RTLSDRClient
from .clients.spyserver import SpyServerClient
from .core.analysis import analyze_signal
from .core.config import SDRConfig
from .core.exceptions import ConfigurationError, ConnectionError, SDRConnectError

__all__ = [
    "SpyServerClient",
    "RTLSDRClient",
    "SDRConfig",
    "SDRConnectError",
    "ConnectionError",
    "ConfigurationError",
    "analyze_signal",
]
