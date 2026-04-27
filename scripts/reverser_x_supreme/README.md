# Reverser X Supreme

Arsenal completo de engenharia reversa e quebra de criptografia.

## Funcionalidades

- Analise estatica avancada (magic numbers, strings, padroes, estruturas PE/ELF/ZIP/PDF)
- Quebra de criptografia (XOR single/multi-byte, AES, DES, RSA)
- Descompressao multipla (GZIP, ZIP, BZ2, LZMA, ZLIB)
- Decodificacao (Base64, Base32, Hex, URL, ROT13, UTF-16)
- Quebra de hashes (MD5, SHA1, SHA256, SHA512, NTLM)
- Rainbow tables manager
- Menu interativo completo
- Modo CLI automatizado

## Instalacao

```bash
python setup.py
```

Ou manualmente:

```bash
pip install -r requirements.txt
mkdir -p output wordlists logs temp results config rainbow_tables
```

## Uso

### Modo interativo

```bash
python main.py -i
```

### Modo CLI

```bash
# Analise de arquivo
python main.py -f arquivo.bin

# Analise de string
python main.py -s "SGVsbG8gV29ybGQ="

# Salvar resultado
python main.py -f encrypted.dat -o decrypted.txt

# Analise avancada
python main.py -f suspicious.bin --max-depth 15 --timeout 60 --verbose

# Exportar todos os resultados
python main.py -f data.bin --export-all --export-dir ./output

# Ler de pipe
cat file.bin | python main.py --stdin
```

## Estrutura do Projeto

```
reverser_x_supreme/
├── main.py                 # Entry point principal
├── setup.py                # Instalador
├── requirements.txt        # Dependencias
├── README.md               # Documentacao
├── core/
│   ├── __init__.py
│   ├── engine.py           # Motor principal (pipeline de analise)
│   ├── analyzer.py         # Analisador estatico
│   ├── crypto_breaker.py   # Quebra de criptografia (AES, DES, RSA)
│   ├── hash_cracker.py     # Quebra de hashes
│   ├── decompressor.py     # Descompressao multipla
│   ├── encoder_decoder.py  # Encoding/Decoding
│   └── xor_attacks.py      # Ataques XOR
├── utils/
│   ├── __init__.py
│   ├── constants.py        # Constantes e configuracoes
│   ├── helpers.py          # Funcoes auxiliares
│   └── rainbow_tables.py   # Gerenciador de rainbow tables
├── menus/
│   ├── __init__.py
│   ├── main_menu.py        # Menu principal interativo
│   ├── crypto_menu.py      # Menu de criptografia
│   └── analysis_menu.py    # Menu de analise
├── wordlists/
│   ├── common_passwords.txt
│   ├── common_keys.txt
│   └── rockyou_sample.txt
└── output/                 # Resultados exportados
```

## Dependencias

- Python 3.8+
- pycryptodome
- cryptography
- colorama

## Licenca

MIT
