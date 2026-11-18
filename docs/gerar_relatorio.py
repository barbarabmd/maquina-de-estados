# -*- coding: utf-8 -*-
"""Gera o relatório em PDF do Trabalho Prático de Máquina de Estados.
Uso (a partir da pasta docs/):  python3 gerar_relatorio.py
Antes de gerar, preencha INTEGRANTES e REPO_URL abaixo."""
import os, re, subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, Preformatted, KeepTogether)

# ====== PREENCHA ======
INTEGRANTES = ["[Nome completo - integrante 1]", "[Nome completo - integrante 2]",
               "[Nome completo - integrante 3]", "[Nome completo - integrante 4]"]
REPO_URL = "https://github.com/[usuario]/maquina-de-estados"
INSTITUICAO = "Universidade Católica de Brasília - Ciência da Computação"
# =======================

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONTES = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FONTES + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", FONTES + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", FONTES + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DVM", FONTES + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-B")

AZUL = colors.HexColor("#1F3A5F")
CINZA = colors.HexColor("#F3F5F8")

corpo = ParagraphStyle("corpo", fontName="DV", fontSize=9.5, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=14, leading=18, textColor=AZUL, spaceBefore=12, spaceAfter=6, keepWithNext=1)
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=11, leading=15, textColor=AZUL, spaceBefore=8, spaceAfter=4, keepWithNext=1)
cel = ParagraphStyle("cel", fontName="DV", fontSize=8.3, leading=11)
celb = ParagraphStyle("celb", parent=cel, fontName="DV-B", textColor=colors.white)
celc = ParagraphStyle("celc", parent=cel, alignment=TA_CENTER)
celm = ParagraphStyle("celm", parent=cel, fontSize=7.1, leading=9)
celmc = ParagraphStyle("celmc", parent=celm, alignment=TA_CENTER)
celmb = ParagraphStyle("celmb", parent=celm, fontName="DV-B", textColor=colors.white, alignment=TA_CENTER)
legenda = ParagraphStyle("leg", fontName="DV-I", fontSize=8, leading=10, alignment=TA_CENTER, spaceAfter=8, textColor=colors.HexColor("#444444"))
cod = ParagraphStyle("cod", fontName="DVM", fontSize=6.4, leading=8.2)


def P(t, s=corpo): return Paragraph(t, s)


def tabela(cabecalho, linhas, larguras, centro=(), pequeno=False):
    sh, sc, sn = (celmb, celmc, celm) if pequeno else (celb, celc, cel)
    dados = [[P(c, sh) for c in cabecalho]]
    for l in linhas:
        dados.append([P(str(c), sc if i in centro else sn) for i, c in enumerate(l)])
    t = Table(dados, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CINZA]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C2D0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def trecho(arquivo, marcador, rotulo):
    """Extrai do arquivo o bloco que começa na linha com 'marcador' e termina na
    primeira linha que começa com '}' - garante que o trecho é o código real."""
    linhas = open(os.path.join(RAIZ, arquivo), encoding="utf-8").read().split("\n")
    ini = next(i for i, l in enumerate(linhas) if marcador in l)
    fim = next(i for i in range(ini, len(linhas)) if linhas[i].startswith("}"))
    txt = "\n".join(linhas[ini:fim + 1])
    # reduz a fonte, se preciso, para a linha mais longa caber na caixa (17 cm - preenchimento)
    maior = max(pdfmetrics.stringWidth(l, "DVM", 1) for l in txt.split("\n"))
    tam = min(6.4, (17 * cm - 10) / maior)
    estilo = ParagraphStyle("codx", parent=cod, fontSize=tam, leading=tam * 1.28)
    caixa = Table([[Preformatted(txt, estilo)]], colWidths=[17 * cm])
    caixa.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CINZA),
                               ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C2D0")),
                               ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]))
    return [caixa, P(rotulo, legenda)]


