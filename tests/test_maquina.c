/*
 * test_maquina.c - Testes 100% automatizados da máquina de estados.
 *
 * Três grupos de testes:
 *   1) Testes de ESTADOS     - todos os 4 estados são alcançáveis
 *   2) Testes de TRANSIÇÕES  - as 9 transições válidas + as 15 inválidas
 *   3) Testes de CAMINHOS    - os 6 caminhos independentes (conjunto base)
 *
 * Retorna 0 se todos passarem; 1 se algum falhar (útil para CI / make test).
 */
#include <stdio.h>
#include <string.h>
#include "../src/maquina.h"

static int total = 0;
static int falhas = 0;

#define CHECK(cond, ...)                                            \
    do {                                                            \
        total++;                                                    \
        if (!(cond)) {                                              \
            falhas++;                                               \
            printf("  [FALHA] ");                                   \
            printf(__VA_ARGS__);                                    \
            printf("\n");                                           \
        }                                                           \
    } while (0)

/* ---------- utilitários ---------- */

/* Leva uma máquina nova até o estado alvo usando o caminho mais curto. */
static void preparar(Maquina *m, Estado alvo)
{
    maquina_iniciar(m);
    switch (alvo) {
    case ESTADO_OCIOSA:
        break;
    case ESTADO_COM_CREDITO:
        maquina_processar(m, EVT_MOEDA);
        break;
    case ESTADO_ENTREGANDO:
        maquina_processar(m, EVT_MOEDA);
        maquina_processar(m, EVT_SELECIONAR);
        break;
    case ESTADO_FORA_DE_SERVICO:
        maquina_processar(m, EVT_FALHA);
        break;
    default:
        break;
    }
}

/* ---------- 1) TESTES DE ESTADOS ---------- */

static void teste_estado_inicial(void)
{
    Maquina m;
    maquina_iniciar(&m);
    CHECK(maquina_estado(&m) == ESTADO_OCIOSA,
          "estado inicial deveria ser OCIOSA, obtido %s", estado_nome(maquina_estado(&m)));
}

static void teste_estados_alcancaveis(void)
{
    Maquina m;
    int s;
    for (s = 0; s < NUM_ESTADOS; s++) {
        preparar(&m, (Estado)s);
        CHECK(maquina_estado(&m) == (Estado)s,
              "estado %s nao alcancado (obtido %s)",
              estado_nome((Estado)s), estado_nome(maquina_estado(&m)));
    }
}

static void teste_nomes_dos_estados(void)
{
    CHECK(strcmp(estado_nome(ESTADO_OCIOSA), "OCIOSA") == 0, "nome OCIOSA");
    CHECK(strcmp(estado_nome(ESTADO_COM_CREDITO), "COM_CREDITO") == 0, "nome COM_CREDITO");
    CHECK(strcmp(estado_nome(ESTADO_ENTREGANDO), "ENTREGANDO") == 0, "nome ENTREGANDO");
    CHECK(strcmp(estado_nome(ESTADO_FORA_DE_SERVICO), "FORA_DE_SERVICO") == 0, "nome FORA_DE_SERVICO");
    CHECK(strcmp(estado_nome((Estado)99), "DESCONHECIDO") == 0, "nome de estado invalido");
    CHECK(strcmp(evento_nome(EVT_MOEDA), "MOEDA") == 0, "nome MOEDA");
    CHECK(strcmp(evento_nome(EVT_REPARO), "REPARO") == 0, "nome REPARO");
    CHECK(strcmp(evento_nome((Evento)99), "DESCONHECIDO") == 0, "nome de evento invalido");
}

/* ---------- 2) TESTES DE TRANSIÇÕES ---------- */

typedef struct {
    const char *id;
    Estado origem;
    Evento evento;
    Estado destino;
} Transicao;

/* As 9 transições válidas, escritas de forma independente da tabela do código. */
static const Transicao TRANSICOES_VALIDAS[] = {
    { "T1", ESTADO_OCIOSA,          EVT_MOEDA,      ESTADO_COM_CREDITO     },
    { "T2", ESTADO_OCIOSA,          EVT_FALHA,      ESTADO_FORA_DE_SERVICO },
    { "T3", ESTADO_COM_CREDITO,     EVT_MOEDA,      ESTADO_COM_CREDITO     },
    { "T4", ESTADO_COM_CREDITO,     EVT_SELECIONAR, ESTADO_ENTREGANDO      },
    { "T5", ESTADO_COM_CREDITO,     EVT_CANCELAR,   ESTADO_OCIOSA          },
    { "T6", ESTADO_COM_CREDITO,     EVT_FALHA,      ESTADO_FORA_DE_SERVICO },
    { "T7", ESTADO_ENTREGANDO,      EVT_RETIRAR,    ESTADO_OCIOSA          },
    { "T8", ESTADO_ENTREGANDO,      EVT_FALHA,      ESTADO_FORA_DE_SERVICO },
    { "T9", ESTADO_FORA_DE_SERVICO, EVT_REPARO,     ESTADO_OCIOSA          }
};
#define NUM_TRANSICOES_VALIDAS ((int)(sizeof TRANSICOES_VALIDAS / sizeof TRANSICOES_VALIDAS[0]))

