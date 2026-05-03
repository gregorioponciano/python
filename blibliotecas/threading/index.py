import threading
import time

def tarefa_demorada():
    print("Iniciando backup em segundo plano...")
    time.sleep(3)
    print("\n[AVISO] Backup concluído!")

# Cria e inicia a linha de execução (thread) separada
threading.Thread(target=tarefa_demorada).start()

print("O programa principal continua rodando normalmente...")