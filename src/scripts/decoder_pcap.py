import os
import pyshark
import numpy as np
import matplotlib.pyplot as plt

# Defina o caminho para o executável do TShark
os.environ['TSHARK_PATH'] = '/usr/bin/tshark'  

# Função para extrair o tempo dos pacotes do arquivo .pcap
def extract_signal_from_pcap(pcap_file):
    cap = pyshark.FileCapture(pcap_file)
    timestamps = []
    for packet in cap:
        timestamps.append(float(packet.sniff_timestamp))
    cap.close()
    return np.array(timestamps)

# Função para calcular a potência do sinal em janelas de tempo
def calculate_signal_power(signal, window_size):
    power = []
    for i in range(0, len(signal) - window_size + 1, window_size):
        window = signal[i:i + window_size]
        power.append(np.mean(window ** 2))
    return np.array(power)

# Função para detectar anomalias na potência do sinal
def detect_anomalies(power, threshold):
    anomalies = np.where(power > threshold)[0]
    return anomalies
