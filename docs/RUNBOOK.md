# Runbook — Observability Lab

Procedimentos de resposta para os alertas definidos em `prometheus/alerts.yml`.
Cada seção segue a mesma estrutura: **o que significa → como confirmar → como mitigar → como resolver**.

---

## High Error Rate

**Alerta:** `HighErrorRate` · **Severidade:** critical · **SLO:** disponibilidade

### Sintomas
Taxa de respostas 5xx acima de 5% nos últimos 5 minutos.

### Confirmar
1. Abra o Prometheus (`http://localhost:9090`) e consulte:
   ```
   job:sli_error_ratio:rate5m
   ```
2. Veja no Grafana o painel **Error ratio (5xx)**.
3. Identifique o endpoint problemático:
   ```
   sum by (endpoint) (rate(http_requests_total{status=~"5.."}[5m]))
   ```

### Mitigar (ação imediata)
- Se for a aplicação: reinicie/redirecione o tráfego (`docker compose restart app`).
- Se for um deploy recente: **rollback** para a última versão saudável.
- Se for dependência externa: habilite *circuit breaker* / degrade funcionalidades.

### Resolver
- Abra postmortem (ver template em `sre-runbooks`).
- Corrija a causa raiz e adicione teste de regressão.

---

## High Latency P95

**Alerta:** `HighLatencyP95` · **Severidade:** warning · **SLO:** latência

### Sintomas
Percentil 95 acima de 300 ms por 5 minutos.

### Confirmar
```
job:sli_latency_p95:rate5m
```
Painel **Latency P95** no Grafana.

### Mitigar
- Verifique saturação de CPU/memória do pod/container.
- Aumente réplicas (scale out) se for carga legítima.
- Verifique dependências lentas (banco, APIs externas).

### Resolver
- Adicione índices/caching, otimize queries, ajuste timeouts.

---

## App Down

**Alerta:** `AppDown` · **Severidade:** critical

### Sintomas
`up{job="observability-lab-app"} == 0` — o Prometheus não consegue coletar métricas do alvo.

### Confirmar
1. `docker compose ps` — o container está de pé?
2. `curl http://localhost:8000/healthz`
3. Logs: `docker compose logs app --tail=100`

### Mitigar
- `docker compose restart app`
- Cheque limites de memória (OOMKilled) e portas em uso.

### Resolver
- Corrija a falha de inicialização; garanta probes corretas.

---

## Referências
- [Google SRE Book — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Prometheus — Alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
