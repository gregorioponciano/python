import pandas as pd # Importa a biblioteca

# 1. Carregar o arquivo CSV para um DataFrame
# O pandas lê o arquivo e já cria a estrutura de tabela
df = pd.read_csv('dados.csv')

# 2. Visualizar as primeiras linhas
print("--- Primeiras 5 linhas do arquivo ---")
print(df.head()) # .head() mostra o topo da tabela

# 3. Analisar informações básicas
print("\n--- Resumo Estatístico ---")
print(df.describe()) # Mostra média, valor máximo, mínimo, etc.

# 4. Filtrar dados (ex: apenas funcionários de TI)
funcionarios_ti = df[df['Departamento'] == 'TI']

print("\n--- Funcionários do Departamento de TI ---")
print(funcionarios_ti)

# 5. Salvar um novo CSV (ex: apenas o filtro de TI)
# index=False evita que o Pandas crie uma coluna extra de números
funcionarios_ti.to_csv('apenas_ti.csv', index=False)
print("\nArquivo 'apenas_ti.csv' criado com sucesso!")
