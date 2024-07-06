from scapy.all import rdpcap, sendp
import time
import sys

path = '/home/rsb6/Desktop/LIVE/ATV4/ethernet-analyser/src/Dataset/Benignos/sine/freq100-1000.pcapng'
# interface = 'wlp0s20f3'
from scapy.all import rdpcap, sendp
import time
import sys

def send_pcap(file_path, interface='veth0', interval=0.1):
    packets = rdpcap(file_path)
    for packet in packets:
        sendp(packet, iface=interface, verbose=False)
        time.sleep(interval)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python sender.py <pcap_file> <interface>")
        sys.exit(1)

    pcap_file = sys.argv[1]
    interface = sys.argv[2]
    send_pcap(pcap_file, interface)
