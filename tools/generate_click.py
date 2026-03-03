import wave
import struct
import math

duration = 0.05 # seconds
sample_rate = 44100
frequency = 800 # Hz

wave_file = wave.open("son/click.wav", "w")
wave_file.setnchannels(1)
wave_file.setsampwidth(2)
wave_file.setframerate(sample_rate)

for i in range(int(duration * sample_rate)):
    # Simple sine wave with exponential decay
    value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate) * math.exp(-i / (sample_rate * 0.02)))
    data = struct.pack("<h", value)
    wave_file.writeframesraw(data)

wave_file.close()
print("click.wav generated successfully.")
