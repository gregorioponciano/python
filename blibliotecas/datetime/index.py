# Essencial para registrar quando as coisas acontecem.
from datetime import datetime

# 1. Pega a data e hora exata de agora
agora = datetime.now()

# 2. Formata para ficar bonito (Dia/Mês/Ano Hora:Minuto)
data_formatada = agora.strftime("%d/%m/%Y %H:%M:%S")

print(f"Relatório gerado em: {data_formatada}")
# No seu banco, você usaria isso em cada depósito ou saque!