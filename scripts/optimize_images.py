#!/usr/bin/env python3
from PIL import Image
from pathlib import Path

images_dir = Path(__file__).resolve().parents[1] / 'images'
images = {
    'fireside-logo.png': {'web': ('fireside-logo-web.png', {'width': 360}), 'header': ('fireside-logo-header.png', {'height': 44}), 'favicon': ('favicon.png', {'size': (32, 32)})},
    'ccpia-logo.png': {'web': ('ccpia-badge.png', {'height': 72})},
    'nachi-logo.png': {'web': ('nachi-badge.png', {'height': 72})},
    '91-low-resolution-for-web-png-1546033375.png': {'web': ('derek-badge.png', {'height': 72})},
    '97-low-resolution-for-web-png-1546035861.png': {'web': ('josiah-badge.png', {'height': 72})}
}

# For images not listed in the images map, create a web-optimized PNG and a webp variant.
def optimize_misc_images(images_dir):
    for p in images_dir.iterdir():
        if p.is_file() and p.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            if p.name in images:
                continue
            # skip already optimized files or logo/header/thumbs
            if p.stem.endswith('-web') or p.stem.endswith('-header') or p.stem == 'favicon':
                continue
            web_name = p.stem + '-web' + p.suffix
            webp_name = p.stem + '-web.webp'
            dst_web = images_dir / web_name
            print(f"Optimizing misc image {p.name} -> {web_name}")
            resize_image(p, dst_web, width=1200, height=None)
            # create webp
            try:
                webp_dst = dst_web.with_suffix('.webp')
                img = Image.open(dst_web)
                img.save(webp_dst, 'WEBP', quality=80, method=6)
            except Exception as e:
                print('Failed to create webp for misc', e)


def resize_image(src_path, dst_path, width=None, height=None, size=None):
    img = Image.open(src_path)
    orig_mode = img.mode
    if size:
        img = img.copy()
        img.thumbnail(size, Image.LANCZOS)
    else:
        w, h = img.size
        if width and not height:
            new_w = width
            new_h = int(h * (width / w))
        elif height and not width:
            new_h = height
            new_w = int(w * (height / h))
        else:
            new_w, new_h = (width or w, height or h)
        img = img.resize((new_w, new_h), Image.LANCZOS)

    # Save optimized PNG
    dst_path_parent = dst_path.parent
    dst_path_parent.mkdir(parents=True, exist_ok=True)
    if img.mode in ("RGBA", "LA"):
        img = img.convert('RGBA')
        img.save(dst_path, optimize=True)
    else:
        img = img.convert('RGB')
        img.save(dst_path, optimize=True, quality=85)

    # Also save WebP variants for modern browsers
    try:
        webp_dst = dst_path.with_suffix('.webp')
        img.save(webp_dst, 'WEBP', quality=80, method=6)
    except Exception as e:
        print(f"Warning: Failed to create webp for {dst_path.name}: {e}")


if __name__ == '__main__':
    for src_name, variants in images.items():
        src_path = images_dir / src_name
        if not src_path.exists():
            print(f"Skipping missing: {src_path}")
            continue
        for variant_name, (dst_name, opts) in variants.items():
            dst_path = images_dir / dst_name
            size = None
            width = opts.get('width')
            height = opts.get('height')
            if 'size' in opts:
                size = opts['size']
            print(f"Resizing {src_path.name} -> {dst_name} (w:{width} h:{height} size:{size})")
            resize_image(src_path, dst_path, width=width, height=height, size=size)
    # Optimize other image files as well
    optimize_misc_images(images_dir)
    # Create favicon.ico from favicon.png variants
    try:
        favicon_png = images_dir / 'favicon.png'
        if favicon_png.exists():
            ico_path = images_dir.parent / 'favicon.ico'
            # create multiple sizes for ICO
            img = Image.open(favicon_png)
            sizes = [(16, 16), (32, 32), (48, 48)]
            icons = [img.copy().resize(s, Image.LANCZOS) for s in sizes]
            icons[0].save(ico_path, format='ICO', sizes=sizes)
            print('Created favicon.ico')
    except Exception as e:
        print('Failed to create favicon:', e)
