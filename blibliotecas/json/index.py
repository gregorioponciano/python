import json

# Um dicionário Python (objeto)
dados_cliente = {"nome": "GPWeb", "saldo": 1050.0, "vip": True}

# Converte para uma String formatada em JSON
json_texto = json.dumps(dados_cliente, indent=4)
print(json_texto)