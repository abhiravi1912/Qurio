import os
import urllib.request

vendor_dir = r"e:\qurio\static\vendor"
css_dir = os.path.join(vendor_dir, "css")
js_dir = os.path.join(vendor_dir, "js")
fonts_dir = os.path.join(vendor_dir, "fonts")

os.makedirs(css_dir, exist_ok=True)
os.makedirs(js_dir, exist_ok=True)
os.makedirs(fonts_dir, exist_ok=True)

files_to_download = [
    # Bootstrap
    ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css", os.path.join(css_dir, "bootstrap.min.css")),
    ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js", os.path.join(js_dir, "bootstrap.bundle.min.js")),
    # Bootstrap Icons
    ("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css", os.path.join(css_dir, "bootstrap-icons.css")),
    ("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff2", os.path.join(fonts_dir, "bootstrap-icons.woff2")),
    ("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff", os.path.join(fonts_dir, "bootstrap-icons.woff")),
    # Inter Font (Variable woff2 from a static source)
    ("https://github.com/rsms/inter/releases/download/v4.0/Inter-VariableFont_slnt,wght.ttf", os.path.join(fonts_dir, "Inter-Variable.ttf")),
]

for url, dest in files_to_download:
    print(f"Downloading {url} to {dest}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# Fix paths in bootstrap-icons.css
icons_css_path = os.path.join(css_dir, "bootstrap-icons.css")
if os.path.exists(icons_css_path):
    with open(icons_css_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("url(\"./fonts/", "url(\"../fonts/")
    with open(icons_css_path, "w", encoding="utf-8") as f:
        f.write(content)

# Create an local inter.css
inter_css_path = os.path.join(css_dir, "inter.css")
with open(inter_css_path, "w", encoding="utf-8") as f:
    f.write('''@font-face {
  font-family: 'Inter';
  src: url('../fonts/Inter-Variable.ttf') format('truetype');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
''')

print("All downloads complete.")
