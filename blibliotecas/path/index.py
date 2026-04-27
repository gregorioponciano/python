# Ele é o jeito mais atual de lidar 
# com pastas e arquivos. É mais intuitivo que o os.
from pathlib import Path

# 1. Cria um objeto que representa um arquivo chamado 'historico.txt'
arquivo = Path("historico.txt")

# 2. Verifica se ele existe de forma simples
if arquivo.exists():
    print("O arquivo de histórico já existe!")
else:
    # Cria o arquivo vazio se não existir
    arquivo.touch()
    print("Arquivo 'historico.txt' criado com sucesso!")