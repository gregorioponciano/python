import hashlib

# 1. O segredo que queremos proteger ou verificar
documento = "Relatorio Financeiro: Saldo Total R$ 1.000.000"

# 2. Criamos a 'assinatura' (Hash) original do documento
hash_original = hashlib.sha256(documento.encode()).hexdigest()

print(f"Assinatura Original: {hash_original}")

# --- SIMULAÇÃO DE ATAQUE ---
# Um invasor altera o valor para 2 milhões
documento_alterado = "Relatorio Financeiro: Saldo Total R$ 2.000.000"
hash_novo = hashlib.sha256(documento_alterado.encode()).hexdigest()

print(f"Assinatura após alteração: {hash_novo}")

# 3. Comparação de segurança
if hash_original == hash_novo:
    print("\n✅ O arquivo é autêntico e seguro.")
else:
    print("\n❌ ALERTA: O arquivo foi modificado ou corrompido!")