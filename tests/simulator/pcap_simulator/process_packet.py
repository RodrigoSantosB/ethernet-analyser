from scapy.all import sniff, Raw
import pandas as pd
class PCAPProcessor:
    def _read_pcapng(self, interface):
        data_packets = []
        chanel0 = []
        chanel1 = []
        dataframe = pd.DataFrame()

        def packet_callback(packet):
            if Raw in packet:
                payload = packet[Raw].load.hex()[48:96]  # Extrair payload como hexadecimal
                data_packets.append(payload)
                time_df = packet.time

                # Separar os bytes entre chanel0 e chanel1
                temp_chanel0 = []
                temp_chanel1 = []

                for i in range(0, len(payload), 4):
                    byte = payload[i:i+4]
                    if (i // 4) % 2 == 0:
                        temp_chanel0.append(byte)
                    else:
                        temp_chanel1.append(byte)

                # Agrupar bytes em conjuntos de 6 e concatenar
                for i in range(0, len(temp_chanel0), 6):
                    group = temp_chanel0[i:i+6]
                    chanel0.append(''.join(group))
                for i in range(0, len(temp_chanel1), 6):
                    group = temp_chanel1[i:i+6]
                    chanel1.append(''.join(group))
                    
                # Converter 'time' para DataFrame se não for

        # Escutar na interface especificada
        sniff(iface=interface, prn=packet_callback, store=0, timeout=2)  # Define um timeout de 10 segundos
        print(chanel0)
        print(chanel1)


if __name__ == '__main__':
    processor = PCAPProcessor()
    interface = 'veth1'
    while True:
        processor._read_pcapng(interface)

