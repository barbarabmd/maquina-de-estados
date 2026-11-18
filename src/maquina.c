/*
 * maquina.c - Implementação da máquina de estados orientada a tabela.
 */
#include "maquina.h"

#define INVALIDO (-1)

/*
 * TABELA[estado atual][evento] = próximo estado (ou INVALIDO).
 * Ordem das colunas: MOEDA, SELECIONAR, CANCELAR, RETIRAR, FALHA, REPARO
 */
static const int TABELA[NUM_ESTADOS][NUM_EVENTOS] = {
    /* OCIOSA          */ { ESTADO_COM_CREDITO, INVALIDO, INVALIDO, INVALIDO, ESTADO_FORA_DE_SERVICO, INVALIDO },
    /* COM_CREDITO     */ { ESTADO_COM_CREDITO, ESTADO_ENTREGANDO, ESTADO_OCIOSA, INVALIDO, ESTADO_FORA_DE_SERVICO, INVALIDO },
    /* ENTREGANDO      */ { INVALIDO, INVALIDO, INVALIDO, ESTADO_OCIOSA, ESTADO_FORA_DE_SERVICO, INVALIDO },
    /* FORA_DE_SERVICO */ { INVALIDO, INVALIDO, INVALIDO, INVALIDO, INVALIDO, ESTADO_OCIOSA }
};

static const char *const NOMES_ESTADOS[NUM_ESTADOS] = {
    "OCIOSA", "COM_CREDITO", "ENTREGANDO", "FORA_DE_SERVICO"
};

static const char *const NOMES_EVENTOS[NUM_EVENTOS] = {
    "MOEDA", "SELECIONAR", "CANCELAR", "RETIRAR", "FALHA", "REPARO"
};

void maquina_iniciar(Maquina *m)
{
    m->estado = ESTADO_OCIOSA;
}

Estado maquina_estado(const Maquina *m)
{
    return m->estado;
}

int maquina_processar(Maquina *m, Evento e)
{
    int proximo;

    if (e < 0 || e >= NUM_EVENTOS || m->estado < 0 || m->estado >= NUM_ESTADOS) {
        return 0;
    }

    proximo = TABELA[m->estado][e];
    if (proximo == INVALIDO) {
        return 0;               /* evento ignorado: estado preservado */
    }

    m->estado = (Estado)proximo;
    return 1;
}

const char *estado_nome(Estado s)
{
    return (s >= 0 && s < NUM_ESTADOS) ? NOMES_ESTADOS[s] : "DESCONHECIDO";
}

const char *evento_nome(Evento e)
{
    return (e >= 0 && e < NUM_EVENTOS) ? NOMES_EVENTOS[e] : "DESCONHECIDO";
}
