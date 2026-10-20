"""Genera la versión en inglés (/en/) a partir de las páginas en español y
añade el selector de idioma y las etiquetas hreflang en ambas versiones.
Uso (desde la raíz del repositorio): python3 -I herramientas/generar_en.py herramientas/traducciones_en.py
Antes, añade a traducciones_en.py la traducción de cualquier texto nuevo: el script
lista al final los que falten."""
import html
import os
import re
import sys
import urllib.parse

ns = {}
exec(open(sys.argv[1], encoding="utf-8").read(), ns)
T, KEEP = ns["T"], ns["KEEP"]
SITE = "https://proyectocaetano.com"
PAGES = {"/": "/en/", "/perfil/": "/en/profile/", "/planes/": "/en/plans/", "/clubes/": "/en/clubs/"}
MAIL = "proyectocaetanohorta@gmail.com"


def norm(t):
    return " ".join(html.unescape(t).split())


missing = []


def tr_text(m):
    raw = m.group(1)
    t = norm(raw)
    if not t or t in KEEP:
        return m.group(0)
    if t in T:
        lead = raw[: len(raw) - len(raw.lstrip())]
        trail = raw[len(raw.rstrip()):]
        return ">" + lead + html.escape(T[t], quote=False) + trail + "<"
    missing.append(t)
    return m.group(0)


def tr_attr(m):
    name, val = m.group(1), m.group(2)
    t = norm(val)
    if t in T:
        return f'{name}="{html.escape(T[t])}"'
    if t and t not in KEEP:
        missing.append(f"[{name}] {t}")
    return m.group(0)


def mailto_en(plan):
    body = f"Hi Caetano,\n\nI'm interested in the {plan}.\n\nName:\nAge:\nClub and country:\nCurrent level:\nMain goal:\nWhen would I like to start?:\n"
    return f"mailto:{MAIL}?" + urllib.parse.urlencode({"subject": f"Getting started: {plan}", "body": body}, quote_via=urllib.parse.quote)


def switcher(html_text, es_path, lang):
    en_path = PAGES[es_path]
    other_href, other_label, other_name = (en_path, "EN", "English") if lang == "es" else (es_path, "ES", "Español")
    alt = (f'<link rel="alternate" hreflang="es" href="{SITE}{es_path}">\n'
           f'<link rel="alternate" hreflang="en" href="{SITE}{en_path}">\n'
           f'<link rel="alternate" hreflang="x-default" href="{SITE}{es_path}">\n')
    html_text = re.sub(r'<link rel="alternate" hreflang[^>]*>\n', "", html_text)
    html_text = html_text.replace('<link rel="icon"', alt + '<link rel="icon"', 1)
    html_text = re.sub(r'\n    <li class="lang-li">.*?</li>', "", html_text)
    html_text = re.sub(r'\n  <a class="lang-link"[^\n]*', "", html_text)
    link = f'<a class="lang-link" href="{other_href}" hreflang="{other_label.lower()}" lang="{other_label.lower()}" aria-label="{other_name}">{other_label}</a>'
    html_text = html_text.replace("\n  </ul>\n  <button class=\"hamburger\"", f'\n    <li class="lang-li">{link}</li>\n  </ul>\n  <button class="hamburger"', 1)
    html_text = html_text.replace('\n</div>\n\n<nav id="navbar">', f'\n  {link}\n</div>\n\n<nav id="navbar">', 1)
    assert html_text.count("lang-link") == 2, es_path
    return html_text


for es_path, en_path in PAGES.items():
    src_file = (es_path.strip("/") or ".") + "/index.html"
    es = open(src_file, encoding="utf-8").read()
    es = switcher(es, es_path, "es")
    open(src_file, "w", encoding="utf-8").write(es)

    en = es
    en = en.replace('<html lang="es">', '<html lang="en">').replace('content="es_ES"', 'content="en_GB"')
    en = en.replace(f'href="{SITE}{es_path}"', f'href="{SITE}{en_path}"').replace(f'content="{SITE}{es_path}"', f'content="{SITE}{en_path}"')
    # hreflang se recalcula después; ahora traducir textos y atributos.
    head, body = en.split("<body>", 1)
    head = re.sub(r"<title>(.*?)</title>", lambda m: "<title>" + html.escape(T.get(norm(m.group(1)), m.group(1)), quote=False) + "</title>", head)
    head = re.sub(r'(content)="([^"]*)"', lambda m: tr_attr(m) if norm(m.group(2)) in T else m.group(0), head)
    body = re.sub(r">([^<>]+)<", tr_text, body)
    body = re.sub(r'(alt|placeholder|aria-label)="([^"]+)"', tr_attr, body)
    en = head + "<body>" + body
    # Enlaces internos a la versión inglesa (las páginas legales siguen en español).
    for es_p, en_p in PAGES.items():
        en = en.replace(f'href="{es_p}"', f'href="{en_p}"').replace(f'href="{es_p}#', f'href="{en_p}#')
    en = re.sub(r'<a class="lang-link" href="/en/[^"]*" hreflang="en" lang="en" aria-label="English">EN</a>',
                f'<a class="lang-link" href="{es_path}" hreflang="es" lang="es" aria-label="Español">ES</a>', en)
    en = re.sub(r'<link rel="alternate" hreflang="es" href="[^"]*">', f'<link rel="alternate" hreflang="es" href="{SITE}{es_path}">', en)
    en = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*">', f'<link rel="alternate" hreflang="x-default" href="{SITE}{es_path}">', en)
    en = re.sub(r'<link rel="alternate" hreflang="en" href="[^"]*">', f'<link rel="alternate" hreflang="en" href="{SITE}{en_path}">', en)
    # Correos de «Empezar» en inglés.
    for es_plan, en_plan in [("Asesoría técnica", "Technique Coaching plan"), ("Plan de entrenamiento", "Training Plan"), ("Plan Premium", "Premium Plan")]:
        en = re.sub(r'mailto:[^"]*' + re.escape(urllib.parse.quote(f"Quiero empezar: {es_plan}")) + r'[^"]*', mailto_en(en_plan), en)
    assert "Quiero%20empezar" not in en
    en = re.sub(r'(THE ROOTS OF THE <span[^>]*>)PROYECTO(</span>)', r'\1PROJECT\2', en)
    out = en_path.strip("/") + "/index.html"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(en)

print("SIN TRADUCIR:", sorted(set(missing)) if missing else "nada")
