"""
Script para gerar ícones do PWA
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Criar diretório de ícones
icons_dir = "app/static/icons"
os.makedirs(icons_dir, exist_ok=True)

# Tamanhos dos ícones
sizes = [16, 32, 48, 72, 96, 128, 144, 152, 192, 384, 512]

# Criar ícone base
def create_icon(size):
    # Criar imagem com fundo gradiente
    img = Image.new('RGB', (size, size), color='#0f172a')
    draw = ImageDraw.Draw(img)
    
    # Desenhar círculo com cor primária
    margin = size // 8
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill='#22d3ee',
        outline='#06b6d4',
        width=max(2, size // 50)
    )
    
    # Adicionar símbolo de dinheiro
    try:
        # Tentar usar fonte do sistema
        font_size = size // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback para fonte padrão
        font = ImageFont.load_default()
    
    # Desenhar $ no centro
    text = "$"
    # Calcular posição central
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - size // 20
    
    draw.text((x, y), text, fill='#0f172a', font=font)
    
    return img

# Gerar todos os ícones
print("Gerando ícones do PWA...")
for size in sizes:
    icon = create_icon(size)
    filename = f"icon-{size}x{size}.png"
    filepath = os.path.join(icons_dir, filename)
    icon.save(filepath, 'PNG')
    print(f"✓ Criado: {filename}")

print("Gerando favicon.ico (múltiplos tamanhos 16/32/48)...")
ico_path = os.path.join("app/static", "favicon.ico")
# Criar um ICO com múltiplos tamanhos
ico_imgs = [create_icon(sz) for sz in [16, 32, 48]]
ico_imgs[0].save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
print(f"✓ Criado: favicon.ico")

print(f"\n✅ {len(sizes)} ícones + favicon criados com sucesso em {icons_dir}/")
