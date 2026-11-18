/*
 * main.c - Demonstração interativa (opcional; não faz parte dos testes).
 * Digite os eventos: moeda, selecionar, cancelar, retirar, falha, reparo, sair
 */
#include <stdio.h>
#include <string.h>
#include "maquina.h"

static int igual_sem_caixa(const char *a, const char *b)
{
    while (*a && *b && ((*a | 0x20) == (*b | 0x20))) { a++; b++; }
    return *a == '\0' && *b == '\0';
}

int main(void)
{
    Maquina m;
    char linha[64];
    int i;

    maquina_iniciar(&m);
    printf("Estado inicial: %s\n", estado_nome(maquina_estado(&m)));

    while (printf("> "), fgets(linha, sizeof linha, stdin) != NULL) {
        linha[strcspn(linha, "\r\n")] = '\0';
        if (strcmp(linha, "sair") == 0) break;

        for (i = 0; i < NUM_EVENTOS; i++) {
            if (igual_sem_caixa(linha, evento_nome((Evento)i))) break;
        }
        if (i == NUM_EVENTOS) {
            printf("Evento desconhecido.\n");
            continue;
        }
        if (maquina_processar(&m, (Evento)i)) {
            printf("OK -> %s\n", estado_nome(maquina_estado(&m)));
        } else {
            printf("Evento ignorado em %s\n", estado_nome(maquina_estado(&m)));
        }
    }
    return 0;
}
