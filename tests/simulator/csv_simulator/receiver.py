from scapy.all import sniff
import sys

def packet_callback(packet):
    if packet.haslayer('Raw'):
        time = packet.time
        payload = packet['Raw'].load
        print(f"Time: {time}, Payload: {payload}")

def listen(interface='veth1'):
    sniff(iface=interface, prn=packet_callback, store=0)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python receiver.py <interface>")
        sys.exit(1)

    interface = sys.argv[1]
    listen(interface)
