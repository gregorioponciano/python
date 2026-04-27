#!/usr/bin/env python3
"""REVERSER X SUPREME - Main Entry Point"""

import os
import sys
import argparse
import time
import signal
import traceback
from typing import Optional, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    from utils.constants import VERSION, Colors, load_config
    from core.engine import ReverserEngine
    from menus.main_menu import MainMenu
    from utils.helpers import setup_logger, print_analysis, safe_file_write
except ImportError as e:
    print(f"Erro ao importar modulos: {e}")
    print("Execute 'python setup.py' primeiro para instalar dependencias")
    sys.exit(1)

logger = None
config = None
start_time = None


def signal_handler(signum: int, frame) -> None:
    global start_time
    print(f"\n{Colors.YELLOW}[!] Sinal recebido: {signum}{Colors.RESET}")
    if signum == signal.SIGINT:
        elapsed = time.time() - start_time if start_time else 0
        print(f"{Colors.YELLOW}[!] Programa interrompido apos {elapsed:.1f} segundos{Colors.RESET}")
        sys.exit(0)
    elif signum == signal.SIGTERM:
        print(f"{Colors.YELLOW}[!] Programa terminado pelo sistema{Colors.RESET}")
        sys.exit(0)


def setup_signal_handlers() -> None:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except Exception:
        pass


