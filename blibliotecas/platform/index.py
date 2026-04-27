# Use este código para saber em que tipo de máquina o
# seu Python está "morando".
import platform

# Mostra o sistema operacional (Windows, Linux, Darwin/Mac)
print(f"Sistema Operacional: {platform.system()}")

# Mostra a versão do sistema
print(f"Versão: {platform.release()}")

# Mostra o tipo de processador (ex: Intel, AMD, Arm)
print(f"Arquitetura: {platform.machine()}")