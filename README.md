# Trabalho Prático: Máquina de Estados

Disciplina: Sistemas Computacionais — modalidade em grupo.

Máquina de venda automática (vending) implementada em **C**, com testes 100% automatizados
de **estados**, **transições** e **caminhos independentes**.

## Estrutura

```
src/maquina.h        interface (estados, eventos, funções)
src/maquina.c        implementação orientada a tabela
src/main.c           demonstração interativa (opcional)
tests/test_maquina.c suíte de testes automatizados
docs/                diagrama (.dot/.png), gerador do relatório e relatório em PDF
Makefile
```

## Como executar

```bash
make test        # compila e roda todos os testes (código de saída 0 = sucesso)
make cobertura   # cobertura de linhas/ramos com gcov
make             # compila a demonstração interativa em build/maquina
make clean
```

Requisitos: `gcc` e `make`. O relatório é gerado com `python3 docs/gerar_relatorio.py`
(requer `reportlab` e `pillow`; o diagrama usa Graphviz: `dot -Tpng docs/diagrama.dot -o docs/diagrama.png`).
