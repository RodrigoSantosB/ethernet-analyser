import sys
import os
from functools import partial
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from scripts._eth_libs import *
from scripts._eth_model_evaluation import ModelEvaluation


def hex_to_decimal(hex_str):
    try:
        return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]
    except ValueError:
        # Retorna uma lista vazia se a string não for válida
        return []

data = []
md  = ModelEvaluation()
label_attck = True  # Variável que define se a mensagem deve ser classificada como ataque ou benigno



def inferency(packet, model_filepath):
    global data
    global label_attck
    if packet.haslayer(Raw):
        # Receiver the packege payload
        payload = packet[Raw].load
        payload_str = payload.decode('utf-8')
        try:
            # Divide a string do payload nas colunas 'Chanel0', 'Chanel1', e 'Time_Diff'
            chanel0, chanel1, time_diff = payload_str.split(',')
            chanel0_numeric = hex_to_decimal(chanel0)
            chanel1_numeric = hex_to_decimal(chanel1)
            time_float = float(time_diff)
            data.append(chanel0_numeric + chanel1_numeric + [time_float])
        except ValueError:
            print(f"Payload mal formatado: {payload_str}")

        # Make the inference network:    
        model = md.load_trained_model(model_filepath)
        predictions = model.predict(data)

        messages = [f"{payload}" for _ in range(len(predictions))]  # substitua pelo conteúdo real das mensagens
                
        # Nome do arquivo CSV
        csv_file = 'predictions.csv'

        # Função para salvar o DataFrame em um arquivo CSV
        def save_to_csv(df, file_name):
            df.to_csv(file_name, index=False)

        # Criar um DataFrame vazio com as colunas necessárias
        df = pd.DataFrame(columns=['Prediction', 'Message'])
        
        try:
            # Iterar sobre o vetor de previsão e imprimir a mensagem correspondente
            for prediction, msg in zip(predictions, messages):
                if prediction == 'benign':
                    print(f"Message is benign: {msg}")
                    new_row = pd.DataFrame({'Prediction': ['benign'], 'Message': [msg]})

                elif prediction == 'delay_attck':
                    print(f"Message is delay attack: {msg}")
                    new_row = pd.DataFrame({'Prediction': ['delay attack'], 'Message': [msg]})

                elif prediction == 'sequency_attck':
                    print(f"Message is sequence attack: {msg}")
                    new_row = pd.DataFrame({'Prediction': ['sequence attack'], 'Message': [msg]})
                    
                elif prediction == 0:
                    print(f"Message is benign: {msg}")
                    new_row = pd.DataFrame({'Prediction': ['benign'], 'Message': [msg]})
                    
                
                elif prediction == 1:
                    print(f"Message is malignant: {msg}")
                    new_row = pd.DataFrame({'Prediction': ['malignant'], 'Message': [msg]})
                    
                else:
                    print(f"Message is unknown attack: {msg} sing the prediction")
                    new_row = pd.DataFrame({'Prediction': ['unknown attack'], 'Message': [msg]})
                df = pd.concat([df, new_row], ignore_index=True)

                if len(df) % 20 == 0:
                    save_to_csv(df, csv_file)       

            # Salvar o DataFrame final após a conclusão do loop
            save_to_csv(df, csv_file)   
                    
        except ValueError as e:
            print(e)
            
            
def listen(model_filepath, interface='veth1', export_interval=60, output_file='amostra.csv'):
    global data
    start_time = time.time()
    while True:
        
        inferency_callback = partial(inferency, model_filepath=model_filepath)
        sniff(iface=interface, prn=inferency_callback, store=0, timeout=1)
        current_time = time.time()
        if current_time - start_time >= export_interval:
            if data:
                df = pd.DataFrame(data, columns=[f'Chanel0_{i}' for i in range(len(data[0])//2)] + 
                                    [f'Chanel1_{i}' for i in range(len(data[0])//2)] + ['Time_Diff'])
                df.to_csv(output_file, index=False)
                print(f"Dados exportados para {output_file}")
            start_time = current_time
            data = []

if __name__ == '__main__':

    interface = 'veth0'
    model_filepath = '/home/rsb6/Desktop/LIVE/ATV4/ethernet-analyser/tests/trained_models/models_multclass/forest_model.pkl'
    listen(model_filepath, interface)
