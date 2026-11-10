"""Preenche o formulário da atividade (PIT_atividade_8.docx) sem alterar sua estrutura.

Uso: python scripts/preencher_formulario.py [--repo URL] [--app URL] [--video URL]
Links não informados ficam como [PENDENTE]. Os 5 testes dos colegas ficam [PENDENTE]
até serem preenchidos com resultados reais.
"""
import argparse
import copy
from pathlib import Path

import docx

RAIZ = Path(__file__).resolve().parents[1]
MODELO = RAIZ / "entrega" / "modelo" / "PIT_atividade_8.docx"
SAIDA = RAIZ / "entrega" / "PIT_atividade_8_preenchido.docx"


def run_como(paragrafo, texto, modelo_run=None, negrito=False):
    """Acrescenta um run copiando a formatação (fonte Arial) de um run de referência."""
    r = paragrafo.add_run(texto)
    if modelo_run is not None and modelo_run._r.rPr is not None:
        r._r.insert(0, copy.deepcopy(modelo_run._r.rPr))
    r.bold = negrito
    r.italic = False
    return r


def escrever_celula(linha, texto, col=1):
    """Escreve na célula de resposta usando a fonte do rótulo da mesma linha, sem o negrito."""
    celula = linha.cells[col]
    ref = next((r for p_ in linha.cells[0].paragraphs for r in p_.runs if r.text.strip()), None)
    p = celula.paragraphs[0]
    for r in p.runs:
        r.text = ""
    run_como(p, texto, ref, negrito=False)


def acrescentar_na_celula(celula, texto):
    """Mantém o rótulo da célula e escreve a resposta logo depois dele."""
    p = celula.paragraphs[-1]
    ref = p.runs[0] if p.runs else None
    run_como(p, " " + texto, ref, negrito=False)


COLEGAS = [
    ("Andrew", "28/10/2026",
     "Parte A completa (A1 a A15) no celular Android + Chrome: cadastro, login, agendamento, cancelamento e "
     "telas de erro.",
     "O cadastro aceitava telefone só com símbolos, como \"((((((((\". Corrigir para aceitar só números e formatar "
     "no padrão (xx) xxxxx-xxxx. Corrigido (C-01).",
     "Parte B (profissional e administrador): testou apenas como cliente."),
    ("Theo Nicoleli", "29/10/2026",
     "A1 a A8, A12, A14 e A15 no iPhone: cadastro, login, agendamento, horário ocupado e celular.",
     "Nada. Sugeriu agendar só com o telefone, sem tantos dados: aplicado como agendamento sem cadastro.",
     "A9, A10, A11, A13 e a Parte B: quis testar só como cliente."),
    ("Davi Inoue", "31/10/2026",
     "Partes A e B completas (A1 a A15 e B1 a B4) no notebook Windows + Chrome.",
     "Nada. Sugeriu aviso por WhatsApp ou e-mail e integração com o Google Agenda: Google Agenda aplicado.",
     "Nenhuma."),
    ("Arthur Furtado", "31/10/2026",
     "A1 a A12, A14 e A15 no iPhone + Safari.",
     "A13 marcado como falha (\"consegui acessar com o admin\"): era a tela de login, não defeito (C-02); o texto "
     "do passo foi corrigido. Sugeriu cores diferentes para horários livres e ocupados: aplicado.",
     "Parte B: não recebeu acesso."),
    ("Cris", "10/11/2026",
     "Parte A completa (A1 a A15) no Chrome.",
     "Nada.",
     "Parte B (profissional e administrador): marcada como não testada."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="[PENDENTE]")
    ap.add_argument("--app", default="[PENDENTE]")
    ap.add_argument("--video", default="[PENDENTE]")
    a = ap.parse_args()

    d = docx.Document(MODELO)
    ps = d.paragraphs

    # Identificação (regiões editáveis "Digite aqui")
    for p, valor in ((ps[3], "Davy Gabriel Stresser Pereira"), (ps[4], "36963089")):
        alvo = next(r for r in p.runs if r.text == "Digite aqui")
        alvo.text = valor

    # Documentação: link do repositório
    p_link = next(p for p in ps if p.text.startswith("Link do repositório"))
    run_como(p_link, a.repo, p_link.runs[-1])
    p_obs = ps[ps.index(p_link) + 1]
    run_como(p_obs, "Documentação em docs/situacao-1 (escopo, UML, IHC, modelo de dados e dicionário), "
                    "docs/situacao-2 e docs/situacao-3.", p_link.runs[-1])

    # Codificação
    t = d.tables[0]
    respostas = ["Python (Flask)", "PostgreSQL", "Vercel, com banco no Neon (domínio via Cloudflare)", "Web"]
    for i, texto in enumerate(respostas):
        escrever_celula(t.rows[i], texto)
    modo = t.rows[4].cells[1]
    for p in modo.paragraphs:
        for r in p.runs:
            if "Tradicional" in p.text and "( )" in r.text:
                r.text = r.text.replace("( )", "(X)")
    assert "(X) Tradicional" in modo.text and modo.text.count("(X)") == 1, modo.text
    escrever_celula(t.rows[5], a.repo)
    escrever_celula(t.rows[6], a.app)
    escrever_celula(t.rows[7], a.video)

    # Testes da solução: 5 tabelas de colegas (respostas reais do Google Forms; detalhes no laudo)
    for tabela, (nome, data, funcionou, falhou, nao_testado) in zip(d.tables[1:6], COLEGAS):
        acrescentar_na_celula(tabela.rows[0].cells[0], nome)
        acrescentar_na_celula(tabela.rows[0].cells[1], data)
        for linha, texto in zip(tabela.rows[1:4], (funcionou, falhou, nao_testado)):
            acrescentar_na_celula(linha.cells[0], texto)

    # Laudo de qualidade: referências (usa os parágrafos vazios já existentes)
    i_laudo = next(i for i, p in enumerate(ps) if p.text.startswith("Insira a seguir o laudo"))
    ref = ps[i_laudo].runs[0]
    linhas = [
        "Laudo completo: docs/situacao-3/laudo-qualidade.md (no repositório indicado acima).",
        "Evidências (prints das telas): docs/evidencias/. Plano de testes de verificação e validação: "
        "docs/situacao-3/plano-testes.md. Relatório de testes automatizados: docs/situacao-2/relatorio-testes.md.",
        "Resumo: 116 testes automatizados aprovados, cobertura de 97%; 4 defeitos na verificação interna (D-01 a "
        "D-04), todos corrigidos. Testes dos 5 colegas: 1 defeito de severidade média (C-01, corrigido) e 1 relato "
        "encerrado por não ser defeito (C-02); 4 de 6 sugestões aplicadas. Parecer: aprovado, sem defeito crítico "
        "ou alto aberto.",
        "Correções após os testes: docs/situacao-3/changelog-melhorias.md.",
    ]
    vazios = [p for p in ps[i_laudo + 1:] if not p.text.strip()][:len(linhas)]
    proximo_titulo = next(i for i, p in enumerate(ps) if p.text.startswith("Vídeo da Solução"))
    assert all(ps.index(p) < proximo_titulo for p in vazios), "parágrafos vazios insuficientes antes do vídeo"
    for p, texto in zip(vazios, linhas):
        run_como(p, texto, ref)

    # Vídeo
    escrever_celula(d.tables[6].rows[0], f"{a.video} (roteiro: docs/situacao-3/roteiro-video.md)")

    SAIDA.parent.mkdir(exist_ok=True)
    d.save(SAIDA)
    print("Formulário salvo em", SAIDA.relative_to(RAIZ))


if __name__ == "__main__":
    main()