def executar(cmd):
    r = subprocess.run(cmd, shell=True, cwd=RAIZ, capture_output=True, text=True)
    return r.stdout + r.stderr


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(2 * cm, 1.2 * cm, "Trabalho Prático: Máquina de Estados - Sistemas Computacionais")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, "Página %d" % doc.page)
    canvas.restoreState()


H = []

# ---------------- CAPA ----------------
H += [Spacer(1, 3.5 * cm),
      P("<font size=11 color='#666666'>%s</font>" % INSTITUICAO, ParagraphStyle("c0", parent=corpo, alignment=TA_CENTER)),
      Spacer(1, 0.6 * cm),
      P("<font size=22 color='#1F3A5F'><b>Trabalho Prático:<br/>Máquina de Estados</b></font>", ParagraphStyle("c1", parent=corpo, alignment=TA_CENTER, leading=28)),
      Spacer(1, 0.5 * cm),
      P("<font size=12>Máquina de venda automática (vending) em C<br/>com testes automatizados de estados, transições e caminhos</font>",
        ParagraphStyle("c2", parent=corpo, alignment=TA_CENTER, leading=17)),
      Spacer(1, 1.6 * cm),
      P("<b>Disciplina:</b> Sistemas Computacionais<br/><b>Modalidade:</b> Em grupo", ParagraphStyle("c3", parent=corpo, alignment=TA_CENTER, leading=16)),
      Spacer(1, 0.8 * cm),
      P("<b>Integrantes</b><br/>" + "<br/>".join(INTEGRANTES), ParagraphStyle("c4", parent=corpo, alignment=TA_CENTER, leading=16)),
      Spacer(1, 0.8 * cm),
      P("<b>Repositório Git</b><br/>%s" % REPO_URL, ParagraphStyle("c5", parent=corpo, alignment=TA_CENTER, leading=16)),
      PageBreak()]

# ---------------- 1. OBJETIVO ----------------
H += [P("1. Objetivo", h1),
      P("Este trabalho implementa, em linguagem C, uma máquina de estados simples e a valida por meio de "
        "testes <b>100% automatizados</b> de estados, de transições e de caminhos independentes. "
        "O problema modelado é uma <b>máquina de venda automática (vending)</b> simplificada: o cliente insere "
        "moedas, escolhe um produto e retira o item; a máquina também pode falhar e precisa de reparo. "
        "Para manter o modelo enxuto, valores monetários, preços e estoque foram abstraídos: o "
        "comportamento relevante é apenas o <i>fluxo</i> da operação."),
      P("<b>Regras do sistema</b>"),
      tabela(["Id", "Regra"], [
          ("R1", "A máquina inicia no estado OCIOSA."),
          ("R2", "Ao receber uma moeda em OCIOSA, passa a ter crédito (COM_CREDITO)."),
          ("R3", "Moedas adicionais em COM_CREDITO acumulam crédito e mantêm o estado."),
          ("R4", "Com crédito, selecionar um produto o libera (ENTREGANDO)."),
          ("R5", "Com crédito, cancelar devolve as moedas e volta a OCIOSA."),
          ("R6", "Com o produto liberado, retirá-lo encerra a venda e volta a OCIOSA."),
          ("R7", "Uma falha pode ocorrer em OCIOSA, COM_CREDITO ou ENTREGANDO e leva a FORA_DE_SERVICO."),
          ("R8", "Somente o reparo tira a máquina de FORA_DE_SERVICO, retornando a OCIOSA."),
          ("R9", "Qualquer evento sem transição definida no estado atual é ignorado e o estado é preservado."),
      ], [1.4 * cm, 15.6 * cm], centro=(0,))]

