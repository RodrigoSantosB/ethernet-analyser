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

# Exemplo de uso

pcap_file = '/home/rsb6/Desktop/LIVE/ATV4/ethernet-analyser/src/scripts/dataset/TSNBox_192.168.41.151_4455.pcapng'
signal = extract_signal_from_pcap(pcap_file)

# Parâmetros para o cálculo da potência do sinal
window_size = 10  # Tamanho da janela para o cálculo da potência
power = calculate_signal_power(signal, window_size)

# Definindo um limiar para detectar anomalias
threshold = np.mean(power) + 2 * np.std(power)
anomalies = detect_anomalies(power, threshold)

# Visualizando a potência do sinal e as anomalias
plt.figure(figsize=(12, 6))
plt.plot(power, label='Potência do Sinal')
plt.axhline(y=threshold, color='r', linestyle='--', label='Limiar de Anomalia')
plt.scatter(anomalies, power[anomalies], color='red', label='Anomalias')
plt.title('Análise da Potência do Sinal')
plt.xlabel('Janela de Tempo')
plt.ylabel('Potência')
plt.legend()
plt.show()

# Imprimindo as janelas de tempo com anomalias
print(f"Anomalias detectadas nas seguintes janelas de tempo: {anomalies}")
