from _eth_libs import *
    
class DataProcessing:
    def __init__(self) -> None:
        ...
        
        
    def undersample_to_minority_class(self, df, target_column):
        """
        Aplica undersampling ao dataset para que todas as classes fiquem equilibradas, 
        com o número de instâncias igual ao da classe minoritária.
        
        Parâmetros:
        - df: DataFrame contendo os dados.
        - target_column: Nome da coluna de alvo (classe) no DataFrame.
        
        Retorna:
        - DataFrame com undersampling aplicado.
        """
        # Identifica a classe minoritária
        class_counts = df[target_column].value_counts()
        min_class_count = class_counts.min()
        
        # Lista para armazenar os DataFrames subamostrados
        df_list = []
        
        # Realiza o undersampling para cada classe
        for class_value in class_counts.index:
            df_class = df[df[target_column] == class_value]
            df_class_undersampled = resample(df_class, 
                                                replace=False,    # sem substituição
                                                n_samples=min_class_count,  # para igualar o número de instâncias da classe minoritária
                                                random_state=42) # para reprodutibilidade
            df_list.append(df_class_undersampled)
        
        # Combina todos os DataFrames subamostrados
        df_undersampled = pd.concat(df_list)
            
        return df_undersampled

    def oversample_to_majority_class(self, df, target_column):
        """
        Aplica oversampling ao dataset para que todas as classes fiquem equilibradas, 
        com o número de instâncias igual ao da classe majoritária.
        
        Parâmetros:
        - df: DataFrame contendo os dados.
        - target_column: Nome da coluna de alvo (classe) no DataFrame.
        
        Retorna:
        - DataFrame com oversampling aplicado.
        """
        ros = RandomOverSampler(random_state=42)
        X = df.drop(columns=[target_column])
        y = df[target_column]
        X_resampled, y_resampled = ros.fit_resample(X, y)
        
        df_resampled = pd.concat([X_resampled, pd.Series(y_resampled, name=target_column)], axis=1)
        
        return df_resampled
            
    def dataset_transform(self, path, selected_features=None, all_dataframe=False, sampling_method=None):
        """
        Transforma o dataset e aplica o método de sampling se especificado.
        
        Parâmetros:
        - path: Caminho para os arquivos CSV.
        - selected_features: Lista de features selecionadas.
        - sampling_method: Método de sampling ('undersampling' ou 'oversampling').
        
        Retorna:
        - DataFrame original, DataFrame transformado, e target.
        """
        if all_dataframe:
            # columns = ['Timestamp', 'Chanel0', 'Chanel1', 'Time_Diff', 'Label']
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            dfs = [pd.read_csv(os.path.join(path, arquivo), sep=',', engine='python') for arquivo in files]

            df_concat = pd.concat(dfs, ignore_index=True)
            df_concat = df_concat.drop(['Timestamp'], axis=1)
        else:
            df_concat = pd.read_csv(path)
        
        # Aplicar o método de sampling se especificado
        if sampling_method == 'undersampling':
            df_concat = self.undersample_to_minority_class(df_concat, 'Label')
        elif sampling_method == 'oversampling':
            df_concat = self.oversample_to_majority_class(df_concat, 'Label')

        # Função para converter pares hexadecimais em decimais
        def hex_to_decimal(hex_str):
            try:
                return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]
            except ValueError:
                # Retorna uma lista vazia se a string não for válida
                return []

        # Converter valores para string e tratar valores ausentes
        df_concat['Chanel0'] = df_concat['Chanel0'].fillna('').astype(str)
        df_concat['Chanel1'] = df_concat['Chanel1'].fillna('').astype(str)

        # Processar chanel0 e chanel1
        chanel0_array = df_concat['Chanel0'].values
        chanel1_array = df_concat['Chanel1'].values

        chanel0_numeric = [hex_to_decimal(ch) for ch in chanel0_array]
        chanel1_numeric = [hex_to_decimal(ch) for ch in chanel1_array]

        # Padronizar o comprimento das sublistas
        max_len = max(max(len(sublist) for sublist in chanel0_numeric), max(len(sublist) for sublist in chanel1_numeric))

        def pad_list(lst, length):
            return lst + [0] * (length - len(lst))
        
        chanel0_numeric = np.array([pad_list(sublist, max_len) for sublist in chanel0_numeric])
        chanel1_numeric = np.array([pad_list(sublist, max_len) for sublist in chanel1_numeric])
        
        # Criar um novo dataframe para armazenar os dados numéricos
        data_numeric = pd.DataFrame()

        # Adicionar colunas conforme as features selecionadas
        if selected_features:
            if 'chanel0' in selected_features:
                for i in range(max_len):
                    data_numeric[f'Chanel0_{i}'] = chanel0_numeric[:, i]
            if 'chanel1' in selected_features:
                for i in range(max_len):
                    data_numeric[f'Chanel1_{i}'] = chanel1_numeric[:, i]
            # Adicionar outras features conforme necessário
            
            if 'time_diff' in selected_features:
                data_numeric['Time_Diff'] = df_concat['Time_Diff'].values
        
        else:
            # Caso contrário, usar todas as colunas padrão
            for i in range(max_len):
                data_numeric[f'Chanel0_{i}'] = chanel0_numeric[:, i]
                data_numeric[f'Chanel1_{i}'] = chanel1_numeric[:, i]
        
        # Extrair os valores alvo
        target = df_concat['Label'].values
        data_numeric = data_numeric.values

        return df_concat, data_numeric, target

        
    # Plotar distribuićão de classe
    def plot_class_distribution(self, datas):
        hist1 =  px.histogram (datas,  x = "Label", nbins=60) 
        hist1.update_layout(width=800,
                            height=500,
                            title_text='<b>Distribuição dos attcks</b>') 
        hist1.show()

    
    def encode_dataframe(self, dataset, target, classify_to_binary=True):
        datas = dataset.copy ( deep = True )
        tam = len(datas.columns)
        
        # Substituir 'benign' por 0 e outras labels por 1
        if classify_to_binary:
            datas['Label'] = datas['Label'].apply(lambda x: 0 if x == 'benign' else 1)
        
        if classify_to_binary:
            target  = datas.iloc[:, (tam-1)].values
        return datas, target