# ---------------- 2. ESPECIFICAÇÃO ----------------
H += [P("2. Especificação do Sistema", h1), P("2.1 Estados", h2),
      P("Definimos quatro estados independentes, mutuamente exclusivos: em qualquer instante a máquina está em exatamente um deles."),
      tabela(["Id", "Estado", "Descrição"], [
          ("S0", "OCIOSA", "Estado inicial. Aguarda a inserção de moeda."),
          ("S1", "COM_CREDITO", "Há crédito inserido. Aguarda seleção, mais moedas ou cancelamento."),
          ("S2", "ENTREGANDO", "Produto liberado. Aguarda a retirada pelo cliente."),
          ("S3", "FORA_DE_SERVICO", "Falha detectada. Só aceita o evento de reparo."),
      ], [1.4 * cm, 4.2 * cm, 11.4 * cm], centro=(0,)),
      P("Eventos de entrada: <b>MOEDA, SELECIONAR, CANCELAR, RETIRAR, FALHA e REPARO</b> (6 eventos).", ParagraphStyle("x", parent=corpo, spaceBefore=6)),
      P("2.2 Transições", h2),
      P("Existem <b>9 transições válidas</b> (T1 a T9). Das 24 combinações possíveis de (estado, evento) - 4 estados x 6 "
        "eventos - as outras <b>15 são inválidas</b> e devem ser ignoradas sem alterar o estado (regra R9)."),
      tabela(["Id", "Origem", "Evento", "Destino", "Regra"], [
          ("T1", "OCIOSA", "MOEDA", "COM_CREDITO", "R2"),
          ("T2", "OCIOSA", "FALHA", "FORA_DE_SERVICO", "R7"),
          ("T3", "COM_CREDITO", "MOEDA", "COM_CREDITO (laço)", "R3"),
          ("T4", "COM_CREDITO", "SELECIONAR", "ENTREGANDO", "R4"),
          ("T5", "COM_CREDITO", "CANCELAR", "OCIOSA", "R5"),
          ("T6", "COM_CREDITO", "FALHA", "FORA_DE_SERVICO", "R7"),
          ("T7", "ENTREGANDO", "RETIRAR", "OCIOSA", "R6"),
          ("T8", "ENTREGANDO", "FALHA", "FORA_DE_SERVICO", "R7"),
          ("T9", "FORA_DE_SERVICO", "REPARO", "OCIOSA", "R8"),
      ], [1.2 * cm, 3.9 * cm, 3.3 * cm, 5.9 * cm, 2.7 * cm], centro=(0, 4)),
      Spacer(1, 6),
      P("<b>Tabela de transição de estados</b> (linhas: estado atual; colunas: evento; '-' = evento ignorado):"),
      tabela(["Estado \\ Evento", "MOEDA", "SELECIONAR", "CANCELAR", "RETIRAR", "FALHA", "REPARO"], [
          ("OCIOSA", "COM_CREDITO", "-", "-", "-", "FORA_DE_SERVICO", "-"),
          ("COM_CREDITO", "COM_CREDITO", "ENTREGANDO", "OCIOSA", "-", "FORA_DE_SERVICO", "-"),
          ("ENTREGANDO", "-", "-", "-", "OCIOSA", "FORA_DE_SERVICO", "-"),
          ("FORA_DE_SERVICO", "-", "-", "-", "-", "-", "OCIOSA"),
      ], [2.9 * cm, 2.4 * cm, 2.4 * cm, 2.0 * cm, 2.0 * cm, 3.0 * cm, 2.0 * cm], centro=(1, 2, 3, 4, 5, 6), pequeno=True),
      P("2.3 Diagrama de Estados", h2),
      Image(os.path.join(RAIZ, "docs", "diagrama.png"), width=17 * cm, height=6 * cm),
      P("Figura 1 - Diagrama de estados. O estado inicial (S0) é indicado pela seta de entrada e pela borda dupla; "
        "as transições de falha estão em vermelho e a de reparo em verde.", legenda)]

# Ajuste de proporção da imagem
from PIL import Image as PILImage
w, h = PILImage.open(os.path.join(RAIZ, "docs", "diagrama.png")).size
H[-2] = Image(os.path.join(RAIZ, "docs", "diagrama.png"), width=17 * cm, height=17 * cm * h / w)

