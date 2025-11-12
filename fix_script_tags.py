#!/usr/bin/env python3
"""
Script para corrigir tags <script> sem fechamento '>' nos templates
"""
import os
import re

TEMPLATES_DIR = "app/templates"

def fix_script_tags(filepath):
    """Corrige tags <script> que estão sem o > de fechamento"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Padrão: <script{%- if csp_nonce %} nonce="{{ csp_nonce }}"{%- endif %} seguido de whitespace e NÃO seguido de >
    # Substituir por: <script{%- if csp_nonce %} nonce="{{ csp_nonce }}"{%- endif %}>
    pattern = r'(<script\{%- if csp_nonce %\} nonce="{{ csp_nonce }}"\{%- endif %\})(\s+(?!>))'
    replacement = r'\1>\2'
    
    content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Processa todos os templates HTML"""
    if not os.path.exists(TEMPLATES_DIR):
        print(f"❌ Diretório {TEMPLATES_DIR} não encontrado")
        return
    
    fixed_count = 0
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith('.html'):
            filepath = os.path.join(TEMPLATES_DIR, filename)
            if fix_script_tags(filepath):
                print(f"✅ {filename} - corrigido")
                fixed_count += 1
            else:
                print(f"⏭️  {filename} - nenhuma alteração necessária")
    
    print(f"\n📊 Total: {fixed_count} arquivo(s) corrigido(s)")

if __name__ == "__main__":
    main()
