# SDRConnect

Modern Python library for SDR connectivity and data collection. Focused exclusively on connecting to SDR devices and collecting raw IQ data.

[![Latest Version](https://img.shields.io/pypi/v/sdrconnect.svg?style=flat)](https://pypi.python.org/pypi/sdrconnect/)

## Features

- **SpyServer Support**: Connect to SpyServer instances for remote SDR access
- **Modern Python**: Built with Python 3.8+ and modern packaging standards
- **Simple API**: Clean, intuitive interface for SDR data collection
- **Type Hints**: Full type annotation support
- **Extensible**: Easy to add new SDR backends

## Installation

```bash
pip install sdrconnect
```

## Quick Start

### SpyServer Example

```python
import sdrconnect as sdr
import numpy as np

# Create configuration for SpyServer
config = sdr.SDRConfig(
    host="localhost",  # Change to your SpyServer host
    port=5555,         # Change to your SpyServer port
    frequency=100_000_000,  # 100 MHz
    timeout=5.0
)

try:
    # Create and connect to SpyServer
    print("Connecting to SpyServer...")
    client = sdr.SpyServerClient(config)
    
    with client:
        # Set up the SDR
        client.set_frequency(config.frequency)
        client.set_sample_rate(config.sample_rate)
        client.set_gain(None)  # Auto gain
        
        # Start streaming
        print("Starting streaming...")
        client.start_streaming()
        
        # Collect data for duration_seconds seconds
        duration_seconds = 5.0
        print(f"Collecting IQ data for {duration_seconds} seconds...")
        iq_data = client.read_samples_timeout(duration_seconds)

        # Save data for later processing
        np.save("iq_data.npy", iq_data)
        
        print(f"Collected {len(iq_data)} IQ samples")
        print(f"Sample rate: {config.sample_rate} Hz")
        print(f"Center frequency: {config.frequency / 1e6:.1f} MHz")
        
        # Analyze the data
        spectrogram, mean_psd, freq_axis, time_axis, _ = sdr.analyze_signal(
            data=iq_data,
            sample_rate=config.sample_rate,
            fft_size=1024
        )
        
        print("Analysis complete!") 
        
except sdr.SDRConnectError as e:
    print(f"Connection error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

SDRConnect uses configuration objects for easy management:

```python
# Create config
config = sdr.SDRConfig(
    host="localhost",
    port=5555,
    frequency=433_920_000,  # 433.92 MHz
    gain=20,                # Manual gain
    iq_format="complex64",  # or "uint8"
    timeout=30.0
)

# Save config
config.save("my_sdr_config.json")

# Load config
config = sdr.SDRConfig.load("my_sdr_config.json")
```

## Supported SDR Devices

- **SpyServer**: Remote SDR access via SpyServer protocol
- **RTL-SDR**: Coming soon

## Data Collection Best Practices

1. **Use Frequency Offset**: Avoid DC spikes by offsetting from your target frequency
2. **Choose Appropriate Sample Rate**: Balance between bandwidth and data size
3. **Monitor Connection**: Use context managers or proper exception handling
4. **Data Format**: Use uint8 for bandwidth efficiency, complex64 for precision

## API Reference

### SpyServerClient

- `connect()`: Connect to SpyServer
- `disconnect()`: Disconnect from SpyServer  
- `set_frequency(freq)`: Set center frequency in Hz
- `set_sample_rate(rate)`: Set sample rate in Hz
- `set_gain(gain)`: Set gain (None for auto)
- `start_streaming()`: Start IQ streaming
- `stop_streaming()`: Stop IQ streaming
- `read_samples(n)`: Read n samples
- `read_samples_timeout(duration)`: Read for duration seconds

### SDRConfig

Configuration class with validation and JSON serialization support.

## Author

**Isak Ruas** - isakruas@gmail.com

## License

Apache License 2.0 - see LICENSE file for details.
