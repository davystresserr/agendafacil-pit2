"""Exporta para PNG os diagramas Mermaid dos .md e os wireframes HTML.

Uso: python scripts/exportar_diagramas.py
Requer: playwright + chromium (playwright install chromium) e acesso à internet
para carregar o mermaid.js do CDN (só o script é baixado; nenhum conteúdo é enviado).
"""
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
S1 = RAIZ / "docs" / "situacao-1"
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"

FONTES = [
    S1 / "uml" / "casos-de-uso.md",
    S1 / "uml" / "classes.md",
    S1 / "uml" / "sequencia-agendar.md",
    S1 / "uml" / "atividades-cancelamento.md",
    S1 / "modelo-dados" / "01-modelo-conceitual.md",
    S1 / "ihc.md",
]

PAGINA = """<!doctype html><html><head><meta charset="utf-8">
<script src="{cdn}"></script>
<style>body{{margin:0;padding:24px;background:#fff;font-family:system-ui}}</style>
</head><body><pre class="mermaid">{codigo}</pre>
<script>mermaid.initialize({{startOnLoad:false, theme:'default'}});
mermaid.run().then(()=>document.body.dataset.ok='1');</script></body></html>"""


def blocos_mermaid(md: Path):
    return re.findall(r"```mermaid\n(.*?)```", md.read_text(encoding="utf-8"), flags=re.S)


def main():
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pagina = nav.new_page(viewport={"width": 1400, "height": 900}, device_scale_factor=2)
        for md in FONTES:
            for i, codigo in enumerate(blocos_mermaid(md), start=1):
                sufixo = "" if i == 1 else f"-{i}"
                nome = "ihc-mapa-telas" if md.stem == "ihc" else md.stem
                destino = md.with_name(nome + sufixo + ".png")
                html = PAGINA.format(cdn=MERMAID_CDN, codigo=codigo.replace("<", "&lt;").replace(">", "&gt;"))
                pagina.set_content(html)
                pagina.wait_for_selector("body[data-ok='1']", timeout=30000)
                pagina.locator("pre.mermaid svg").screenshot(path=str(destino))
                print("PNG:", destino.relative_to(RAIZ))

        wf_dir = S1 / "wireframes"
        (wf_dir / "png").mkdir(exist_ok=True)
        pagina.set_viewport_size({"width": 1000, "height": 700})
        for html in sorted(wf_dir.glob("0*.html")):
            pagina.goto(html.as_uri())
            destino = wf_dir / "png" / (html.stem + ".png")
            pagina.screenshot(path=str(destino), full_page=True)
            print("PNG:", destino.relative_to(RAIZ))
        nav.close()


if __name__ == "__main__":
    main()
