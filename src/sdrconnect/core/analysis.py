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
from scipy.signal import find_peaks


def analyze_signal(
    data: np.ndarray, sample_rate: float, fft_size: int = 1024
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Perform signal analysis on complex IQ data and plot results.

    Parameters:
        data (np.ndarray): Complex IQ baseband signal.
        sample_rate (float): Sampling rate in Hz.
        fft_size (int): FFT size for spectrum analysis.

    Returns:
        metrics_dict (dict): All metrics in JSON-friendly format.
        spectrogram (np.ndarray): Time-frequency spectrogram in dB.
        mean_psd (np.ndarray): Average PSD in dB.
        freq_axis (np.ndarray): Frequency axis in MHz.
        time_axis (np.ndarray): Time axis in seconds.
    """

    # ===== Frequency Analysis =====
    num_rows = len(data) // fft_size
    spectrogram = np.zeros((num_rows, fft_size))

    for i in range(num_rows):
        segment = data[i * fft_size : (i + 1) * fft_size]
        fft_vals = np.fft.fftshift(np.fft.fft(segment))
        mag = np.abs(fft_vals) ** 2
        spectrogram[i, :] = 10 * np.log10(mag + 1e-12)

    time_axis = np.arange(num_rows) * (fft_size / sample_rate)
    freq_axis = np.linspace(-sample_rate / 2, sample_rate / 2, fft_size) / 1e6
    mean_psd = np.mean(spectrogram, axis=0)

    # ===== Time-Domain =====
    amplitude = np.abs(data)
    phase = np.angle(data)
    rms = np.sqrt(np.mean(amplitude**2))
    peak = np.max(amplitude)
    crest_factor = peak / rms
    dc_offset_i = np.mean(np.real(data))
    dc_offset_q = np.mean(np.imag(data))
    zero_crossings = ((np.real(data[:-1]) * np.real(data[1:])) < 0).sum()

    # ===== Noise & Quality =====
    snr_est = 10 * np.log10(
        np.mean(amplitude**2) / np.var(amplitude - np.mean(amplitude))
    )
    noise_floor = np.median(mean_psd)
    sinad = 10 * np.log10(
        np.mean(amplitude**2) / (np.mean((amplitude - np.mean(amplitude)) ** 2) + 1e-12)
    )

    # ===== Instantaneous =====
    inst_phase = np.unwrap(phase)
    inst_freq = np.diff(inst_phase) * (sample_rate / (2 * np.pi))

    # ===== Occupied Bandwidth =====
    psd_linear = 10 ** (mean_psd / 10)
    cum_energy = np.cumsum(psd_linear) / np.sum(psd_linear)
    lower_idx = np.searchsorted(cum_energy, 0.005)
    upper_idx = np.searchsorted(cum_energy, 0.995)
    occ_bw_khz = (upper_idx - lower_idx) * (sample_rate / fft_size) / 1e3

    # ===== Peak Frequency =====
    peak_idx = np.argmax(mean_psd)
    peak_freq_mhz = freq_axis[peak_idx]

    # ===== Frequency Drift =====
    freq_drift_hz = np.max(inst_freq) - np.min(inst_freq)

    # ===== Harmonic & Spur Detection =====
    peaks, _ = find_peaks(mean_psd, height=noise_floor + 6)
    spur_frequencies = freq_axis[peaks].tolist()

    # ===== Modulation Hint =====
    modulation_hint = "Unknown"
    if np.std(inst_freq) > 1000:
        modulation_hint = "Likely FM"
    elif np.std(inst_phase) > 0.1:
        modulation_hint = "Likely PSK/QAM"
    elif np.std(amplitude) > 0.05:
        modulation_hint = "Likely AM"

    # ===== Symbol Rate Estimation =====
    spectrum_mag = np.abs(np.fft.fftshift(np.fft.fft(amplitude - np.mean(amplitude))))
    half_spectrum = spectrum_mag[len(spectrum_mag) // 2 :]
    symbol_rate_est = (np.argmax(half_spectrum) / len(half_spectrum)) * (
        sample_rate / 2
    )

    # ===== Carrier-to-Noise Ratio =====
    carrier_power = np.max(psd_linear)
    noise_power = np.mean(psd_linear[(psd_linear < carrier_power * 0.01)])
    cnr = 10 * np.log10(carrier_power / (noise_power + 1e-12))

    # ===== JSON-Ready Metrics =====
    metrics_dict = {
        "sample_rate_hz": float(sample_rate),
        "time_domain": {
            "rms_level": float(rms),
            "peak_level": float(peak),
            "crest_factor": float(crest_factor),
            "dc_offset_i": float(dc_offset_i),
            "dc_offset_q": float(dc_offset_q),
            "zero_crossing_count": int(zero_crossings),
        },
        "frequency_domain": {
            "occupied_bandwidth_khz": float(occ_bw_khz),
            "peak_frequency_mhz": float(peak_freq_mhz),
            "frequency_drift_hz": float(freq_drift_hz),
            "spur_frequencies_mhz": spur_frequencies,
        },
        "noise_quality": {
            "snr_db": float(snr_est),
            "noise_floor_db": float(noise_floor),
            "sinad_db": float(sinad),
            "carrier_to_noise_db": float(cnr),
        },
        "modulation": {
            "modulation_hint": modulation_hint,
            "symbol_rate_hz": float(symbol_rate_est),
        },
    }

    # ========== Print Summary ==========
    print("\n===== 📊 Summary =====\n")
    print(f"Sample rate: {sample_rate/1e6:.3f} MHz")
    print(f"RMS level: {rms:.4f}")
    print(f"Peak level: {peak:.4f}")
    print(f"Crest factor: {crest_factor:.2f}")
    print(f"DC offset (I): {dc_offset_i:.6f}")
    print(f"DC offset (Q): {dc_offset_q:.6f}")
    print(f"Zero-crossing rate: {zero_crossings} crossings")
    print(f"Estimated SNR: {snr_est:.2f} dB")
    print(f"Noise floor: {noise_floor:.2f} dB")
    print(f"SINAD: {sinad:.2f} dB")
    print(f"Occupied bandwidth (99%): {occ_bw_khz:.2f} kHz")
    print(f"Peak frequency: {peak_freq_mhz:.6f} MHz")
    print(f"Frequency drift: {freq_drift_hz:.2f} Hz")
    print(f"Detected spurs: {spur_frequencies} MHz")
    print(f"Carrier-to-Noise Ratio: {cnr:.2f} dB")
    print(f"Modulation type hint: {modulation_hint}")
    print(f"Estimated symbol rate: {symbol_rate_est:.2f} Hz")

    # ===== Plots =====
    fig, axs = plt.subplots(5, 2, figsize=(14, 14))

    axs[0, 0].plot(freq_axis, mean_psd)
    axs[0, 0].set_xlabel("Frequency [MHz]")
    axs[0, 0].set_ylabel("PSD [dB]")
    axs[0, 0].set_title("Average Power Spectral Density")

    axs[0, 1].imshow(
        spectrogram,
        aspect="auto",
        extent=[freq_axis[0], freq_axis[-1], time_axis[-1], time_axis[0]],
        cmap="viridis",
    )
    axs[0, 1].set_title("Spectrogram")
    axs[0, 1].set_xlabel("Frequency [MHz]")
    axs[0, 1].set_ylabel("Time [s]")

    axs[1, 0].scatter(
        np.real(data[:: max(1, len(data) // 5000)]),
        np.imag(data[:: max(1, len(data) // 5000)]),
        s=2,
        alpha=0.5,
    )
    axs[1, 0].set_xlabel("I")
    axs[1, 0].set_ylabel("Q")
    axs[1, 0].set_title("IQ Constellation")
    axs[1, 0].grid(True)

    axs[1, 1].hist(amplitude, bins=100, color="orange", alpha=0.7)
    axs[1, 1].set_xlabel("Amplitude")
    axs[1, 1].set_ylabel("Count")
    axs[1, 1].set_title("Amplitude Histogram")

    axs[2, 0].plot(inst_phase[:5000])
    axs[2, 0].set_xlabel("Sample index")
    axs[2, 0].set_ylabel("Phase [rad]")
    axs[2, 0].set_title("Instantaneous Phase [rad]")

    axs[2, 1].plot(inst_freq[:5000])
    axs[2, 1].set_xlabel("Sample index")
    axs[2, 1].set_ylabel("Frequency [Hz]")
    axs[2, 1].set_title("Instantaneous Frequency [Hz]")

    axs[3, 0].plot(amplitude[:5000])
    axs[3, 0].set_xlabel("Sample index")
    axs[3, 0].set_ylabel("Amplitude")
    axs[3, 0].set_title("Amplitude Envelope")

    axs[3, 1].hist(phase, bins=100, color="green", alpha=0.7)
    axs[3, 1].set_xlabel("Phase [rad]")
    axs[3, 1].set_ylabel("Count")
    axs[3, 1].set_title("Phase Distribution")

    axs[4, 0].stem(freq_axis, mean_psd, basefmt=" ")
    axs[4, 0].set_xlabel("Frequency [MHz]")
    axs[4, 0].set_ylabel("PSD [dB]")
    axs[4, 0].set_title("Harmonics & Spurs")

    axs[4, 1].plot(half_spectrum)
    axs[4, 1].set_xlabel("Frequency bin index")
    axs[4, 1].set_ylabel("Magnitude")
    axs[4, 1].set_title("Symbol Rate Spectrum")

    plt.tight_layout()
    plt.show()

    return spectrogram, mean_psd, freq_axis, time_axis, metrics_dict