H += [P("2.4 Caminhos independentes", h2),
      P("A quantidade de caminhos independentes é dada pela complexidade ciclomática do grafo de estados. Como o grafo é "
        "fortemente conexo (todo estado volta a OCIOSA), usamos V(G) = E - N + 1, com E = 9 transições e N = 4 estados: "
        "<b>V(G) = 9 - 4 + 1 = 6</b>. (Equivale a E - N + 2 quando se acrescenta uma aresta virtual de saída.) "
        "O conjunto base abaixo parte sempre de OCIOSA e retorna a ela, e cada caminho introduz ao menos uma transição inédita:"),
      tabela(["Id", "Caminho (estados)", "Eventos", "Transições", "Nova(s)"], [
          ("C1", "OCIOSA > COM_CREDITO > ENTREGANDO > OCIOSA", "MOEDA, SELECIONAR, RETIRAR", "T1, T4, T7", "T1, T4, T7"),
          ("C2", "OCIOSA > COM_CREDITO > OCIOSA", "MOEDA, CANCELAR", "T1, T5", "T5"),
          ("C3", "OCIOSA > COM_CREDITO > COM_CREDITO > OCIOSA", "MOEDA, MOEDA, CANCELAR", "T1, T3, T5", "T3"),
          ("C4", "OCIOSA > FORA_DE_SERVICO > OCIOSA", "FALHA, REPARO", "T2, T9", "T2, T9"),
          ("C5", "OCIOSA > COM_CREDITO > FORA_DE_SERVICO > OCIOSA", "MOEDA, FALHA, REPARO", "T1, T6, T9", "T6"),
          ("C6", "OCIOSA > COM_CREDITO > ENTREGANDO > FORA_DE_SERVICO > OCIOSA", "MOEDA, SELECIONAR, FALHA, REPARO", "T1, T4, T8, T9", "T8"),
      ], [1.0 * cm, 6.2 * cm, 4.2 * cm, 2.6 * cm, 3.0 * cm], centro=(0,)),
      P("Em conjunto, C1 a C6 percorrem todas as 9 transições e todos os 4 estados.", ParagraphStyle("y", parent=corpo, spaceBefore=6))]

# ---------------- IMPLEMENTAÇÃO ----------------
H += [P("3. Implementação (resumo)", h1),
      P("A máquina foi implementada de forma <b>orientada a tabela</b> (arquivos <font name='DVM'>src/maquina.h</font> e "
        "<font name='DVM'>src/maquina.c</font>): a tabela <font name='DVM'>TABELA</font> guarda o próximo estado para cada par "
        "(estado, evento) e <font name='DVM'>INVALIDO</font> marca as 15 combinações ignoradas. Assim a lógica fica separada dos dados "
        "e o código da função de processamento é curto e livre de ramificações aninhadas.")]
H += trecho("src/maquina.c", "static const int TABELA", "Trecho 1 - Tabela de transições (src/maquina.c).")
H += trecho("src/maquina.c", "int maquina_processar", "Trecho 2 - Função que processa um evento (src/maquina.c).")
H += [P("O código completo (incluindo <font name='DVM'>main.c</font> de demonstração, o <font name='DVM'>Makefile</font> e este "
        "relatório) está no repositório Git: <b>%s</b>." % REPO_URL)]

