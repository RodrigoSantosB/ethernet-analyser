from scapy.all import sniff
import sys


def hex_to_decimal(hex_str):
    try:
        return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]
    except ValueError:
        # Retorna uma lista vazia se a string não for válida
        return []

def packet_callback(packet):
    data = []
    if packet.haslayer('Raw'):
        time = packet.time
        payload = packet['Raw'].load
        payload_str = payload.decode('utf-8')

        # try:
        #     # Divide a string do payload nas colunas 'Chanel0', 'Chanel1', e 'Time_Diff'
        #     chanel0, chanel1, time_diff = payload_str.split(',')
        #     chanel0_numeric = hex_to_decimal(chanel0)
        #     chanel1_numeric = hex_to_decimal(chanel1)
        #     time_float = float(time_diff)
        #     data.append(chanel0_numeric + chanel1_numeric + [time_float])
        # except ValueError:
        #     print(f"Payload mal formatado: {payload_str}")

        print(payload)

def listen(interface='veth1'):
    sniff(iface=interface, prn=packet_callback, store=0)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python receiver.py <interface>")
        sys.exit(1)

    interface = sys.argv[1]
    listen(interface)
