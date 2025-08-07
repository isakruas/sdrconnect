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

# Custom exceptions for SDRConnect.


class SDRConnectError(Exception):
    """Base exception for all SDRConnect errors."""

    pass


class ConnectionError(SDRConnectError):
    """Raised when connection to SDR device fails."""

    pass


class ConfigurationError(SDRConnectError):
    """Raised when SDR configuration is invalid."""

    pass


class TimeoutError(SDRConnectError):
    """Raised when operation times out."""

    pass


class SDRTimeoutError(SDRConnectError):
    """Raised when SDR operation times out."""

    pass


class ProtocolError(SDRConnectError):
    """Raised when protocol communication fails."""

    pass
