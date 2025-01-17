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
                payload = packet[Raw].load.hex()[48:96]  # Extract to hexadecimal payload 
                # Add the elements of list
                data_packets.append(payload)
                
                # separate the bytes betwen chanel0 and chanel1
                temp_chanel0 = []
                temp_chanel1 = []
                
                for i in range(0, len(payload), 4):
                    byte = payload[i:i+4]
                    if (i // 4) % 2 == 0:
                        temp_chanel0.append(byte)
                    else:
                        temp_chanel1.append(byte)
                
                # Group the bytes in set of 6 and concat
                for i in range(0, len(temp_chanel0), 6):
                    group = temp_chanel0[i:i+6]
                    chanel0.append(''.join(group))
                for i in range(0, len(temp_chanel1), 6):
                    group = temp_chanel1[i:i+6]
                    chanel1.append(''.join(group))
                        
        return data_packets, chanel0, chanel1

    
    
    def _process_data_pcapng(self, packets):
        # Functions for to convert hexadecimals pars in decimals
        hex_to_decimal = lambda hex_str: [int(hex_str[i:i+2], 16) 
                                            for i in range(0, len(hex_str), 2)]

        # Processamento dos dados utilizando list comprehension
        data_numeric = [hex_to_decimal(hex_str) for hex_str in packets]

        # Convertendo para um array do NumPy
        payloads = np.array(data_numeric)
        
        return payloads
    
    
    def _create_dataframe(self, csv_path, chanel0, chanel1):
        time_df = pd.read_csv(csv_path)
        time_df = time_df['Time'] 
        
        if len(time_df) != len(chanel0) or len(time_df) != len(chanel1):
            raise ValueError("The size of the time vector and the sizes of the \
                                channel0 and channel1 vectors must correspond")

        # Converter 'time' para DataFrame se não for
        if isinstance(time_df, pd.Series):
            dataframe = time_df.to_frame(name='Timestamp')
        else:
            dataframe = time_df.copy()
        
        # Adicionar as colunas de vetores
        dataframe['Chanel0'] = chanel0
        dataframe['Chanel1'] = chanel1
        return dataframe


    def label_anomalies(self, df, output_filename, attck_name='malicius', 
                            expected_interval=0.000125, multiplier=2):
                
        # Calculate the time difference between consecutive rows
        df['Time_Diff'] = df['Timestamp'].diff().fillna(0)
        # Calculate the threshold
        threshold = expected_interval * multiplier
        # Detect anomalies based on the threshold and label them as 'malicious' or 'benign'.
        df['Label'] = df['Time_Diff'].apply(lambda x: attck_name 
                            if (x > threshold or x < (expected_interval-0.000001)) 
                            else 'benign')
        
        # Export DataFrame to CSV
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
