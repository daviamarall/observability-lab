# SLI / SLO — Observability Lab

Este documento formaliza os **Indicadores de Nível de Serviço (SLI)**, os **Objetivos (SLO)** e o **orçamento de erro (error budget)** usados neste laboratório. É o mesmo raciocínio aplicado a sistemas de produção.

## 1. Definições

| Termo             | Significado                                                              |
|-------------------|--------------------------------------------------------------------------|
| **SLI**           | Métrica que mede um aspecto do serviço (ex.: taxa de sucesso)            |
| **SLO**           | Meta para o SLI em uma janela de tempo (ex.: 99,9% em 30 dias)           |
| **SLA**           | Acordo contratual com o cliente (consequências se o SLO não for atingido)|
| **Error budget**  | Quanto de "falha" o SLO permite (100% − SLO)                             |

## 2. SLIs adotados

### 2.1 Disponibilidade

Proporção de requisições bem-sucedidas (não-5xx) sobre o total.

```
sli_error_ratio = sum(rate(http_requests_total{status=~"5.."}[5m]))
                  / sum(rate(http_requests_total[5m]))

disponibilidade = 1 - sli_error_ratio
```

### 2.2 Latência

Percentil 95 do tempo de resposta, medido pelo histograma `http_request_duration_seconds`.

```
sli_latency_p95 = histogram_quantile(
  0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

## 3. SLOs

| SLI            | SLO alvo | Janela | Error budget        |
|----------------|----------|--------|---------------------|
| Disponibilidade| 99,9%    | 30 dias| 0,1% → ~43 min/mês  |
| Latência P95   | < 300 ms | 30 dias| 5% dos períodos     |

### Como calcular o error budget

Para 30 dias (~43.200 minutos) e SLO de 99,9%:

```
budget = (1 - 0.999) * 43200 min = 43.2 min
```

Ou seja: o serviço pode ficar **até ~43 minutos/mês** em violação antes de o SLO ser rompido.

## 4. Política de alerta

- Alertas **preferem sintomas** (taxa de erro, latência) a **causas** (CPU, memória).
- Alertas de `critical` disparam em **violação do SLO**, não em qualquer variação.
- Cada alerta aponta para um **runbook** ([RUNBOOK.md](RUNBOOK.md)).

| Alerta           | Expressão                                             | `for` | Severidade |
|------------------|-------------------------------------------------------|-------|------------|
| `HighErrorRate`  | `job:sli_error_ratio:rate5m > 0.05`                   | 2m    | critical   |
| `HighLatencyP95` | `job:sli_latency_p95:rate5m > 0.3`                    | 5m    | warning    |
| `AppDown`        | `up{job="observability-lab-app"} == 0`                | 1m    | critical   |

## 5. Error budget policy (burn rate)

Quando o error budget é consumido rápido demais (alta "*burn rate*"), a recomendação é:

1. **Congelar** entregas que mudam comportamento (feature freeze).
2. Priorizar **confiabilidade** (correções, dívida técnica).
3. Revisão pós-incidente obrigatória.

Exemplo de burn rate (referência de mercado):

| Janela longa | Janela curta | Consumo do budget | Ação       |
|--------------|--------------|-------------------|------------|
| 1h           | 5m           | 14,4x             | Page       |
| 6h           | 30m          | 6x                | Ticket     |
| 3d           | 6h           | 1x                | Acompanhar |
