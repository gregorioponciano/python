def saudar_usuario(nome, periodo="dia"): #periodo tem um valor padrao
    return f"Bom {periodo}, {nome}!"

#chamando funcao 
print(saudar_usuario("Carlos"))
#usa a funcao dia
print(saudar_usuario("Ana", "noite"))
#sobrescreve para noite
