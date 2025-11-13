from pathlib import Path
from PIL import Image, ImageOps

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "app" / "static"
BRAND_DIR = STATIC_DIR / "brand"
ICONS_DIR = STATIC_DIR / "icons"
SIZES = [16, 32, 48, 72, 96, 128, 144, 152, 180, 192, 256, 384, 512]


def get_source_image() -> Path:
    png = BRAND_DIR / "logo.png"
    if png.exists():
        return png
    # Poderíamos suportar SVG via cairosvg, mas evitamos dependência extra.
    # Se precisar de SVG, converter manualmente para PNG.
    raise SystemExit(
        f"Arquivo de origem não encontrado: {png}. Coloque o logo oficial em {png}"
    )


def ensure_square_variant(src: Path, size: int) -> Path:
    out_path = ICONS_DIR / f"domo360-{size}x{size}.png"
    img = Image.open(src).convert("RGBA")
    resized = ImageOps.contain(img, (size, size), method=Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - resized.width) // 2
    y = (size - resized.height) // 2
    canvas.paste(resized, (x, y), resized)
    canvas.save(out_path, format="PNG", optimize=True)
    return out_path


def main():
    src = get_source_image()
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    created = []
    for s in SIZES:
        out = ensure_square_variant(src, s)
        created.append(out.name)
    # Compat: também gerar um domo360-logo.png 192x192
    logo192 = ICONS_DIR / "domo360-logo.png"
    if not logo192.exists():
        (ICONS_DIR / "domo360-192x192.png").replace(logo192)
        created.append(logo192.name)
    print("Gerados:", ", ".join(created))


if __name__ == "__main__":
    main()
