import pyshark
import wave

def read_pcapng(file_path):
    cap = pyshark.FileCapture(file_path)
    packets = []
    
    for packet in cap:
        try:
            time = float(packet.sniff_time.timestamp())
            payload = bytes.fromhex(packet.data.data.replace(':', ''))
            packets.append((time, payload))
        except AttributeError:
            continue
    
    return packets

def reconstruct_audio(packets, output_file):
    # Assuming the audio is in PCM format with 16-bit samples
    sample_rate = 44100  # Adjust this based on your audio file
    num_channels = 1
    sample_width = 2
    
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        
        for _, payload in packets:
            wf.writeframes(payload)

# Define the file paths
output_audio_file = 'reconstructed_audio.wav'
PATH = '/home/rsb6/Desktop/LIVE/ATV4/ethernet-analyser/'

input_file_path = PATH + 'src/Dataset/Benignos/sine/freq100-1000.pcapng'

# Read the pcapng file and extract packets
packets = read_pcapng(input_file_path)

# Reconstruct and save the audio file
reconstruct_audio(packets, output_audio_file)