static int eh_transicao_valida(Estado s, Evento e)
{
    int i;
    for (i = 0; i < NUM_TRANSICOES_VALIDAS; i++) {
        if (TRANSICOES_VALIDAS[i].origem == s && TRANSICOES_VALIDAS[i].evento == e) return 1;
    }
    return 0;
}

static void teste_transicoes_validas(void)
{
    int i;
    for (i = 0; i < NUM_TRANSICOES_VALIDAS; i++) {
        const Transicao *t = &TRANSICOES_VALIDAS[i];
        Maquina m;
        int ret;
        preparar(&m, t->origem);
        ret = maquina_processar(&m, t->evento);
        CHECK(ret == 1, "%s: %s --%s--> deveria retornar 1", t->id,
              estado_nome(t->origem), evento_nome(t->evento));
        CHECK(maquina_estado(&m) == t->destino, "%s: destino esperado %s, obtido %s", t->id,
              estado_nome(t->destino), estado_nome(maquina_estado(&m)));
    }
}

static void teste_transicoes_invalidas(void)
{
    int s, e, quantidade = 0;
    for (s = 0; s < NUM_ESTADOS; s++) {
        for (e = 0; e < NUM_EVENTOS; e++) {
            Maquina m;
            int ret;
            if (eh_transicao_valida((Estado)s, (Evento)e)) continue;
            quantidade++;
            preparar(&m, (Estado)s);
            ret = maquina_processar(&m, (Evento)e);
            CHECK(ret == 0, "%s --%s--> deveria ser ignorado (retorno 0)",
                  estado_nome((Estado)s), evento_nome((Evento)e));
            CHECK(maquina_estado(&m) == (Estado)s, "%s --%s--> nao deveria mudar o estado",
                  estado_nome((Estado)s), evento_nome((Evento)e));
        }
    }
    CHECK(quantidade == NUM_ESTADOS * NUM_EVENTOS - NUM_TRANSICOES_VALIDAS,
          "quantidade de combinacoes invalidas inesperada: %d", quantidade);
}

static void teste_entradas_invalidas(void)
{
    Maquina m;
    maquina_iniciar(&m);
    CHECK(maquina_processar(&m, (Evento)99) == 0, "evento fora do intervalo deve ser rejeitado");
    CHECK(maquina_processar(&m, (Evento)-1) == 0, "evento negativo deve ser rejeitado");
    CHECK(maquina_estado(&m) == ESTADO_OCIOSA, "estado deve ser preservado apos evento invalido");
    m.estado = (Estado)99; /* estado corrompido */
    CHECK(maquina_processar(&m, EVT_MOEDA) == 0, "estado corrompido deve ser rejeitado");
}

/* ---------- 3) TESTES DE CAMINHOS ---------- */

#define MAX_PASSOS 8

typedef struct {
    const char *id;
    const char *descricao;
    int passos;
    Evento eventos[MAX_PASSOS];
    Estado estados[MAX_PASSOS];   /* estado esperado após cada evento */
} Caminho;

