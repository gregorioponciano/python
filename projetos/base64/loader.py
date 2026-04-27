import base64

# Este é o código ofuscado (neste exemplo, ele apenas imprime "Olá, Mundo!")
# O conteúdo original era: print("Acesso concedido. Sistema iniciado.")
codigo_ofuscado = "ZGVmIHNhdWRhcl91c3VhcmlvKG5vbWUsIHBlcmlvZG89ImRpYSIpOiAjcGVyaW9kbyB0ZW0gdW0gdmFsb3IgcGFkcmFvCiAgICByZXR1cm4gZiJCb20ge3BlcmlvZG99LCB7bm9tZX0hIgoKI2NoYW1hbmRvIGZ1bmNhbyAKcHJpbnQoc2F1ZGFyX3VzdWFyaW8oIkNhcmxvcyIpKQojdXNhIGEgZnVuY2FvIGRpYQpwcmludChzYXVkYXJfdXN1YXJpbygiQW5hIiwgIm5vaXRlIikpCiNzb2JyZXNjcmV2ZSBwYXJhIG5vaXRl"

def executar_ofuscado(payload):
    try:
        # 1. Decodifica a string Base64 para bytes
        bytes_decodificados = base64.b64decode(payload)
        
        # 2. Converte os bytes de volta para string (UTF-8)
        script_original = bytes_decodificados.decode('utf-8')
        
        # 3. Executa o código dentro do ambiente Python atual
        exec(script_original)
        
    except Exception as e:
        print(f"Erro ao executar o código: {e}")

# Rodando o código
executar_ofuscado(codigo_ofuscado)
