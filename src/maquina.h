/*
 * maquina.h - Máquina de estados de uma máquina de venda automática (vending)
 */
#ifndef MAQUINA_H
#define MAQUINA_H

/* Estados (4) */
typedef enum {
    ESTADO_OCIOSA = 0,        /* aguardando moeda (estado inicial)          */
    ESTADO_COM_CREDITO,       /* moeda inserida, aguardando seleção         */
    ESTADO_ENTREGANDO,        /* produto liberado, aguardando retirada      */
    ESTADO_FORA_DE_SERVICO,   /* falha detectada, aguardando reparo         */
    NUM_ESTADOS
} Estado;

/* Eventos (6) */
typedef enum {
    EVT_MOEDA = 0,
    EVT_SELECIONAR,
    EVT_CANCELAR,
    EVT_RETIRAR,
    EVT_FALHA,
    EVT_REPARO,
    NUM_EVENTOS
} Evento;

typedef struct {
    Estado estado;
} Maquina;

/* Coloca a máquina no estado inicial (OCIOSA). */
void maquina_iniciar(Maquina *m);

/* Retorna o estado atual. */
Estado maquina_estado(const Maquina *m);

/*
 * Processa um evento.
 * Retorna 1 se havia transição definida (o estado pode mudar ou não, no
 * caso de laço) e 0 se o evento é inválido no estado atual (o estado é
 * mantido) ou se o evento/estado são inválidos.
 */
int maquina_processar(Maquina *m, Evento e);

/* Nomes legíveis, úteis para depuração e relatórios. */
const char *estado_nome(Estado s);
const char *evento_nome(Evento e);

#endif /* MAQUINA_H */