# ---------------- 4. CASOS DE TESTE ----------------
H += [P("4. Casos de Teste", h1),
      P("Todos os testes estão em <font name='DVM'>tests/test_maquina.c</font> e são executados por "
        "<font name='DVM'>make test</font>, sem nenhuma interação manual. O programa retorna código 0 se todas as verificações passam "
        "e 1 caso contrário. Para que os testes não repitam um possível erro da implementação, as transições esperadas e os "
        "caminhos são escritos <i>independentemente</i> da tabela do código, como oráculo de teste."),
      P("4.1 Testes de Estados", h2),
      P("Objetivo: cobrir <b>todos os 4 estados</b>. Cada estado é alcançado a partir do estado inicial pela sequência mais curta de eventos."),
      tabela(["Id", "Estado coberto", "Entrada (a partir de OCIOSA)", "Resultado esperado", "Função de teste"], [
          ("CT-E1", "OCIOSA", "(nenhum evento)", "OCIOSA", "teste_estado_inicial"),
          ("CT-E2", "COM_CREDITO", "MOEDA", "COM_CREDITO", "teste_estados_alcancaveis"),
          ("CT-E3", "ENTREGANDO", "MOEDA, SELECIONAR", "ENTREGANDO", "teste_estados_alcancaveis"),
          ("CT-E4", "FORA_DE_SERVICO", "FALHA", "FORA_DE_SERVICO", "teste_estados_alcancaveis"),
      ], [1.5 * cm, 3.3 * cm, 4.2 * cm, 3.4 * cm, 4.6 * cm], centro=(0,)),
      Spacer(1, 4),
      P("Há ainda verificação dos nomes dos estados e eventos (<font name='DVM'>teste_nomes_dos_estados</font>).", corpo),
      P("4.2 Testes de Transições", h2),
      P("Objetivo: cobrir <b>todas as 9 transições válidas</b> (T1 a T9) - o teste coloca a máquina no estado de origem, aplica o evento e "
        "confere o retorno (1) e o estado de destino - e também as <b>15 combinações inválidas</b>, que devem retornar 0 e preservar o estado. "
        "Em <font name='DVM'>teste_entradas_invalidas</font> verificam-se ainda evento fora do intervalo e estado corrompido."),
      tabela(["Casos", "Cobertura", "Resultado esperado", "Função de teste"], [
          ("CT-T1 a CT-T9", "T1 a T9 (uma verificação de retorno e uma de destino por transição)", "retorno 1 e estado de destino correto", "teste_transicoes_validas"),
          ("CT-T10 a CT-T24", "As 15 combinações (estado, evento) sem transição", "retorno 0 e estado inalterado", "teste_transicoes_invalidas"),
          ("CT-T25", "Evento fora do intervalo, evento negativo, estado corrompido", "retorno 0 e estado preservado", "teste_entradas_invalidas"),
      ], [2.6 * cm, 5.4 * cm, 4.0 * cm, 5.0 * cm]),
      Spacer(1, 6)]
H += trecho("tests/test_maquina.c", "static void teste_transicoes_validas", "Trecho 3 - Teste das 9 transições válidas (tests/test_maquina.c).")
H += [P("4.3 Testes de Caminhos", h2),
      P("Objetivo: cobrir os <b>6 caminhos independentes</b> (C1 a C6) da seção 2.4. Cada caminho é uma sequência de eventos com o "
        "estado esperado após <i>cada</i> passo; todos devem ser aceitos e terminar em OCIOSA. Um teste adicional "
        "(<font name='DVM'>teste_caminhos_cobrem_transicoes</font>) comprova que a união dos caminhos cobre as 9 transições.")]
H += trecho("tests/test_maquina.c", "static void teste_caminhos_independentes", "Trecho 4 - Execução dos caminhos independentes (tests/test_maquina.c).")
H += [tabela(["Id", "Eventos aplicados", "Estados esperados após cada evento"], [
          ("CT-C1", "MOEDA, SELECIONAR, RETIRAR", "COM_CREDITO, ENTREGANDO, OCIOSA"),
          ("CT-C2", "MOEDA, CANCELAR", "COM_CREDITO, OCIOSA"),
          ("CT-C3", "MOEDA, MOEDA, CANCELAR", "COM_CREDITO, COM_CREDITO, OCIOSA"),
          ("CT-C4", "FALHA, REPARO", "FORA_DE_SERVICO, OCIOSA"),
          ("CT-C5", "MOEDA, FALHA, REPARO", "COM_CREDITO, FORA_DE_SERVICO, OCIOSA"),
          ("CT-C6", "MOEDA, SELECIONAR, FALHA, REPARO", "COM_CREDITO, ENTREGANDO, FORA_DE_SERVICO, OCIOSA"),
      ], [1.5 * cm, 6.0 * cm, 9.5 * cm], centro=(0,))]

