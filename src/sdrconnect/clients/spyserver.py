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

# SpyServer SDR client implementation.

import logging
import socket
import struct
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..core.config import SDRConfig
from ..core.exceptions import SDRConnectError, SDRTimeoutError
from .base import BaseSDRClient

logger = logging.getLogger(__name__)

# SpyServer Protocol Constants
SPYSERVER_PROTOCOL_VERSION = (2 << 24) | (0 << 16) | 1700

# Command types
SPYSERVER_CMD_HELLO = 0
SPYSERVER_CMD_SET_SETTING = 2

# Setting types
SPYSERVER_SETTING_IQ_FORMAT = 100
SPYSERVER_SETTING_IQ_FREQUENCY = 101
SPYSERVER_SETTING_IQ_DECIMATION = 102
SPYSERVER_SETTING_STREAMING_MODE = 0
SPYSERVER_SETTING_STREAMING_ENABLED = 1
SPYSERVER_SETTING_GAIN = 2

# Stream modes
SPYSERVER_STREAM_MODE_IQ_ONLY = 1

# Message types
SPYSERVER_MSG_TYPE_DEVICE_INFO = 0
SPYSERVER_MSG_TYPE_UINT8_IQ = 100

# Little-endian format
_LE32 = "<I"


class SpyServerClient(BaseSDRClient):
    """SpyServer SDR client implementation."""

    def __init__(self, config: Optional[SDRConfig] = None):
        """Initialize SpyServer client."""
        super().__init__(config)
        self.socket: Optional[socket.socket] = None
        self.app_name = (
            self.config.app_name.encode("ascii")
            if hasattr(self.config, "app_name")
            else b"SDRConnect"
        )

    def connect(self) -> None:
        """Connect to SpyServer."""
        if self.is_connected:
            return

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.config.timeout)
            self.socket.connect((self.config.host, self.config.port))

            # Send hello message
            self._send_hello()

            # Wait for device info
            self.device_info = self._wait_for_device_info()

            self.is_connected = True
            logger.info(
                f"Connected to SpyServer at {self.config.host}:{self.config.port}"
            )

        except Exception as e:
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            raise SDRConnectError(f"Failed to connect to SpyServer: {e}")

    def disconnect(self) -> None:
        """Disconnect from SpyServer."""
        try:
            if self.is_streaming:
                self.stop_streaming()
        except:
            pass

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None

        self.is_connected = False
        self.device_info = {}
        logger.info("Disconnected from SpyServer")

    def set_frequency(self, frequency: int) -> None:
        """Set center frequency."""
        if not self.is_connected:
            raise SDRConnectError("Not connected to SpyServer")
        self._set_setting(SPYSERVER_SETTING_IQ_FREQUENCY, frequency)
        logger.debug(f"Set frequency to {frequency} Hz")

    def set_sample_rate(self, sample_rate: int) -> None:
        """Set sample rate via decimation."""
        if not self.is_connected:
            raise SDRConnectError("Not connected to SpyServer")

        # Calculate decimation based on maximum sample rate
        max_rate = self.device_info.get("MaximumSampleRate", 2048000)
        decimation = max(1, max_rate // sample_rate)
        self._set_setting(SPYSERVER_SETTING_IQ_DECIMATION, decimation)
        logger.debug(f"Set decimation to {decimation} for sample rate {sample_rate} Hz")

    def set_gain(self, gain: Optional[int]) -> None:
        """Set gain."""
        if not self.is_connected:
            raise SDRConnectError("Not connected to SpyServer")

        if gain is None:
            gain = 0  # Auto gain

        max_gain = self.device_info.get("MaximumGainIndex", 29)
        gain = min(max(0, gain), max_gain)

        self._set_setting(SPYSERVER_SETTING_GAIN, gain)
        logger.debug(f"Set gain to {gain}")

    def start_streaming(self) -> None:
        """Start IQ streaming."""
        if not self.is_connected:
            raise SDRConnectError("Not connected to SpyServer")

        self._set_setting(SPYSERVER_SETTING_STREAMING_ENABLED, 1)
        self.is_streaming = True
        logger.debug("Started IQ streaming")

    def stop_streaming(self) -> None:
        """Stop IQ streaming."""
        if not self.is_connected:
            raise SDRConnectError("Not connected to SpyServer")

        try:
            self._set_setting(SPYSERVER_SETTING_STREAMING_ENABLED, 0)
        finally:
            self.is_streaming = False
        logger.debug("Stopped IQ streaming")

    def read_samples(self, num_samples: int) -> np.ndarray:
        """Read specific number of samples."""
        if not self.is_connected:
            raise SDRConnectError("Not connected to SpyServer")
        if not self.is_streaming:
            raise SDRConnectError("Streaming not enabled")

        iq_list = []
        samples_collected = 0

        while samples_collected < num_samples:
            try:
                iq_data = self._read_iq_packet()
                if len(iq_data) > 0:
                    remaining = num_samples - samples_collected
                    if len(iq_data) > remaining:
                        iq_data = iq_data[:remaining]

                    iq_list.append(iq_data)
                    samples_collected += len(iq_data)
            except socket.timeout:
                break

        if iq_list:
            return np.concatenate(iq_list).astype(np.complex64)
        else:
            return np.array([], dtype=np.complex64)

    def read_samples_timeout(self, duration: float) -> np.ndarray:
        """Read samples for specified duration."""
        if not self.is_connected:
            raise SDRConnectError("Not connected to SpyServer")
        if not self.is_streaming:
            raise SDRConnectError("Streaming not enabled")

        start_time = time.time()
        iq_list = []

        while time.time() - start_time < duration:
            try:
                iq_data = self._read_iq_packet()
                if len(iq_data) > 0:
                    iq_list.append(iq_data)
            except socket.timeout:
                break

        if iq_list:
            return np.concatenate(iq_list).astype(np.complex64)
        else:
            return np.array([], dtype=np.complex64)

    def read_iq_samples_with_metadata(
        self, duration: float
    ) -> Tuple[np.ndarray, List[float], List[float]]:
        """Read IQ samples with timing metadata (SpyServer specific method)."""
        if not self.is_connected:
            raise SDRConnectError("Not connected to SpyServer")
        if not self.is_streaming:
            raise SDRConnectError("Streaming not enabled")

        start_time = time.time()
        iq_list = []
        timestamps = []
        latencies = []

        while time.time() - start_time < duration:
            t_before = time.time()
            try:
                iq_data = self._read_iq_packet()
                t_after = time.time()

                if len(iq_data) > 0:
                    iq_list.append(iq_data)
                    timestamps.append(t_after)
                    latencies.append(t_after - t_before)
            except socket.timeout:
                break

        if iq_list:
            iq_data = np.concatenate(iq_list).astype(np.complex64)
        else:
            iq_data = np.array([], dtype=np.complex64)

        return iq_data, timestamps, latencies

    def _send_command(self, cmd_type: int, data: bytes = b"") -> None:
        """Send command to SpyServer."""
        if not self.socket:
            raise SDRConnectError("Socket not connected")

        header = struct.pack("<II", cmd_type, len(data))
        self.socket.sendall(header + data)

    def _recv_all(self, num_bytes: int) -> bytes:
        """Receive exact number of bytes."""
        if not self.socket:
            raise SDRConnectError("Socket not connected")

        buffer = bytearray()
        while len(buffer) < num_bytes:
            chunk = self.socket.recv(num_bytes - len(buffer))
            if not chunk:
                raise SDRConnectError("Connection closed prematurely")
            buffer += chunk
        return bytes(buffer)

    def _send_hello(self) -> None:
        """Send handshake message."""
        payload = struct.pack(_LE32, SPYSERVER_PROTOCOL_VERSION) + self.app_name
        self._send_command(SPYSERVER_CMD_HELLO, payload)

    def _set_setting(self, setting: int, value: int) -> None:
        """Set SpyServer setting."""
        payload = struct.pack("<II", setting, int(value))
        self._send_command(SPYSERVER_CMD_SET_SETTING, payload)

    def _wait_for_device_info(self, timeout_ms: int = 3000) -> Dict[str, int]:
        """Wait for device information."""
        deadline = time.time() + timeout_ms / 1000.0

        while time.time() < deadline:
            header = self._recv_all(20)
            pid, raw_msg_type, stream_type, seq, body_size = struct.unpack(
                "<IIIII", header
            )
            body = self._recv_all(body_size) if body_size > 0 else b""
            msg_type = raw_msg_type & 0xFFFF

            if msg_type == SPYSERVER_MSG_TYPE_DEVICE_INFO:
                fields = struct.unpack("<" + "I" * 12, body)
                return {
                    "DeviceType": fields[0],
                    "DeviceSerial": fields[1],
                    "MaximumSampleRate": fields[2],
                    "MaximumBandwidth": fields[3],
                    "DecimationStageCount": fields[4],
                    "GainStageCount": fields[5],
                    "MaximumGainIndex": fields[6],
                    "MinimumFrequency": fields[7],
                    "MaximumFrequency": fields[8],
                    "Resolution": fields[9],
                    "MinimumIQDecimation": fields[10],
                    "ForcedIQFormat": fields[11],
                }

        raise SDRTimeoutError("Device info not received within timeout")

    def _read_iq_packet(self) -> np.ndarray:
        """Read single IQ packet."""
        header = self._recv_all(20)
        pid, raw_msg_type, stream_type, seq, body_size = struct.unpack("<IIIII", header)
        body = self._recv_all(body_size) if body_size > 0 else b""

        msg_type = raw_msg_type & 0xFFFF
        flags = raw_msg_type >> 16

        if msg_type == SPYSERVER_MSG_TYPE_UINT8_IQ:
            if body_size % 2 != 0:
                raise SDRConnectError("Invalid IQ data size")

            # Convert uint8 IQ to complex float
            arr = np.frombuffer(body, dtype=np.uint8).reshape(-1, 2).astype(np.float32)

            # Apply gain scaling
            gain = 10 ** (flags / 20.0)
            scale = 1.0 / (gain * 128.0)

            # Convert to normalized complex
            re = (arr[:, 0] - 128.0) * scale
            im = (arr[:, 1] - 128.0) * scale
            return re + 1j * im

        return np.array([], dtype=np.complex64)
