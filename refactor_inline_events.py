#!/usr/bin/env python3
"""Refatora handlers inline (onclick=, onchange= etc) para atributos data-*, permitindo CSP sem inline JS.
Substitui:
  onclick="acao()" -> data-onclick="acao()"
Mantém o restante do HTML.
"""
import os, re, sys
EVENT_ATTRS = ["onclick","onchange","oninput","onsubmit","onload","onmouseover","onmouseout"]
PATTERN = re.compile(r'\s(' + '|'.join(EVENT_ATTRS) + r')="([^"]*)"', re.IGNORECASE)
TEMPLATES_DIR = 'app/templates'

def transform(content: str) -> str:
    return PATTERN.sub(lambda m: f' data-{m.group(1).lower()}="{m.group(2)}"', content)

def process_file(path: str):
    orig = open(path,'r',encoding='utf-8').read()
    new = transform(orig)
    if new != orig:
        open(path,'w',encoding='utf-8').write(new)
        return True
    return False

def main():
    changed = 0
    for name in os.listdir(TEMPLATES_DIR):
        if not name.endswith('.html'): continue
        p = os.path.join(TEMPLATES_DIR,name)
        if process_file(p):
            print(f'✅ {name} modificado')
            changed +=1
        else:
            print(f'⏭️  {name} sem alterações')
    print(f'\nTotal alterados: {changed}')
    if changed:
        print('Lembre-se de incluir o script de delegação se ainda não estiver nos templates.')

if __name__ == '__main__':
    main()
