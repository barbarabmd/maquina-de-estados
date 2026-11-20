CC      = gcc
CFLAGS  = -std=c99 -Wall -Wextra -Wpedantic -O0

# Extensão do executável (.exe no Windows)
ifeq ($(OS),Windows_NT)
EXT = .exe
else
EXT =
endif

# Detecta o shell: em shell POSIX (Linux, macOS, WSL, MSYS2, Git Bash) "echo" sem
# argumentos imprime vazio; no cmd.exe/PowerShell imprime "ECHO is on/off".
ifeq ($(shell echo),)
MKDIR     = mkdir -p build
RMDIR     = rm -rf build
RUN_TEST  = ./build/test_maquina$(EXT)
COBERTURA = cd build && ./test_cov$(EXT) > /dev/null && gcov -b test_cov-maquina.gcda
else
MKDIR     = if not exist build mkdir build
RMDIR     = if exist build rmdir /s /q build
RUN_TEST  = build\test_maquina$(EXT)
COBERTURA = cd build && test_cov$(EXT) > nul && gcov -b test_cov-maquina.gcda
endif

.PHONY: all test cobertura clean

all: build/maquina$(EXT)

build:
	$(MKDIR)

build/maquina$(EXT): src/main.c src/maquina.c src/maquina.h | build
	$(CC) $(CFLAGS) -o build/maquina$(EXT) src/main.c src/maquina.c

build/test_maquina$(EXT): tests/test_maquina.c src/maquina.c src/maquina.h | build
	$(CC) $(CFLAGS) -o build/test_maquina$(EXT) tests/test_maquina.c src/maquina.c

# Executa a suíte automatizada (retorna código != 0 se algum teste falhar)
test: build/test_maquina$(EXT)
	$(RUN_TEST)

# Cobertura de linhas/ramos de src/maquina.c com gcov
cobertura: | build
	$(CC) $(CFLAGS) --coverage -o build/test_cov$(EXT) tests/test_maquina.c src/maquina.c
	$(COBERTURA)

clean:
	$(RMDIR)