/* Conjunto base de 6 caminhos independentes: V(G) = E - N + 1 = 9 - 4 + 1 = 6 */
static const Caminho CAMINHOS[] = {
    { "C1", "compra completa: OCIOSA > COM_CREDITO > ENTREGANDO > OCIOSA", 3,
      { EVT_MOEDA, EVT_SELECIONAR, EVT_RETIRAR },
      { ESTADO_COM_CREDITO, ESTADO_ENTREGANDO, ESTADO_OCIOSA } },

    { "C2", "cancelamento: OCIOSA > COM_CREDITO > OCIOSA", 2,
      { EVT_MOEDA, EVT_CANCELAR },
      { ESTADO_COM_CREDITO, ESTADO_OCIOSA } },

    { "C3", "credito acumulado: OCIOSA > COM_CREDITO > COM_CREDITO > OCIOSA", 3,
      { EVT_MOEDA, EVT_MOEDA, EVT_CANCELAR },
      { ESTADO_COM_CREDITO, ESTADO_COM_CREDITO, ESTADO_OCIOSA } },

    { "C4", "falha em repouso: OCIOSA > FORA_DE_SERVICO > OCIOSA", 2,
      { EVT_FALHA, EVT_REPARO },
      { ESTADO_FORA_DE_SERVICO, ESTADO_OCIOSA } },

    { "C5", "falha com credito: OCIOSA > COM_CREDITO > FORA_DE_SERVICO > OCIOSA", 3,
      { EVT_MOEDA, EVT_FALHA, EVT_REPARO },
      { ESTADO_COM_CREDITO, ESTADO_FORA_DE_SERVICO, ESTADO_OCIOSA } },

    { "C6", "falha na entrega: OCIOSA > COM_CREDITO > ENTREGANDO > FORA_DE_SERVICO > OCIOSA", 4,
      { EVT_MOEDA, EVT_SELECIONAR, EVT_FALHA, EVT_REPARO },
      { ESTADO_COM_CREDITO, ESTADO_ENTREGANDO, ESTADO_FORA_DE_SERVICO, ESTADO_OCIOSA } }
};
#define NUM_CAMINHOS ((int)(sizeof CAMINHOS / sizeof CAMINHOS[0]))

static void teste_caminhos_independentes(void)
{
    int i, p;
    for (i = 0; i < NUM_CAMINHOS; i++) {
        const Caminho *c = &CAMINHOS[i];
        Maquina m;
        maquina_iniciar(&m);
        for (p = 0; p < c->passos; p++) {
            int ret = maquina_processar(&m, c->eventos[p]);
            CHECK(ret == 1, "%s passo %d: evento %s deveria ser aceito", c->id, p + 1,
                  evento_nome(c->eventos[p]));
            CHECK(maquina_estado(&m) == c->estados[p], "%s passo %d: esperado %s, obtido %s",
                  c->id, p + 1, estado_nome(c->estados[p]), estado_nome(maquina_estado(&m)));
        }
        CHECK(maquina_estado(&m) == ESTADO_OCIOSA,
              "%s deveria terminar em OCIOSA (estado inicial)", c->id);
    }
}

/* Os 6 caminhos juntos devem cobrir as 9 transições (cada uma ao menos 1 vez). */
static void teste_caminhos_cobrem_transicoes(void)
{
    int t, i, p, cobertas = 0;
    for (t = 0; t < NUM_TRANSICOES_VALIDAS; t++) {
        int achou = 0;
        for (i = 0; i < NUM_CAMINHOS && !achou; i++) {
            Estado atual = ESTADO_OCIOSA;
            for (p = 0; p < CAMINHOS[i].passos; p++) {
                if (atual == TRANSICOES_VALIDAS[t].origem &&
                    CAMINHOS[i].eventos[p] == TRANSICOES_VALIDAS[t].evento) {
                    achou = 1;
                    break;
                }
                atual = CAMINHOS[i].estados[p];
            }
        }
        CHECK(achou, "transicao %s nao coberta pelos caminhos", TRANSICOES_VALIDAS[t].id);
        cobertas += achou;
    }
    CHECK(cobertas == NUM_TRANSICOES_VALIDAS, "cobertura de transicoes pelos caminhos incompleta");
}

/* ---------- execução ---------- */

typedef void (*FuncaoTeste)(void);

static void executar(const char *nome, FuncaoTeste f)
{
    int falhas_antes = falhas, total_antes = total;
    f();
    printf("[%s] %-38s (%d verificacoes)\n",
           falhas == falhas_antes ? " OK " : "FAIL", nome, total - total_antes);
}

int main(void)
{
    printf("=== Testes da Maquina de Estados (vending) ===\n");

    printf("\n-- Testes de estados --\n");
    executar("estado inicial",                teste_estado_inicial);
    executar("todos os estados alcancaveis",  teste_estados_alcancaveis);
    executar("nomes de estados e eventos",    teste_nomes_dos_estados);

    printf("\n-- Testes de transicoes --\n");
    executar("9 transicoes validas",          teste_transicoes_validas);
    executar("15 transicoes invalidas",       teste_transicoes_invalidas);
    executar("entradas invalidas",            teste_entradas_invalidas);

    printf("\n-- Testes de caminhos --\n");
    executar("6 caminhos independentes",      teste_caminhos_independentes);
    executar("caminhos cobrem transicoes",    teste_caminhos_cobrem_transicoes);

    printf("\nResumo: %d verificacoes, %d falhas\n", total, falhas);
    printf(falhas == 0 ? "RESULTADO: TODOS OS TESTES PASSARAM\n"
                       : "RESULTADO: HA TESTES FALHANDO\n");
    return falhas == 0 ? 0 : 1;
}
