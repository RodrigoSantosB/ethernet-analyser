import pandas as pd
import warnings
from scapy.all import Ether, sendp
import time
import sys
warnings.filterwarnings("ignore")


path = '/home/rsb6/Desktop/LIVE/ATV4/ethernet-analyser/src/Dataset_labeled/labeled_drop.csv'

def send_csv(file_path, interface='veth0', interval=0.1, dst_mac='ff:ff:ff:ff:ff:ff'):
    # Leia o CSV
    df = pd.read_csv(file_path)
    
    while True:
        for _, row in df.iterrows():
            # Crie um payload a partir das colunas 'Chanel0' e 'Chanel1'
            payload = f"{row['Chanel0']},{row['Chanel1']},{row['Time_Diff']} ".encode('utf-8')
            # Crie um pacote Ethernet com o payload
            packet = Ether() / payload
            # Envie o pacote pela interface especificada
            sendp(packet, iface=interface, verbose=False)
            # Aguarde o intervalo especificado antes de enviar o próximo pacote
            time.sleep(interval)
            # print(packet)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python sender.py <csv_file> <interface ex: veth0>")
        sys.exit(1)

    csv_file = sys.argv[1]
    interface = sys.argv[2]
    send_csv(csv_file, interface)
