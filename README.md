# Trabalho Prático: Máquina de Estados

Disciplina: Análise de Algoritmos

Máquina de venda automática (vending) implementada em **C**, com testes 100% automatizados
de **estados**, **transições** e **caminhos independentes**.

## O sistema modelado

| Item | Descrição |
| --- | --- |
| Estados (4) | `OCIOSA` (inicial), `COM_CREDITO`, `ENTREGANDO`, `FORA_DE_SERVICO` |
| Eventos (6) | `MOEDA`, `SELECIONAR`, `CANCELAR`, `RETIRAR`, `FALHA`, `REPARO` |
| Transições válidas (9) | T1 a T9, definidas na tabela `TABELA` em `src/maquina.c` |
| Transições inválidas (15) | Ignoradas: a função retorna 0 e o estado é preservado |
| Caminhos independentes (6) | V(G) = E − N + 1 = 9 − 4 + 1 = 6 |

O diagrama de estados está em `docs/diagrama.png`.

## Estrutura

```
src/maquina.h         interface (estados, eventos, funções)
src/maquina.c         implementação orientada a tabela
src/main.c            demonstração interativa (opcional)
tests/test_maquina.c  suíte de testes automatizados
docs/                 diagrama (.dot/.png)
Makefile              atalhos de compilação (opcional)
```

## Requisitos

Somente o compilador `gcc`. O `make` é opcional.

- **Windows:** instale o [MSYS2](https://www.msys2.org) e, no terminal "MSYS2 UCRT64", rode
  `pacman -S mingw-w64-ucrt-x86_64-gcc`. Adicione `C:\msys64\ucrt64\bin` ao `Path` do Windows
  e confira com `gcc --version` no PowerShell.
- **Linux (Ubuntu/Debian):** `sudo apt install build-essential`
- **macOS:** `xcode-select --install`

## Como compilar e executar

### Windows (PowerShell) — apenas gcc

Dentro da pasta do projeto:

```powershell
mkdir build
```

(se a pasta `build` já existir, ignore a mensagem)

**Testes automatizados:**

```powershell
gcc -std=c99 -Wall -Wextra -Wpedantic -o build\test_maquina.exe tests\test_maquina.c src\maquina.c
.\build\test_maquina.exe
```

**Demonstração interativa:**

```powershell
gcc -std=c99 -Wall -Wextra -Wpedantic -o build\maquina.exe src\main.c src\maquina.c
.\build\maquina.exe
```

### Linux / macOS / WSL — apenas gcc

```bash
mkdir -p build

# testes automatizados
gcc -std=c99 -Wall -Wextra -Wpedantic -o build/test_maquina tests/test_maquina.c src/maquina.c
./build/test_maquina

# demonstração interativa
gcc -std=c99 -Wall -Wextra -Wpedantic -o build/maquina src/main.c src/maquina.c
./build/maquina
```

### Com make (opcional)

Em Linux, macOS, WSL ou MSYS2 use `make`; no Windows com MinGW use `mingw32-make`
(no MSYS2 UCRT64: `pacman -S mingw-w64-ucrt-x86_64-make`).

```bash
make test        # compila e roda os testes (código de saída 0 = sucesso)
make cobertura   # cobertura de linhas e ramos com gcov
make             # compila a demonstração em build/maquina
make clean       # apaga a pasta build
```

## Testes automatizados

Os testes ficam em `tests/test_maquina.c` e cobrem:

| Grupo | O que verifica |
| --- | --- |
| Estados | Os 4 estados são alcançáveis a partir do estado inicial |
| Transições | As 9 transições válidas (retorno 1 e destino correto) e as 15 inválidas (retorno 0 e estado preservado), além de entradas fora do intervalo |
| Caminhos | Os 6 caminhos independentes, conferindo o estado após cada evento, e a cobertura das 9 transições pela união deles |

O programa de testes retorna código de saída 0 se todas as verificações passarem e 1 se alguma falhar.

Resultado esperado no final da execução:

```text
Resumo: 116 verificacoes, 0 falhas
RESULTADO: TODOS OS TESTES PASSARAM
```

### Cobertura de código (opcional)

Com make: `make cobertura`. Sem make, no Linux/macOS/WSL:

```bash
gcc -std=c99 --coverage -o build/test_cov tests/test_maquina.c src/maquina.c
cd build && ./test_cov > /dev/null && gcov -b test_cov-maquina.gcda
```

Resultado esperado para `src/maquina.c`: 100% das linhas e 100% dos ramos executados.
O gcov pode exibir `Cannot open source file src/maquina.c`; é inofensivo, pois ele roda dentro de `build/`.

## Demonstração interativa

Digite um evento por linha e `sair` para encerrar: `moeda`, `selecionar`, `cancelar`,
`retirar`, `falha`, `reparo`.

```text
Estado inicial: OCIOSA
> moeda
OK -> COM_CREDITO
> selecionar
OK -> ENTREGANDO
> retirar
OK -> OCIOSA
> retirar
Evento ignorado em OCIOSA
> sair
```

## Regenerar o diagrama (opcional)

Requer [Graphviz](https://graphviz.org):

```bash
dot -Tpng docs/diagrama.dot -o docs/diagrama.png
```
