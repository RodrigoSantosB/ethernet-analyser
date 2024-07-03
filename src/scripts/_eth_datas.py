from _eth_libs import *
class DataProcessing:
    def __init__(self) -> None:
        ...
        
    def dataset_transform(self, path):
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        dfs = []
        
        for arquivo in files:
            try:
                df = pd.read_csv(os.path.join(path, arquivo))
                dfs.append(df)
            except pd.errors.ParserError as e:
                print(f"Erro ao ler o arquivo {arquivo}: {e}")
                continue
        
        if not dfs:
            raise ValueError("Nenhum arquivo foi processado com sucesso.")
        
        df_concat = pd.concat(dfs, ignore_index=True)
        
        return df_concat

        
        
    # Plotar distribuićão de classe
    def plot_class_distribution(self, datas):
        hist1 =  px.histogram (datas,  x = "Label", nbins=60) 
        hist1.update_layout(width=800,
                            height=500,
                            title_text='<b>Distribuição dos attcks</b>') 
        hist1.show()
