CC      = gcc
CFLAGS  = -std=c99 -Wall -Wextra -Wpedantic -O0

.PHONY: all test cobertura clean

all: build/maquina

build:
	mkdir -p build

build/maquina: src/main.c src/maquina.c src/maquina.h | build
	$(CC) $(CFLAGS) -o $@ src/main.c src/maquina.c

build/test_maquina: tests/test_maquina.c src/maquina.c src/maquina.h | build
	$(CC) $(CFLAGS) -o $@ tests/test_maquina.c src/maquina.c

# Executa a suíte automatizada (retorna código != 0 se algum teste falhar)
test: build/test_maquina
	./build/test_maquina

# Cobertura de linhas/ramos de src/maquina.c com gcov
cobertura: | build
	$(CC) $(CFLAGS) --coverage -o build/test_cov tests/test_maquina.c src/maquina.c
	cd build && ./test_cov > /dev/null && gcov -b test_cov-maquina.gcda | head -n 6

clean:
	rm -rf build *.gcda *.gcno *.gcov
