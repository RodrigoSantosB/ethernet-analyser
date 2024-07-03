from _eth_libs import *

class EthernetProcess:
    def __init__(self) -> None:
        pass
    
    
    
    def _read_pcapng(self, file_path_audio):
        packets = rdpcap(file_path_audio)
        
        data_packets = []
        chanel0 = []
        chanel1 = []
        
        for packet in packets:
            if Raw in packet:
                # time = packet.time
                payload = packet[Raw].load.hex()[48:96]  # Extrair payload como hexadecimal
                # Adiciona os elementos na lista
                data_packets.append(payload)
                
                # Separar os bytes entre chanel0 e chanel1
                for i in range(0, len(payload), 4):
                    byte = payload[i:i+4]
                    if (i // 4) % 2 == 0:
                        chanel0.append(byte)
                    else:
                        chanel1.append(byte)
                        
        return data_packets, chanel0, chanel1
    
    
    def _process_data_pcapng(self, packets):
        # Função para converter pares hexadecimais em decimais
        hex_to_decimal = lambda hex_str: [int(hex_str[i:i+2], 16) 
                                            for i in range(0, len(hex_str), 2)]

        # Processamento dos dados utilizando list comprehension
        data_numeric = [hex_to_decimal(hex_str) for hex_str in packets]

        # Convertendo para um array do NumPy
        payloads = np.array(data_numeric)
        
        return payloads
    
    
    def _create_dataframe(self, csv_path, payload):
        time_df = pd.read_csv(csv_path)
        time_df = time_df['Time'] 
        if len(time_df) != payload.shape[0]:
            raise ValueError("O tamanho do vetor de tempos e o tamanho do vetor de \
                                payload devem ser correspondentes")

        # Converter 'time' para DataFrame se não for
        if isinstance(time_df, pd.Series):
            dataframe = time_df.to_frame(name='Timestamp')
        else:
            dataframe = time_df.copy()
        
        # Adicionar a coluna de vetores
        dataframe['Payload'] = list(payload)
        return dataframe

    def label_anomalies(self, df, output_filename, attck_name='malicius', 
                            expected_interval=0.000125, multiplier=2):
                
        # Calcular a diferença de tempo entre linhas consecutivas
        df['Time_Diff'] = df['Timestamp'].diff().fillna(0)
        
        # Calcular o threshold
        threshold = expected_interval * multiplier
        
        # Detectar anomalias com base no threshold e rotular como 'malicius' ou 'benigno'
        df['Label'] = df['Time_Diff'].apply(lambda x: attck_name 
                            if (x > threshold or x < (expected_interval-0.000001)) 
                            else 'benign')
        
        # Exportar o DataFrame como um arquivo CSV
        df.to_csv(f'{output_filename}.csv', index=False)
        
        return df
    
    def reconstruct_audio(self, packets, output_file=None, sample_rate = 44100,
                            num_channels = 1, sample_width = 2):
        '''
        output_audio_file = 'path_to_your_file/reconstructed_audio.wav'
        '''
        if output_file is None:
            output_file = 'reconstructed_audio.wav'
            
        # Convete audio-data to byte
        byte_data = [bytes.fromhex(data) for data in packets]
        
        # audio is in PCM format with 16-bit samples
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            
            for payload in byte_data:
                wf.writeframes(payload)
        print(f'reconstruct_audio in {output_file}')
        
    
    def plot_waveform(self, time_data, packets):
        # Criar o gráfico
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=time_data,
            y=packets,
            mode='lines',
            name='Amplitude'
        ))

        fig.update_layout(
            title='Waveform do Áudio',
            xaxis_title='Tempo (segundos)',
            yaxis_title='Amplitude'
        )

        fig.show()
