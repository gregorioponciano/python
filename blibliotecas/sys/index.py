# O sys te dá informações sobre como o Python
# está rodando e permite interagir com o interpretador.
import sys  

# 1. Mostrar qual versão do Python você está usando
print(f"Versão do Python: {sys.version}")

# 2. Mostrar onde o Python está instalado no seu PC
print(f"O Python está em: {sys.executable}")

# 3. Encerrar o programa imediatamente (útil para erros graves)
# sys.exit()