# ---------------- 5. EXECUÇÃO ----------------
saida = executar("make clean >/dev/null; make test 2>&1 | sed -n '/^===/,$p'")
cob = executar("make cobertura 2>&1 | grep -E 'Lines|Branches|Taken'")
H += [P("5. Execução e Resultados", h1),
      P("Para reproduzir: <font name='DVM'>git clone</font> do repositório, depois <font name='DVM'>make test</font> (testes) e "
        "<font name='DVM'>make cobertura</font> (cobertura com gcov). A compilação usa <font name='DVM'>gcc -std=c99 -Wall -Wextra -Wpedantic</font> "
        "e não emite avisos."),
      Table([[Preformatted(saida.strip(), ParagraphStyle("o", fontName="DVM", fontSize=7, leading=9))]], colWidths=[17 * cm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), CINZA), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C2D0"))])),
      P("Saída 1 - Resultado de <font name='DVM'>make test</font>.", legenda),
      Table([[Preformatted(cob.strip(), ParagraphStyle("o2", fontName="DVM", fontSize=7.5, leading=10))]], colWidths=[17 * cm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), CINZA), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C2D0"))])),
      P("Saída 2 - Cobertura do arquivo <font name='DVM'>src/maquina.c</font> medida pelo gcov.", legenda),
      P("Resultado: todas as verificações passaram, com <b>100% de cobertura de linhas e de ramos</b> da implementação, o que é coerente com a "
        "cobertura de 4/4 estados, 9/9 transições válidas, 15/15 transições inválidas e 6/6 caminhos independentes.")]

# ---------------- 6. CONSIDERAÇÕES FINAIS ----------------
H += [P("6. Considerações Finais", h1),
      P("Ao longo do trabalho o grupo consolidou a ideia de que uma máquina de estados é, antes de tudo, uma <b>especificação</b>: "
        "ao definir estados, eventos e a tabela de transições antes de programar, a implementação ficou curta e os testes puderam ser "
        "derivados diretamente do modelo. A abordagem orientada a tabela mostrou-se vantajosa porque separa os dados da lógica e "
        "torna evidente quais combinações são inválidas."),
      P("Aprendemos também a diferença entre os três níveis de cobertura: os testes de <i>estados</i> garantem que cada estado é "
        "alcançável; os de <i>transições</i> exigem verificar cada aresta - inclusive o que <i>não</i> deve acontecer (as 15 combinações "
        "inválidas e as entradas fora do intervalo); e os de <i>caminhos</i> conferem sequências completas de uso. O cálculo da complexidade "
        "ciclomática, V(G) = E - N + 1 = 6, deu um critério objetivo para escolher quantos caminhos independentes testar."),
      P("Por fim, reforçamos o valor da automação: com <font name='DVM'>make test</font> a suíte roda em milissegundos, devolve um código de "
        "saída que indica sucesso ou falha e pode ser reexecutada a cada alteração, e a medição com gcov nos deu evidência (100% de linhas e "
        "ramos) de que nenhum trecho do código ficou sem teste. Como limitação, o modelo abstrai valores monetários e estoque; uma extensão natural seria "
        "acrescentar variáveis de contexto (saldo, preço) e novos estados, como 'sem troco' ou 'sem estoque', reaplicando a mesma metodologia.")]

doc = SimpleDocTemplate(os.path.join(RAIZ, "docs", "Relatorio_Maquina_de_Estados.pdf"), pagesize=A4,
                        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                        title="Trabalho Prático: Máquina de Estados", author=", ".join(INTEGRANTES))
doc.build(H, onFirstPage=lambda c, d: None, onLaterPages=rodape)
print("PDF gerado.")
