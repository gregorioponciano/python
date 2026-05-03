import struct

# Transforma o número 1024 em um formato binário de 4 bytes
binario = struct.pack('i', 1024)
print(f"O número 1024 em binário 'bruto' é: {binario}")