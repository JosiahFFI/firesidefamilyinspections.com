# Fireside Family Inspections — Static Site

This repository contains a simple static website optimized for hosting at https://firesidefamilyinspections.com.

Hosting checklist

- DNS: point your domain `firesidefamilyinspections.com` (and optionally `www`) to your hosting service via A or CNAME records.
- SSL: enable HTTPS (Let's Encrypt, Cloudflare, or hosting provider-managed certs).
- Deploy static files to your hosting provider (GitHub Pages, Netlify, Vercel, S3+CloudFront, or Apache/nginx server).
- Set the site root to serve `index.html`.
- Verify `robots.txt` and `sitemap.xml` are served from the root.

Quick local preview

```sh
# Serve the folder at port 8000
python3 -m http.server 8000
# Open http://localhost:8000
```

Helpful notes

- The site uses `OG` and `Twitter Card` meta tags; make sure `og:image` and `twitter:image` URLs point to the final production domain.
- JSON-LD Business Schema is defined in `index.html` and includes the company address, telephone, and email.
- There is no contact form — contact is via `tel:` and `mailto:` links.

If you want deployment help or to add a build step (minification / asset hashing), let me know and I can add a `package.json` with a build pipeline.
