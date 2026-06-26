# Heureka — DevOps Training Plan

A working RabbitMQ → Consumer → PostgreSQL pipeline used as a hands-on DevOps training project.
Progress is tracked here layer by layer.

---

## Layer 1 — Container basics
- [x] Fix inter-container communication (RabbitMQ host, DB name, consumer commented out)
- [x] Use venv locally, psycopg2-binary in setup.py
- [x] Health checks for RabbitMQ and Postgres in docker-compose.yaml
- [x] Retry logic in consumer (don't crash if broker/db not ready yet)
- [x] `restart: on-failure` on consumer service

## Layer 2 — Kubernetes / k3s
- [x] Install and configure k3s locally
- [x] Namespace, ConfigMap, Sealed Secrets
- [x] Postgres StatefulSet + Service
- [x] RabbitMQ StatefulSet + Service
- [x] Consumer Deployment
- [x] Producer CronJob
- [x] End-to-end verified: producer → RabbitMQ → consumer → Postgres

> Raw k8s manifests and Terraform k8s configs removed — replaced by Helm (cleaner separation of concerns)

## Layer 2.5 — Terraform (Azure)
> Deferred until Azure account is set up. Terraform will provision Azure VMs + networking + k3s.
> Local KVM not available (VMware nested virt blocked).
- [ ] Set up Azure account and CLI
- [ ] Write Terraform config for Azure VMs + networking
- [ ] Remote state in Azure Blob Storage
- [ ] Install k3s on provisioned VMs via Terraform

## Layer 3 — Helm
- [x] Install Helm
- [x] Package the app as a Helm chart (namespace, configmap, secret, postgres, rabbitmq, consumer, producer)
- [x] End-to-end verified: producer CronJob → RabbitMQ → consumer → Postgres
- [ ] Use official sub-charts for RabbitMQ and Postgres
- [ ] Practice values overrides and multi-environment configs (e.g. values-dev.yaml, values-prod.yaml)

## Layer 4 — Observability
- [x] Expose Prometheus metrics from consumer (Counter, Histogram via prometheus-client)
- [x] Deploy Prometheus + Grafana via kube-prometheus-stack
- [x] PodMonitor for consumer scrape discovery
- [x] Grafana dashboard (processing rate, DB inserts, duration percentiles)
- [ ] Alertmanager rules (e.g. alert on failures or consumer down)
- [ ] Loki for log aggregation
- [ ] (Optional) OpenTelemetry tracing

## Layer 5 — CI/CD
- [ ] GitHub Actions: build and push Docker image on push
- [ ] Install ArgoCD in k3s
- [ ] GitOps deployment: ArgoCD watches repo and syncs to k3s

---

## Notes
- Producer runs locally (outside Docker/k3s) to simulate an external system sending messages
- RabbitMQ management UI: http://localhost:15672 (guest/guest)
- Current branch: main
