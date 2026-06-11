#!/usr/bin/env python3
"""
WhatIf AI - Day 2: Chronos Static Analysis Engine
Parses Python source files using the native 'ast' module to extract explicit import dependencies 
and build a static dependency matrix. Falls back to an interactive simulated AST compile if 
no Python files are present.
"""

import ast
import os
import json
import sys
import argparse

class StaticDependencyVisitor(ast.NodeVisitor):
    """
    AST Visitor to identify and record internal module dependencies.
    """
    def __init__(self, filename, local_modules):
        self.filename = filename
        self.local_modules = local_modules
        self.dependencies = set()

    def visit_Import(self, node):
        for alias in node.names:
            # Split to handle sub-module imports e.g., 'import pkg.module'
            base_module = alias.name.split('.')[0]
            if base_module in self.local_modules:
                self.dependencies.add(self.local_modules[base_module])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            base_module = node.module.split('.')[0]
            if base_module in self.local_modules:
                self.dependencies.add(self.local_modules[base_module])
        # Note: Relative imports (level > 0) without a module name (e.g. 'from . import x')
        # are handled here if node.module is None, but typically resolve to local package files.
        self.generic_visit(node)


def build_dependency_matrix(files_dict):
    """
    Given a dict of {filename: file_contents_str}, parses ASTs and builds dependency matrix.
    """
    # Create module lookup mapping (e.g., 'auth' -> 'auth.py')
    local_modules = {}
    for filename in files_dict.keys():
        module_name = os.path.splitext(filename)[0]
        local_modules[module_name] = filename

    matrix = {}

    for filename, content in files_dict.items():
        matrix[filename] = []
        try:
            tree = ast.parse(content, filename=filename)
            visitor = StaticDependencyVisitor(filename, local_modules)
            visitor.visit(tree)
            
            # Remove self-references if any
            visitor.dependencies.discard(filename)
            matrix[filename] = sorted(list(visitor.dependencies))
        except SyntaxError as e:
            print(f"[-] Syntax error while parsing {filename}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[-] Failed parsing {filename}: {e}", file=sys.stderr)

    return matrix


def run_real_scan(target_dir):
    """
    Scans the actual filesystem target directory for python files and builds dependencies.
    """
    print(f"[*] Scanning workspace directory: {target_dir}")
    if not os.path.isdir(target_dir):
        print(f"[-] Error: Directory '{target_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    files_dict = {}
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, target_dir)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        files_dict[rel_path] = f.read()
                except Exception as e:
                    print(f"[-] Skipping file {rel_path} due to read error: {e}", file=sys.stderr)

    if not files_dict:
        print("[!] No Python files found in target directory. Switching to simulation mode...")
        return None

    return build_dependency_matrix(files_dict)


def run_simulation():
    """
    Simulates AST compilation on in-memory mock codebase to demonstrate parsing.
    """
    print("[*] Running in AST Simulation Fallback Mode...")
    
    # In-memory mock codebase for a web service
    mock_codebase = {
        "main.py": """
import auth
import database
from billing import process_payment
import sys
import os

def run_app():
    print("Application booting...")
    db = database.connect()
    auth.verify_session()
""",
        "auth.py": """
import database
import jwt
from utils import logger

def login(user, pwd):
    database.query("SELECT * FROM users")
    return jwt.sign_token(user)
""",
        "billing.py": """
import database
import redis_cache
import utils

def process_payment(amount):
    redis_cache.lock_transaction()
    database.query("UPDATE balance SET ...")
""",
        "jwt.py": """
import time
import hmac

def sign_token(data):
    return hmac.new(b"secret", data.encode(), digestmod="sha256").hexdigest()
""",
        "database.py": """
import os

def connect():
    return f"connected_to_{os.getenv('DB_HOST')}"

def query(sql):
    pass
""",
        "redis_cache.py": """
import socket

def lock_transaction():
    pass
""",
        "utils.py": """
import logging

def logger(msg):
    logging.info(msg)
"""
    }

    print("[*] Compiling mock source code trees into AST structures...")
    return build_dependency_matrix(mock_codebase)


def main():
    parser = argparse.ArgumentParser(description="WhatIf AI - Static AST Dependency Engine")
    parser.add_argument("target_dir", nargs="?", default=None, 
                        help="Target directory containing Python files to scan")
    parser.add_argument("--simulate", action="store_true", 
                        help="Force simulation fallback mode using in-memory mock source trees")
    parser.add_argument("--output", default="ast_static_matrix.json",
                        help="Filename for the output dependency matrix JSON (default: ast_static_matrix.json)")

    args = parser.parse_args()

    # Determine execution path
    if args.simulate or not args.target_dir:
        matrix = run_simulation()
    else:
        matrix = run_real_scan(args.target_dir)
        if matrix is None:
            matrix = run_simulation()

    # Save Matrix
    try:
        output_path = os.path.abspath(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(matrix, f, indent=2)
        print(f"[+] Success: Static dependency matrix written to: {output_path}")
        print("\nParsed Dependencies Mapping:")
        for file, deps in matrix.items():
            print(f"  {file} -> {deps}")
    except Exception as e:
        print(f"[-] Failed to write matrix output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
