import pandas as pd  # Importamos e apelidamos de 'pd' para facilitar

# 1. Criando um conjunto de dados (como se fosse uma planilha)
dados = {
    'Produto': ['Teclado', 'Mouse', 'Monitor', 'Mouse', 'Teclado'],
    'Preço': [150, 80, 900, 80, 150],
    'Quantidade': [2, 5, 1, 3, 1]
}

# 2. Transformando esses dados em um DataFrame (Tabela do Pandas)
df = pd.DataFrame(dados)

print("--- Tabela Completa ---")
print(df)

# 3. Fazendo cálculos simples
# Vamos criar uma nova coluna chamada 'Total' (Preço * Quantidade)
df['Total'] = df['Preço'] * df['Quantidade']

print("\n--- Tabela com a coluna Total ---")
print(df)

# 4. Filtrando os dados
# Queremos ver apenas onde o produto é 'Mouse'
mouses = df[df['Produto'] == 'Mouse']

print("\n--- Apenas as vendas de Mouse ---")
print(mouses)

# 5. Resumo estatístico rápido
print("\n--- Valor total vendido ---")
print(df['Total'].sum()) # Soma todos os valores da coluna Total
