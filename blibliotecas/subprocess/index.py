# Ele serve para o Python "mandar"
# o windows ou Linux abrir um programa externo.
import subprocess

print("Abrindo o Bloco de Notas...")

# No Windows, o comando 'notepad.exe' abre o editor de texto
# No Linux, você poderia usar 'gedit' ou 'nano'
subprocess.run(["code"]) 
# subprocess.run(["code", "--list-extensions"]) 

print("Você fechou o Bloco de Notas e voltou para o Python!")