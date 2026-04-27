#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Busca Profissional GPWEB
Versão: 2.0.3
Autor: GPWEB Systems
Descrição: Sistema avançado de busca em arquivos CSV
"""

# ============================================================================
# IMPORTAÇÃO DE BIBLIOTECAS
# ============================================================================
import pandas as pd
import os
import sys
import subprocess
import time
import hashlib
import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Any
import logging
from dataclasses import dataclass, asdict
import re

# ============================================================================
# CONFIGURAÇÕES DO SISTEMA
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gpweb_search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GPWEB_Search')

CONFIG_FILE = 'gpweb_config.json'
HISTORY_FILE = 'gpweb_history.json'
CACHE_FILE = 'gpweb_cache.db'
MAX_HISTORY = 100
CACHE_EXPIRY_DAYS = 7

# Colunas para busca - APENAS estas serão exibidas
COLUNAS_PESSOAIS = ['Nome', 'CPF', 'Email', 'Telefone', 'Parentesco']


@dataclass
class SearchResult:
    query: str
    column: str
    count: int
    timestamp: str
    duration: float


@dataclass
class Config:
    theme: str = "default"
    max_results_display: int = 50
    enable_cache: bool = True
    enable_history: bool = True
    auto_export: bool = False
    export_format: str = "json"
    fuzzy_search: bool = True
    case_sensitive: bool = False


# ============================================================================
# CLASSE DE INTERFACE
# ============================================================================

class GPWEBInterface:
    def __init__(self):
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'gray': '\033[90m',
            'white': '\033[97m'
        }
        
    def print_banner(self):
        try:
            figlet_text = subprocess.check_output(
                ['figlet', '-f', 'big', 'GPWEB'],
                stderr=subprocess.DEVNULL,
                universal_newlines=True
            )
            print(f"{self.colors['cyan']}{figlet_text}{self.colors['reset']}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            banner = """
