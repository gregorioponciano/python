#!/usr/bin/env python3
"""Setup e instalador do Reverser X Supreme"""

import os
import sys
import subprocess


def print_banner():
    print("=" * 70)
    print("  REVERSER X SUPREME - INSTALADOR PROFISSIONAL")
    print("=" * 70)
    print("  Versao: 3.0.0")
    print("  Autor: Reverser X Team")
    print("  Licenca: MIT")
    print("=" * 70 + "\n")


def check_python_version():
    print("[1/6] Verificando Python...")
    if sys.version_info < (3, 8):
        print(f"ERRO: Python 3.8+ e necessario. Versao atual: {sys.version}")
        sys.exit(1)
    print(f"OK Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def create_directories():
    print("\n[2/6] Criando estrutura de diretorios...")
    directories = ["output", "wordlists", "logs", "temp", "results", "config", "rainbow_tables"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"    Criado: {directory}/")
        else:
            print(f"    Ja existe: {directory}/")
    return True


def install_dependencies():
    print("\n[3/6] Instalando dependencias...")
    dependencies = [
        "pycryptodome>=3.19.0",
        "cryptography>=41.0.7",
        "colorama>=0.4.6",
        "pyfiglet>=0.8.post1",
        "tqdm>=4.66.1",
        "rich>=13.7.0",
    ]
    for dep in dependencies:
        try:
            print(f"    Instalando {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep, "--quiet"])
            print(f"    OK {dep}")
        except Exception as e:
            print(f"    Erro ao instalar {dep}: {e}")
    return True


def create_wordlists():
    print("\n[4/6] Criando wordlists...")

    common_passwords = [
        "password", "123456", "123456789", "admin", "root", "toor",
        "qwerty", "abc123", "letmein", "monkey", "dragon", "master",
        "shadow", "secret", "12345", "password123", "admin123",
        "welcome", "login", "test", "user", "guest", "default",
    ]
    with open("wordlists/common_passwords.txt", "w") as f:
        for pwd in common_passwords:
            f.write(pwd + "\n")

    common_keys = [
        "key", "secretkey", "encryptionkey", "aeskey", "rsakey",
        "privatekey", "publickey", "cryptokey", "masterkey",
    ]
    with open("wordlists/common_keys.txt", "w") as f:
        for key in common_keys:
            f.write(key + "\n")

    rockyou_sample = [
        "123456", "12345", "123456789", "password", "iloveyou",
        "princess", "1234567", "rockyou", "12345678", "abc123",
        "nicole", "daniel", "babygirl", "monkey", "lovely",
        "jessica", "654321", "michael", "ashley", "qwerty",
        "111111", "iloveu", "000000", "michelle", "tigger",
        "sunshine", "chocolate", "password1", "soccer", "anthony",
        "friends", "butterfly", "purple", "angel", "jordan",
        "liverpool", "justin", "loveme", "fuckyou", "123123",
        "football", "secret", "andrea", "carlos", "jennifer",
        "joshua", "bubbles", "1234567890", "superman", "hannah",
        "amanda", "loveyou", "pretty", "basketball", "andrew",
        "angels", "tweety", "flower", "playboy", "hello",
        "charlie", "donald", "love123", "testing", "pass",
    ]
    with open("wordlists/rockyou_sample.txt", "w") as f:
        for pwd in rockyou_sample:
            f.write(pwd + "\n")

    print("    Wordlists criadas com sucesso")
    return True


def create_config():
    print("\n[5/6] Criando configuracao...")
    config_content = """{
    "version": "3.0.0",
    "max_depth": 10,
    "timeout": 30,
    "brute_force_limit": 1000000,
    "entropy_threshold": 7.5,
    "min_printable_ratio": 0.7,
    "xor_max_key_size": 50,
    "auto_export": true,
    "verbose": true,
    "save_logs": true,
    "output_dir": "output",
    "wordlist_dir": "wordlists",
    "temp_dir": "temp",
    "log_dir": "logs"
}
"""
    with open("config/settings.json", "w") as f:
        f.write(config_content)
    print("    Configuracao criada")
    return True


def final_check():
    print("\n[6/6] Verificacao final...")
    try:
        import Crypto
        print("    OK PyCryptodome")
    except ImportError:
        print("    AVISO PyCryptodome nao encontrado")
    try:
        import colorama
        print("    OK Colorama")
    except ImportError:
        print("    AVISO Colorama nao encontrado")

    print("\n" + "=" * 70)
    print("INSTALACAO CONCLUIDA COM SUCESSO!")
    print("=" * 70)
    print("\nPara iniciar:")
    print("  python main.py")
    print("\nOu em modo interativo:")
    print("  python main.py --interactive")
    print("=" * 70 + "\n")
    return True


def main():
    print_banner()
    try:
        check_python_version()
        create_directories()
        install_dependencies()
        create_wordlists()
        create_config()
        final_check()
    except KeyboardInterrupt:
        print("\nInstalacao interrompida pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro durante instalacao: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