def initialize_system() -> bool:
    global logger, config, start_time
    start_time = time.time()

    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}  REVERSER X SUPREME - Sistema de Engenharia Reversa{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.GREEN}  Versao: {VERSION}{Colors.RESET}")
    print(f"{Colors.GREEN}  Autor: Reverser X Team{Colors.RESET}")
    print(f"{Colors.GREEN}  Inicializacao: {time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

    try:
        config = load_config()
        print(f"{Colors.GREEN}[+] Configuracoes carregadas{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.YELLOW}[!] Erro ao carregar configuracoes: {e}{Colors.RESET}")
        config = {}

    try:
        log_file = config.get('log_file', 'logs/reverser.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logger = setup_logger('ReverserX', log_file)
        logger.info(f"Sistema iniciado - Versao {VERSION}")
        print(f"{Colors.GREEN}[+] Logger configurado{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.YELLOW}[!] Erro ao configurar logger: {e}{Colors.RESET}")
        logger = None

    critical_modules = ['Crypto', 'colorama']
    missing = []
    for module in critical_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        print(f"{Colors.RED}[-] Modulos faltando: {', '.join(missing)}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Execute 'python setup.py' para instalar dependencias{Colors.RESET}")
        return False

    print(f"{Colors.GREEN}[+] Dependencias verificadas{Colors.RESET}")
    elapsed = time.time() - start_time
    print(f"{Colors.GREEN}[+] Sistema inicializado em {elapsed:.2f} segundos{Colors.RESET}\n")
    return True


def process_file(filepath: str, options: Dict[str, Any]) -> Optional[bytes]:
    if logger:
        logger.info(f"Processando arquivo: {filepath}")

    if not os.path.exists(filepath):
        print(f"{Colors.RED}[-] Arquivo nao encontrado: {filepath}{Colors.RESET}")
        return None

    file_size = os.path.getsize(filepath)
    max_size = options.get('max_size', 100 * 1024 * 1024)

    if file_size > max_size:
        print(f"{Colors.YELLOW}[!] Arquivo muito grande: {file_size} bytes{Colors.RESET}")
        if not options.get('force', False):
            return None
        print(f"{Colors.CYAN}[*] Forcando leitura...{Colors.RESET}")

    try:
        print(f"{Colors.CYAN}[*] Lendo arquivo: {filepath}{Colors.RESET}")
        with open(filepath, 'rb') as f:
            data = f.read()
        print(f"{Colors.GREEN}[+] Arquivo lido: {len(data)} bytes{Colors.RESET}")
        if logger:
            logger.info(f"Arquivo lido: {len(data)} bytes")
        return data
    except MemoryError:
        print(f"{Colors.RED}[-] Memoria insuficiente{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.RED}[-] Erro ao ler arquivo: {e}{Colors.RESET}")
        if logger:
            logger.error(f"Erro ao ler arquivo: {e}")
        return None


def process_string(string_data: str, options: Dict[str, Any]) -> Optional[bytes]:
    if logger:
        logger.info(f"Processando string: {string_data[:50]}...")
    try:
        for encoding in ['utf-8', 'latin-1', 'ascii', 'cp1252']:
            try:
                data = string_data.encode(encoding)
                print(f"{Colors.GREEN}[+] String codificada como: {encoding}{Colors.RESET}")
                return data
            except Exception:
                continue
        data = string_data.encode('utf-8', errors='ignore')
        print(f"{Colors.YELLOW}[!] Usando fallback: utf-8 com ignore{Colors.RESET}")
        return data
    except Exception as e:
        print(f"{Colors.RED}[-] Erro ao processar string: {e}{Colors.RESET}")
        if logger:
            logger.error(f"Erro ao processar string: {e}")
        return None


def save_results(data: bytes, output_path: str, options: Dict[str, Any]) -> bool:
    if not data:
        print(f"{Colors.YELLOW}[!] Nada para salvar{Colors.RESET}")
        return False
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        success = safe_file_write(output_path, data, backup=options.get('backup', True))
        if success:
            print(f"{Colors.GREEN}[+] Resultado salvo: {output_path}{Colors.RESET}")
            print(f"{Colors.GREEN}[+] Tamanho: {len(data)} bytes{Colors.RESET}")
            if logger:
                logger.info(f"Resultado salvo: {output_path} ({len(data)} bytes)")
            return True
        print(f"{Colors.RED}[-] Erro ao salvar resultado{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}[-] Erro ao salvar: {e}{Colors.RESET}")
        if logger:
            logger.error(f"Erro ao salvar: {e}")
        return False


def run_interactive_mode() -> None:
    global logger, config
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}                    MODO INTERATIVO ATIVADO{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")
    try:
        menu = MainMenu(config)
        menu.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Modo interativo interrompido{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[-] Erro no modo interativo: {e}{Colors.RESET}")
        if logger:
            logger.error(f"Erro no modo interativo: {e}")
            logger.error(traceback.format_exc())
        traceback.print_exc()


def run_auto_mode(args: argparse.Namespace) -> int:
    global logger, config
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}                     MODO AUTOMATICO ATIVADO{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

    options = {
        'max_depth': args.max_depth or config.get('max_depth', 10),
        'timeout': args.timeout or config.get('timeout', 30),
        'force': args.force,
        'verbose': args.verbose,
        'backup': True,
        'max_size': args.max_size or 100 * 1024 * 1024,
    }

    if args.file:
        data = process_file(args.file, options)
    elif args.string:
        data = process_string(args.string, options)
    elif args.stdin:
        print(f"{Colors.CYAN}[*] Lendo de stdin...{Colors.RESET}")
        data = sys.stdin.buffer.read()
        print(f"{Colors.GREEN}[+] Lidos {len(data)} bytes de stdin{Colors.RESET}")
    else:
        print(f"{Colors.RED}[-] Nenhuma fonte de entrada especificada{Colors.RESET}")
        return 1

    if not data:
        print(f"{Colors.RED}[-] Falha ao carregar dados{Colors.RESET}")
        return 1

    try:
        print(f"{Colors.CYAN}[*] Iniciando analise...{Colors.RESET}")
        engine = ReverserEngine(config=config, logger=logger)
        results = engine.run_full_analysis(data)

        if not results:
            print(f"{Colors.YELLOW}[!] Nenhum resultado encontrado{Colors.RESET}")
            return 1

        print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}\n")

        for i, result in enumerate(results[:10], 1):
            print(f"{Colors.CYAN}[{i}] {result.engine}: {result.method}{Colors.RESET}")
            print(f"    Tamanho: {len(result.data)} bytes")
            if options['verbose']:
                preview = result.data[:100]
                print(f"    Preview: {preview}...")
            print()

        if args.output:
            best_result = results[0].data
            save_results(best_result, args.output, options)

        if args.export_all:
            export_dir = args.export_dir or 'results'
            os.makedirs(export_dir, exist_ok=True)
            timestamp = int(time.time())
            for i, result in enumerate(results):
                filename = f"{export_dir}/result_{timestamp}_{i}_{result.engine}.bin"
                save_results(result.data, filename, options)

        return 0
    except TimeoutError:
        print(f"{Colors.RED}[-] Timeout durante analise{Colors.RESET}")
        return 1
    except MemoryError:
        print(f"{Colors.RED}[-] Memoria insuficiente{Colors.RESET}")
        return 1
    except Exception as e:
        print(f"{Colors.RED}[-] Erro durante analise: {e}{Colors.RESET}")
        if logger:
            logger.error(f"Erro durante analise: {e}")
            logger.error(traceback.format_exc())
        if args.debug:
            traceback.print_exc()
        return 1


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"REVERSER X SUPREME v{VERSION} - Arsenal Completo de Engenharia Reversa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.CYAN}EXEMPLOS DE USO:{Colors.RESET}

  python main.py -f malware.bin
  python main.py -i
  python main.py -s "SGVsbG8gV29ybGQ="
  python main.py -f encrypted.dat -o decrypted.txt
  python main.py -f suspicious.bin --max-depth 15 --timeout 60 --verbose
  python main.py -f data.bin --export-all --export-dir ./output
  cat file.bin | python main.py --stdin
"""
    )

    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument("-f", "--file", type=str, help="Arquivo de entrada")
    input_group.add_argument("-s", "--string", type=str, help="String para analise")
    input_group.add_argument("--stdin", action="store_true", help="Ler de stdin")

    parser.add_argument("-o", "--output", type=str, help="Salvar melhor resultado")
    parser.add_argument("--export-all", action="store_true", help="Exportar todos os resultados")
    parser.add_argument("--export-dir", type=str, default="results", help="Diretorio de exportacao")
    parser.add_argument("-i", "--interactive", action="store_true", help="Modo interativo")
    parser.add_argument("--max-depth", type=int, help="Profundidade maxima")
    parser.add_argument("--timeout", type=int, help="Timeout em segundos")
    parser.add_argument("--max-size", type=int, help="Tamanho maximo do arquivo (bytes)")
    parser.add_argument("--force", action="store_true", help="Forcar analise")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo verboso")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    parser.add_argument("--version", action="version", version=f"Reverser X Supreme v{VERSION}")

    return parser


def main() -> int:
    global start_time
    setup_signal_handlers()

    if not initialize_system():
        print(f"{Colors.RED}[-] Falha na inicializacao do sistema{Colors.RESET}")
        return 1

    parser = create_argument_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        print(f"\n{Colors.YELLOW}[!] Nenhum argumento. Use -i para modo interativo.{Colors.RESET}")
        return 0

    if args.interactive:
        run_interactive_mode()
        return 0
    else:
        return run_auto_mode(args)


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Programa interrompido{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}[-] Erro fatal: {e}{Colors.RESET}")
        traceback.print_exc()
        sys.exit(1)
