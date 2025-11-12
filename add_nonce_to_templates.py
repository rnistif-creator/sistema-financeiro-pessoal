#!/usr/bin/env python3
"""
Script para adicionar atributo nonce aos scripts inline em templates HTML.
Atualiza todos os templates no diretório app/templates.
"""

import re
from pathlib import Path

def add_nonce_to_script_tags(content: str) -> str:
    """
    Adiciona atributo nonce a todas as tags <script> inline que não o possuem.
    Ignora tags <script> com src (scripts externos).
    """
    # Padrão para encontrar tags <script> sem src e sem nonce
    # Procura por <script> (possivelmente com outros atributos) mas sem 'src=' e sem 'nonce='
    pattern = r'<script(?!\s+[^>]*src=)(?!\s+[^>]*nonce=)([^>]*)>'
    
    def replacer(match):
        attrs = match.group(1)
        # Adiciona nonce condicional do Jinja2
        if attrs and not attrs.endswith(' '):
            attrs += ' '
        return f'<script{attrs}{{%- if csp_nonce %}} nonce="{{{{ csp_nonce }}}}"{{%- endif %}}'
    
    # Substituir todas as ocorrências
    updated = re.sub(pattern, replacer, content)
    return updated

def process_template_file(filepath: Path) -> bool:
    """
    Processa um arquivo de template adicionando nonce aos scripts inline.
    Retorna True se o arquivo foi modificado.
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Adicionar nonce aos scripts
        updated_content = add_nonce_to_script_tags(content)
        
        if updated_content != original_content:
            filepath.write_text(updated_content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"❌ Erro ao processar {filepath}: {e}")
        return False

def main():
    templates_dir = Path(__file__).parent / "app" / "templates"
    
    if not templates_dir.exists():
        print(f"❌ Diretório não encontrado: {templates_dir}")
        return
    
    print(f"🔍 Procurando templates em: {templates_dir}")
    
    html_files = list(templates_dir.glob("*.html"))
    modified_count = 0
    
    for html_file in html_files:
        print(f"📄 Processando: {html_file.name}...", end=" ")
        if process_template_file(html_file):
            print("✅ Modificado")
            modified_count += 1
        else:
            print("⏭️  Sem alterações")
    
    print(f"\n✨ Concluído! {modified_count}/{len(html_files)} arquivos modificados.")

if __name__ == "__main__":
    main()
