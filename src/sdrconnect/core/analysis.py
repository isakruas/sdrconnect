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

# Signal analysis utilities.

from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np


def plot(
    data: np.ndarray, sample_rate: float, fft_size: int = 1024
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute and (optionally) plot the spectrogram and average PSD of an IQ signal.

    Parameters:
        data (np.ndarray): IQ signal (complex).
        sample_rate (float): Sampling rate in Hz.
        fft_size (int): Number of samples per FFT (default: 1024).
        plot (bool): If True, plot the graphs (default: True).

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
            spectrogram [num_frames x fft_size],
            mean_psd [fft_size],
            freq_axis [MHz],
            time_axis [s]
    """
    num_rows = len(data) // fft_size
    spectrogram = np.zeros((num_rows, fft_size))

    for i in range(num_rows):
        segment = data[i * fft_size : (i + 1) * fft_size]
        fft_vals = np.fft.fftshift(np.fft.fft(segment))
        magnitude_linear = np.abs(fft_vals) ** 2
        spectrogram[i, :] = 10 * np.log10(magnitude_linear + 1e-12)

    # Axes
    time_axis = np.arange(num_rows) * (fft_size / sample_rate)
    freq_axis = np.linspace(-sample_rate / 2, sample_rate / 2, fft_size) / 1e6  # MHz

    # Average PSD
    mean_psd = np.mean(spectrogram, axis=0)

    fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    axs[0].plot(freq_axis, mean_psd)
    axs[0].set_ylabel("Average PSD [dB]")
    axs[0].set_title("Average Power Spectral Density")

    axs[1].imshow(
        spectrogram,
        aspect="auto",
        extent=[freq_axis[0], freq_axis[-1], time_axis[-1], time_axis[0]],
        cmap="viridis",
    )
    axs[1].set_ylabel("Time [s]")
    axs[1].set_xlabel("Frequency [MHz]")
    axs[1].set_title("Spectrogram")

    plt.tight_layout()
    plt.show()
    fig.clear()
    plt.close(fig)

    return spectrogram, mean_psd, freq_axis, time_axis