╔═══════════════════════════════════════════════════════════════════╗
║   ▄████  ██▓███   █     █░▓█████  ██▀███       ██████  ▓█████   ║
║  ██▒ ▀█▒▓██░  ██▒▓█░ █ ░█░▓█   ▀ ▓██ ▒ ██▒   ▒██    ▒  ▓█   ▀   ║
║ ▒██░▄▄▄░▓██░ ██▓▒▒█░ █ ░█ ▒███   ▓██ ░▄█ ▒   ░ ▓██▄    ▒███     ║
║ ░▓█  ██▓▒██▄█▓▒ ▒░█░ █ ░█ ▒▓█  ▄ ▒██▀▀█▄       ▒   ██▒ ▒▓█  ▄   ║
║ ░▒▓███▀▒▒██▒ ░  ░░░██▒██▓ ░▒████▒░██▓ ▒██▒   ▒██████▒▒ ░▒████▒  ║
║  ░▒   ▒ ▒▓▒░ ░  ░░ ▓░▒ ▒  ░░ ▒░ ░░ ▒▓ ░▒▓░   ▒ ▒▓▒ ▒ ░ ░░ ▒░ ░  ║
║   ░   ░ ░▒ ░       ▒ ░ ░   ░ ░  ░  ░▒ ░ ▒░   ░ ░▒  ░ ░  ░ ░  ░  ║
║ ░ ░   ░ ░░         ░   ░     ░     ░░   ░    ░  ░  ░      ░     ║
║       ░            ░       ░  ░   ░               ░      ░  ░    ║
╚═══════════════════════════════════════════════════════════════════╝
"""
            print(f"{self.colors['cyan']}{banner}{self.colors['reset']}")
        
        print(f"{self.colors['gray']}{'═' * 70}{self.colors['reset']}")
        print(f"{self.colors['green']}🚀 Sistema de Busca Avançado{self.colors['reset']} | "
              f"Versão: 2.0.3 | "
              f"{self.colors['yellow']}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{self.colors['reset']}")
        print(f"{self.colors['gray']}{'═' * 70}{self.colors['reset']}\n")
    
    def print_status(self, message: str, status_type: str = "info"):
        icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}
        colors = {
            "info": self.colors['blue'],
            "success": self.colors['green'],
            "error": self.colors['red'],
            "warning": self.colors['yellow']
        }
        
        print(f"{colors.get(status_type, self.colors['white'])}{icons.get(status_type, '')} "
              f"{message}{self.colors['reset']}")
    
    def print_table(self, headers: List[str], data: List[List[Any]], max_width: int = 80):
        if not data:
            return
        
        col_widths = [len(h) for h in headers]
        for row in data:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        total_width = sum(col_widths) + len(headers) * 3
        if total_width > max_width:
            factor = max_width / total_width
            col_widths = [max(5, int(w * factor)) for w in col_widths]
        
        print(f"{self.colors['cyan']}┌{'─' * (sum(col_widths) + len(headers) * 2 + 1)}┐")
        
        header_parts = []
        for i, h in enumerate(headers):
            header_parts.append(f" {h:<{col_widths[i]}} ")
        print(f"│{'│'.join(header_parts)}│")
        
        print(f"├{'─' * (sum(col_widths) + len(headers) * 2 + 1)}┤")
        
        for row in data:
            row_parts = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_parts.append(f" {str(cell):<{col_widths[i]}} ")
            print(f"│{'│'.join(row_parts)}│")
        
        print(f"└{'─' * (sum(col_widths) + len(headers) * 2 + 1)}┘")


# ============================================================================
# CLASSE PRINCIPAL DO SISTEMA
# ============================================================================

class GPWEBSearchSystem:
    def __init__(self):
        self.interface = GPWEBInterface()
        self.config = self._load_config()
        self.dataframe = None
        self.filename = None
        self.search_history = self._load_history()
        self.cache_db = None
        
        if self.config.enable_cache:
            self._init_cache()
    
    def _init_cache(self):
        try:
            self.cache_db = sqlite3.connect(CACHE_FILE)
            cursor = self.cache_db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT UNIQUE,
                    column_name TEXT,
                    query TEXT,
                    results TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_query_hash ON search_cache(query_hash)
            ''')
            self.cache_db.commit()
            logger.info("Cache inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar cache: {e}")
            self.config.enable_cache = False
    
    def _load_config(self) -> Config:
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    if isinstance(config_data, dict):
                        return Config(**config_data)
            return Config()
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            return Config()
    
    def _save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
            self.interface.print_status("Configurações salvas com sucesso", "success")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
    
    def _load_history(self) -> List[SearchResult]:
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    if isinstance(history_data, list):
                        return [SearchResult(**h) for h in history_data if isinstance(h, dict)]
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar histórico: {e}")
            return []
    
    def _save_history(self):
        try:
            if self.config.enable_history:
                history_to_save = self.search_history[-MAX_HISTORY:]
                with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                    json.dump([asdict(h) for h in history_to_save], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {e}")
    
    def _add_to_history(self, result: SearchResult):
        if self.config.enable_history:
            self.search_history.append(result)
            self._save_history()
    
    def _get_cache_key(self, column: str, query: str) -> str:
        key = f"{column}:{query}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_from_cache(self, column: str, query: str) -> Optional[pd.DataFrame]:
        if not self.config.enable_cache or not self.cache_db:
            return None
        
        try:
            cache_key = self._get_cache_key(column, query)
            cursor = self.cache_db.cursor()
            cursor.execute('''
                SELECT results FROM search_cache 
                WHERE query_hash = ? 
                AND julianday('now') - julianday(timestamp) <= ?
            ''', (cache_key, CACHE_EXPIRY_DAYS))
            
            result = cursor.fetchone()
            if result:
                import io
                return pd.read_json(io.StringIO(result[0]))
        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
        return None
    
    def _save_to_cache(self, column: str, query: str, results: pd.DataFrame):
        if not self.config.enable_cache or not self.cache_db:
            return
        
        try:
            cache_key = self._get_cache_key(column, query)
            cursor = self.cache_db.cursor()
            results_json = results.to_json(orient='records')
            cursor.execute('''
                INSERT OR REPLACE INTO search_cache (query_hash, column_name, query, results)
                VALUES (?, ?, ?, ?)
            ''', (cache_key, column, query, results_json))
            self.cache_db.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
    
    def load_csv(self, filename: str = 'dados.csv') -> bool:
        try:
            self.interface.print_status(f"Carregando arquivo: {filename}", "info")
            
            if not os.path.exists(filename):
                self.interface.print_status(f"Arquivo '{filename}' não encontrado!", "error")
                return False
            
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
            loaded = False
            
            for encoding in encodings:
                try:
                    self.dataframe = pd.read_csv(
                        filename, 
                        sep=',', 
                        quotechar='"', 
                        skipinitialspace=True, 
                        encoding=encoding,
                        na_values=['', 'NA', 'null', 'NULL'],
                        keep_default_na=True,
                        on_bad_lines='skip'
                    )
                    loaded = True
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.warning(f"Erro com encoding {encoding}: {e}")
                    continue
            
            if not loaded:
                raise Exception("Não foi possível ler o arquivo com nenhum encoding suportado")
            
            self.dataframe.columns = self.dataframe.columns.str.strip()
            self.dataframe.dropna(axis=1, how='all', inplace=True)
            
            for col in self.dataframe.columns:
                try:
                    self.dataframe[col] = self.dataframe[col].astype(str).fillna('')
                except:
                    self.dataframe[col] = self.dataframe[col].fillna('').astype(str)
            
            self.filename = filename
            self.interface.print_status(f"✅ Arquivo carregado: {len(self.dataframe)} registros, {len(self.dataframe.columns)} colunas", "success")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {e}")
            self.interface.print_status(f"Erro crítico: {e}", "error")
            return False
    
    def search(self, column: str, term: str, use_fuzzy: bool = True) -> pd.DataFrame:
        start_time = time.time()
        
        if self.dataframe is None or self.dataframe.empty:
            self.interface.print_status("Nenhum dado carregado para busca", "error")
            return pd.DataFrame()
        
        if column not in self.dataframe.columns:
            self.interface.print_status(f"Coluna '{column}' não encontrada", "error")
            return pd.DataFrame()
        
        term = str(term).strip()
        if not term:
            return pd.DataFrame()
        
        cached_result = self._get_from_cache(column, term)
        if cached_result is not None:
            logger.info(f"Cache hit para {column}:{term}")
            return cached_result
        
        col_data = self.dataframe[column].astype(str).fillna('')
        
        if use_fuzzy and self.config.fuzzy_search:
            try:
                escaped_term = re.escape(term)
                pattern = f".*{escaped_term}.*"
                mask = col_data.str.contains(pattern, 
                                            case=not self.config.case_sensitive,
                                            na=False, 
                                            regex=True)
            except re.error:
                mask = col_data.str.contains(term, 
                                            case=not self.config.case_sensitive,
                                            na=False)
        else:
            mask = col_data.str.contains(term, 
                                        case=not self.config.case_sensitive,
                                        na=False)
        
        result = self.dataframe[mask].copy()
        
        if not result.empty:
            self._save_to_cache(column, term, result)
        
        duration = time.time() - start_time
        search_result = SearchResult(
            query=term,
            column=column,
            count=len(result),
            timestamp=datetime.now().isoformat(),
            duration=duration
        )
        self._add_to_history(search_result)
        
        logger.info(f"Busca concluída: {len(result)} resultados em {duration:.2f}s")
        
        return result
    
    def export_results(self, results: pd.DataFrame, format: str = 'json'):
        if results.empty:
            self.interface.print_status("Nenhum resultado para exportar", "warning")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            if format == 'json':
                filename = f'gpweb_results_{timestamp}.json'
                results.to_json(filename, orient='records', indent=2, force_ascii=False)
            elif format == 'csv':
                filename = f'gpweb_results_{timestamp}.csv'
                results.to_csv(filename, index=False, encoding='utf-8-sig')
            elif format == 'excel':
                filename = f'gpweb_results_{timestamp}.xlsx'
                results.to_excel(filename, index=False)
            else:
                filename = f'gpweb_results_{timestamp}.txt'
                results.to_csv(filename, sep='\t', index=False)
            
            self.interface.print_status(f"Resultados exportados para: {filename}", "success")
        except Exception as e:
            logger.error(f"Erro ao exportar: {e}")
            self.interface.print_status(f"Erro ao exportar: {e}", "error")
    
    def show_statistics(self):
        if self.dataframe is None:
            self.interface.print_status("Nenhum dado carregado", "error")
            return
        
        self.interface.print_status("📊 Estatísticas do Dataset", "info")
        
        stats_data = [
            ["Total de Registros", len(self.dataframe)],
            ["Total de Colunas", len(self.dataframe.columns)],
            ["Valores Nulos", self.dataframe.isnull().sum().sum()],
            ["Memória (MB)", f"{self.dataframe.memory_usage(deep=True).sum() / 1024 / 1024:.2f}"],
            ["Colunas Numéricas", len(self.dataframe.select_dtypes(include=['number']).columns)],
            ["Colunas Texto", len(self.dataframe.select_dtypes(include=['object']).columns)]
        ]
        
        self.interface.print_table(["Métrica", "Valor"], stats_data)
        
        print(f"\n{self.interface.colors['yellow']}📈 Top 5 Colunas por Preenchimento:{self.interface.colors['reset']}")
        completeness = []
        for col in self.dataframe.columns:
            non_empty = (self.dataframe[col] != '') & (self.dataframe[col] != 'nan') & (self.dataframe[col].notna())
            pct = (non_empty.sum() / len(self.dataframe)) * 100
            completeness.append((col, f"{pct:.1f}%"))
        
        completeness.sort(key=lambda x: float(x[1].replace('%', '')), reverse=True)
        self.interface.print_table(["Coluna", "Completude"], completeness[:5])
    
    def show_search_history(self):
        if not self.search_history:
            self.interface.print_status("Nenhuma busca realizada ainda", "info")
            return
        
        self.interface.print_status("📜 Histórico de Buscas", "info")
        
        history_data = []
        for h in reversed(self.search_history[-20:]):
            history_data.append([
                h.query[:30],
                h.column,
                h.count,
                f"{h.duration:.2f}s",
                h.timestamp[:19]
            ])
        
        self.interface.print_table(["Termo", "Campo", "Resultados", "Tempo", "Data/Hora"], history_data)
    
    def configure_system(self):
        """Menu de configuração do sistema - CORRIGIDO"""
        while True:
            print(f"\n{self.interface.colors['bold']}{'═' * 70}{self.interface.colors['reset']}")
            self.interface.print_status("⚙️ Configurações do Sistema", "info")
            print(f"{self.interface.colors['bold']}{'═' * 70}{self.interface.colors['reset']}")
            
            # Lista de opções como tuplas (texto, valor)
            opcoes = [
                (f"Tema da Interface", self.config.theme),
                (f"Máx. Resultados por Tela", self.config.max_results_display),
                (f"Cache Ativo", "Sim" if self.config.enable_cache else "Não"),
                (f"Histórico Ativo", "Sim" if self.config.enable_history else "Não"),
                (f"Busca Fuzzy", "Sim" if self.config.fuzzy_search else "Não"),
                (f"Case Sensitive", "Sim" if self.config.case_sensitive else "Não"),
                (f"Exportação Automática", "Sim" if self.config.auto_export else "Não"),
                (f"Formato de Exportação", self.config.export_format),
                (f"Voltar ao Menu Principal", "")
            ]
            
            # Mostra as opções
            for i, (texto, valor) in enumerate(opcoes, 1):
                if i < len(opcoes):
                    print(f"{self.interface.colors['cyan']}{i}.{self.interface.colors['reset']} {texto}: {self.interface.colors['yellow']}{valor}{self.interface.colors['reset']}")
                else:
                    print(f"{self.interface.colors['cyan']}{i}.{self.interface.colors['reset']} {self.interface.colors['red']}{texto}{self.interface.colors['reset']}")
            
            choice = input(f"\n{self.interface.colors['green']}Escolha uma opção (1-{len(opcoes)}): {self.interface.colors['reset']}").strip()
            
            try:
                choice_num = int(choice)
                
                if choice_num == len(opcoes):  # Última opção (Voltar)
                    self._save_config()
                    break
                elif choice_num == 1:  # Tema
                    temas = ["default", "dark", "light"]
                    current = temas.index(self.config.theme) if self.config.theme in temas else 0
                    self.config.theme = temas[(current + 1) % len(temas)]
                    self.interface.print_status(f"Tema alterado para: {self.config.theme}", "success")
                    input("Pressione ENTER para continuar...")
                elif choice_num == 2:  # Máx. Resultados
                    try:
                        novo_max = int(input("Novo máximo de resultados (10-500): "))
                        self.config.max_results_display = max(10, min(500, novo_max))
                        self.interface.print_status(f"Máximo alterado para: {self.config.max_results_display}", "success")
                    except:
                        self.interface.print_status("Valor inválido!", "error")
                    input("Pressione ENTER para continuar...")
                elif choice_num == 3:  # Cache
                    self.config.enable_cache = not self.config.enable_cache
                    self.interface.print_status(f"Cache ativado: {'Sim' if self.config.enable_cache else 'Não'}", "success")
                    input("Pressione ENTER para continuar...")
                elif choice_num == 4:  # Histórico
                    self.config.enable_history = not self.config.enable_history
                    self.interface.print_status(f"Histórico ativado: {'Sim' if self.config.enable_history else 'Não'}", "success")
                    input("Pressione ENTER para continuar...")
                elif choice_num == 5:  # Busca Fuzzy
                    self.config.fuzzy_search = not self.config.fuzzy_search
                    self.interface.print_status(f"Busca Fuzzy ativada: {'Sim' if self.config.fuzzy_search else 'Não'}", "success")
                    input("Pressione ENTER para continuar...")
                elif choice_num == 6:  # Case Sensitive
                    self.config.case_sensitive = not self.config.case_sensitive
                    self.interface.print_status(f"Case Sensitive ativado: {'Sim' if self.config.case_sensitive else 'Não'}", "success")
                    input("Pressione ENTER para continuar...")
                elif choice_num == 7:  # Exportação Automática
                    self.config.auto_export = not self.config.auto_export
                    self.interface.print_status(f"Exportação Automática ativada: {'Sim' if self.config.auto_export else 'Não'}", "success")
                    input("Pressione ENTER para continuar...")
                elif choice_num == 8:  # Formato de Exportação
                    formatos = ["json", "csv", "excel", "txt"]
                    current = formatos.index(self.config.export_format) if self.config.export_format in formatos else 0
                    self.config.export_format = formatos[(current + 1) % len(formatos)]
                    self.interface.print_status(f"Formato alterado para: {self.config.export_format}", "success")
                    input("Pressione ENTER para continuar...")
                else:
                    self.interface.print_status("Opção inválida", "error")
                    input("Pressione ENTER para continuar...")
                    
            except ValueError:
                self.interface.print_status("Entrada inválida. Digite um número.", "error")
                input("Pressione ENTER para continuar...")


# ============================================================================
# CLASSE DA APLICAÇÃO PRINCIPAL
# ============================================================================

class GPWEBApplication:
    def __init__(self):
        self.system = GPWEBSearchSystem()
        self.interface = self.system.interface
        
    def run(self):
        while True:
            self.interface.print_banner()
            
            print(f"{self.interface.colors['bold']}{'═' * 70}{self.interface.colors['reset']}")
            print(f"{self.interface.colors['bold']}{'MENU PRINCIPAL':^70}{self.interface.colors['reset']}")
            print(f"{self.interface.colors['bold']}{'═' * 70}{self.interface.colors['reset']}")
            
            print(f"{self.interface.colors['cyan']}[1]{self.interface.colors['reset']} 🔍 Buscar Dados")
            print(f"{self.interface.colors['cyan']}[2]{self.interface.colors['reset']} 📊 Estatísticas")
            print(f"{self.interface.colors['cyan']}[3]{self.interface.colors['reset']} 📜 Histórico")
            print(f"{self.interface.colors['cyan']}[4]{self.interface.colors['reset']} ⚙️ Configurações")
            print(f"{self.interface.colors['cyan']}[5]{self.interface.colors['reset']} 📁 Carregar CSV")
            print(f"{self.interface.colors['cyan']}[6]{self.interface.colors['reset']} 💾 Exportar Dados")
            print(f"{self.interface.colors['cyan']}[7]{self.interface.colors['reset']} 🚪 Sair")
            
            choice = input(f"\n{self.interface.colors['green']}Escolha uma opção (1-7): {self.interface.colors['reset']}").strip()
            
            if choice == "7":
                self.interface.print_status("Encerrando sistema...", "info")
                if self.system.cache_db:
                    self.system.cache_db.close()
                sys.exit(0)
            elif choice == "1":
                self._perform_search()
            elif choice == "2":
                self.system.show_statistics()
                input("\nPressione ENTER para continuar...")
            elif choice == "3":
                self.system.show_search_history()
                input("\nPressione ENTER para continuar...")
            elif choice == "4":
                self.system.configure_system()
            elif choice == "5":
                filename = input("Nome do arquivo CSV (padrão: dados.csv): ").strip() or 'dados.csv'
                if self.system.load_csv(filename):
                    input("Pressione ENTER para continuar...")
            elif choice == "6":
                if self.system.dataframe is not None and not self.system.dataframe.empty:
                    self.system.export_results(self.system.dataframe, self.system.config.export_format)
                    input("Pressione ENTER para continuar...")
                else:
                    self.interface.print_status("Nenhum dado carregado", "error")
                    input("Pressione ENTER para continuar...")
            else:
                self.interface.print_status("Opção inválida", "error")
                input("Pressione ENTER para continuar...")
    
    def _perform_search(self):
        """Realiza busca apenas nos dados pessoais"""
        if self.system.dataframe is None or self.system.dataframe.empty:
            self.interface.print_status("Nenhum arquivo CSV carregado. Carregue primeiro.", "error")
            input("Pressione ENTER para continuar...")
            return
        
        while True:
            print(f"\n{self.interface.colors['bold']}{'═' * 70}{self.interface.colors['reset']}")
            print(f"{self.interface.colors['bold']}{'BUSCA EM DADOS PESSOAIS':^70}{self.interface.colors['reset']}")
            print(f"{self.interface.colors['bold']}{'═' * 70}{self.interface.colors['reset']}")
            
            print(f"\n{self.interface.colors['bold']}Colunas disponíveis para busca:{self.interface.colors['reset']}")
            
            # Mostra apenas as colunas de dados pessoais
            colunas_disponiveis = [col for col in COLUNAS_PESSOAIS if col in self.system.dataframe.columns]
            
            if not colunas_disponiveis:
                self.interface.print_status("Nenhuma das colunas esperadas foi encontrada no arquivo!", "warning")
                self.interface.print_status(f"Colunas esperadas: {', '.join(COLUNAS_PESSOAIS)}", "info")
                input("Pressione ENTER para voltar...")
                break
            
            for i, col in enumerate(colunas_disponiveis, 1):
                print(f"{self.interface.colors['cyan']}{i:3}.{self.interface.colors['reset']} {col}")
            
            print(f"\n{self.interface.colors['yellow']}0 - Voltar ao Menu Principal{self.interface.colors['reset']}")
            col_choice = input(f"\n{self.interface.colors['green']}Número da coluna para buscar: {self.interface.colors['reset']}").strip()
            
            if col_choice == "0":
                break
            
            try:
                col_idx = int(col_choice) - 1
                if 0 <= col_idx < len(colunas_disponiveis):
                    coluna_selecionada = colunas_disponiveis[col_idx]
                    
                    termo = input(f"{self.interface.colors['green']}Termo a buscar: {self.interface.colors['reset']}").strip()
                    
                    if not termo:
                        self.interface.print_status("Termo de busca vazio", "warning")
                        continue
                    
                    self.interface.print_status("Buscando...", "info")
                    resultados = self.system.search(coluna_selecionada, termo)
                    
                    if not resultados.empty:
                        duration = self.system.search_history[-1].duration if self.system.search_history else 0
                        print(f"\n{self.interface.colors['green']}🎯 Encontrados {len(resultados)} resultado(s) em {duration:.2f}s{self.interface.colors['reset']}")
                        
                        to_display = resultados.head(self.system.config.max_results_display)
                        
                        # Mostra APENAS os dados pessoais
                        for idx, row in to_display.iterrows():
                            print(f"\n{self.interface.colors['cyan']}{'═' * 70}{self.interface.colors['reset']}")
                            print(f"{self.interface.colors['yellow']}{' DADOS DO USUÁRIO ':=^70}{self.interface.colors['reset']}")
                            print(f"{self.interface.colors['cyan']}{'═' * 70}{self.interface.colors['reset']}")
                            
                            for col in COLUNAS_PESSOAIS:
                                if col in row.index:
                                    value = row[col]
                                    if pd.isna(value) or value == '' or value == 'nan':
                                        value = "NÃO INFORMADO"
                                    
                                    if col == coluna_selecionada and termo.lower() in str(value).lower():
                                        print(f"{self.interface.colors['yellow']}{col:<20}{self.interface.colors['reset']}: {self.interface.colors['green']}{value}{self.interface.colors['reset']}")
                                    else:
                                        print(f"{self.interface.colors['yellow']}{col:<20}{self.interface.colors['reset']}: {value}")
                            
                            print(f"{self.interface.colors['cyan']}{'═' * 70}{self.interface.colors['reset']}")
                        
                        if len(resultados) > self.system.config.max_results_display:
                            print(f"\n{self.interface.colors['gray']}... e mais {len(resultados) - self.system.config.max_results_display} resultados{self.interface.colors['reset']}")
                        
                        print(f"\n{self.interface.colors['cyan']}{'─' * 70}{self.interface.colors['reset']}")
                        print("Opções:")
                        print("1 - Nova busca")
                        print("2 - Exportar resultados")
                        print("3 - Voltar ao menu")
                        
                        action = input("Escolha: ").strip()
                        
                        if action == "2":
                            colunas_exportar = [col for col in COLUNAS_PESSOAIS if col in resultados.columns]
                            self.system.export_results(resultados[colunas_exportar], self.system.config.export_format)
                            input("Pressione ENTER para continuar...")
                        elif action == "3":
                            break
                    else:
                        self.interface.print_status("Nenhum resultado encontrado", "warning")
                        input("Pressione ENTER para continuar...")
                else:
                    self.interface.print_status("Número de coluna inválido", "error")
                    
            except ValueError:
                self.interface.print_status("Entrada inválida", "error")
            except Exception as e:
                logger.error(f"Erro durante busca: {e}")
                self.interface.print_status(f"Erro: {e}", "error")


# ============================================================================
# PONTO DE ENTRADA DO PROGRAMA
# ============================================================================

if __name__ == "__main__":
    try:
        app = GPWEBApplication()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{GPWEBInterface().colors['yellow']}⚠️ Interrompido pelo usuário{GPWEBInterface().colors['reset']}")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Erro fatal: {e}")
        print(f"\n{GPWEBInterface().colors['red']}❌ Erro fatal: {e}{GPWEBInterface().colors['reset']}")
        sys.exit(1)