#!/usr/bin/env python3
from PIL import Image
from pathlib import Path

images_dir = Path(__file__).resolve().parents[1] / 'images'
images = {
    'fireside-logo-hires.png': {
        'web': ('fireside-logo-hires-web.png', {'width': 1200}),
        'header': ('fireside-logo-header.png', {'height': 96}),
        'header2x': ('fireside-logo-header@2x.png', {'height': 192}),
        'favicon': ('favicon.png', {'size': (32, 32)})
    },
    'ccpia-badge.png': {'web': ('ccpia-badge-web.png', {'height': 1200}), 'web2x': ('ccpia-badge@2x.png', {'height': 2400})},
    'nachi-badge.png': {'web': ('nachi-badge-web.png', {'height': 1200}), 'web2x': ('nachi-badge@2x.png', {'height': 2400})},
    'cpi-badge.png': {'web': ('cpi-badge-web.png', {'height': 1200}), 'web2x': ('cpi-badge@2x.png', {'height': 2400})},
    'sewer-badge.png': {'web': ('sewer-badge-web.png', {'height': 1200}), 'web2x': ('sewer-badge@2x.png', {'height': 2400})}
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


def create_2x_variants(images_dir, targets):
    """Create @2x PNG/WebP variants for existing image files named in targets.
    If the file exists, create <name>@2x.png and <name>@2x.webp scaled to double height.
    """
    for name in targets:
        src = images_dir / name
        if not src.exists():
            print(f"Skipping for 2x: missing source {name}")
            continue
        try:
            img = Image.open(src)
            w, h = img.size
            # target 2x scale is height * 2
            new_h = int(h * 2)
            new_w = int(w * 2)
            img2x = img.copy().resize((new_w, new_h), Image.LANCZOS)
            dst2x = src.with_name(src.stem + '@2x' + src.suffix)
            img2x.save(dst2x, optimize=True, quality=85)
            # also save webp
            webp_dst = dst2x.with_suffix('.webp')
            img2x.save(webp_dst, 'WEBP', quality=85, method=6)
            print(f"Created 2x variant for {name} -> {dst2x.name}")
        except Exception as e:
            print(f"Failed creating 2x for {name}: {e}")


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
    # Create @2x variants for logo and badges if we only have low-res images
    create_2x_variants(images_dir, [
        'fireside-logo-hires-web.png',
        'ccpia-badge.png',
        'nachi-badge.png',
        'cpi-badge.png',
        'sewer-badge.png',
        'favicon.png'
    ])
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
