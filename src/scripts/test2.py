from scapy.all import rdpcap
from pydub import AudioSegment
import numpy as np
import os

# Defina o caminho para o executável do TShark
os.environ['TSHARK_PATH'] = '/usr/bin/tshark'

from scapy.all import rdpcap
from pydub import AudioSegment
import numpy as np
import os

# Defina o caminho para o executável do TShark
os.environ['TSHARK_PATH'] = '/usr/bin/tshark'

def extract_audio_from_avtp_pcapng(file_path, reconstruct_audio=False):
    # Ler o arquivo pcapng
    packets = rdpcap(file_path)
    
    audio_data = []
    time_data = []
    
    # Iterar sobre os pacotes e extrair dados AVTP
    for packet in packets:
        if packet.haslayer("Ethernet") and packet["Ethernet"].type == 0x22F0:  # EtherType para AVTP
            eth_layer = packet["Ethernet"]
            
            # Inspecionar os dados brutos do pacote AVTP
            avtp_data = bytes(eth_layer.payload)
            tm_data   = eth_layer.time
            
            
            # Adicionar dados de áudio extraídos ao array audio_data
            audio_data.append(avtp_data)
            time_data.append(tm_data)
    
    # Concatenar todos os dados de áudio
    raw_audio_data = b''.join(audio_data)
    time_array = np.array([float(val) for val in time_data], dtype=np.float64)


    
    
    # Verificar se os dados de áudio não estão vazios
    if not raw_audio_data and raw_time_data:
        raise ValueError("Nenhum dado de áudio encontrado nos pacotes.")
    
    # Converte os bytes para um array numpy no formato little-endian
    audio_array = np.frombuffer(raw_audio_data, dtype='<i2')
    
    # Normalizar os dados de áudio
    audio_array = audio_array / np.max(np.abs(audio_array))
    
    
    # Converte o array normalizado de volta para bytes
    normalized_audio_data = (audio_array * 32767).astype(np.int16).tobytes()
    
    # Criar um segmento de áudio a partir dos dados normalizados
    if reconstruct_audio:
        audio_segment = AudioSegment(
            data=normalized_audio_data,
            sample_width=2,  # 2 bytes para PCM 16 bits
            frame_rate=48000,  # Frequência de amostragem
            channels=2  # Estéreo
        )
            
        # Salvar o áudio em um arquivo WAV
        output_file = "reconstructed_audio.wav"
        audio_segment.export(output_file, format="wav")
        print(f"Áudio reconstruído e salvo como '{output_file}'")
    else:
        ...
        
    return time_array, audio_array
