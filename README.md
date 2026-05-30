# Codex Skills

Репозиторий для построения личной agentic delivery system: набора Codex skills, агентов, workflow, шаблонов и проверок для инфраструктуры, Big Data, ML/DS, backend/frontend, QA/AQA, IT Security и платформенной работы.

Цель не в том, чтобы собрать много промптов. Цель в том, чтобы агенты работали как управляемая инженерная организация: брали задачи из понятного контекста, работали спринтами, оставляли артефакты, фиксировали решения, не теряли память и улучшались после ошибок.

## Принципы

- Контекст является дорогим ресурсом: skills должны быть короткими, а детали лежать в references и templates.
- Каждый агент оставляет handoff: что сделал, как проверил, какие риски остались, что делать дальше.
- Agile используется как операционная модель, а не как имитация встреч.
- xOps и платформенные задачи закрываются только вместе с runbook, access map, observability и rollback/restore контекстом.
- Секреты никогда не попадают в репозиторий. Разрешены только ссылки на систему хранения, path, key, owner, role и безопасные команды проверки.
- Ошибки агентов превращаются в обновление skill, шаблона, workflow или eval case.

## Структура

```text
skills/      # Codex skills: процедурные знания и доменные workflow
agents/      # роли агентов и их контракт ответственности
workflows/   # командные сценарии: sprint planning, delivery, incident response
templates/   # стандартные артефакты: ADR, handoff, access-map, runbook
evals/       # проверки поведения skills/agents/workflows на типовых задачах
scripts/     # детерминированные проверки и утилиты репозитория
.memory/     # рабочая память самого репозитория и спринтовые артефакты
```

## Состав v1.0

Релиз `1.0.0` закрывает базовый scope:

| Pack | Назначение |
| --- | --- |
| `core` | discovery, память, handoff, review, evolution loop |
| `agile-delivery` | backlog, sprint planning, async standup, review, retro, Linear-ready metadata |
| `xops-platform` | platform design, GitOps, provisioning, secrets/access map, runbooks, observability, incident, backup/restore, cost |
| `software-engineering` | backend, frontend, API, database, performance, code review |
| `data-platform` | data architecture, pipelines, Spark, orchestration, analytics, DQ, governance |
| `ml-mlops` | ML research, MLOps, model evals, RAG, feature engineering |
| `qa-aqa` | QA strategy, automation, API testing, Playwright/E2E, performance testing |
| `security` | threat modeling, AppSec, cloud security, vulnerability triage, incident response |

Текущий масштаб можно посмотреть командой:

```bash
python3 scripts/inventory.py
```

## Рабочая Модель

Каждая итерация идет как спринт:

1. Sprint brief: цель, scope, definition of done.
2. Implementation: добавление или обновление skills, agents, workflows, templates.
3. Validation: запуск структурных проверок и ручная проверка смысла.
4. Handoff: что изменилось, какие решения приняты, что осталось.
5. Commit and push: каждый спринт сохраняется в GitHub.

## Версионирование

- `0.x`: базовые packs и структура.
- `1.0`: полноценная система с core, Agile delivery, xOps/platform, engineering, data, ML, QA и security packs.
- После `1.0`: расширение под конкретные проекты, Linear-интеграции, автоматические evals и специализированные runbooks.

## Проверка

```bash
python3 scripts/validate_repo.py
```

Валидатор проверяет базовую структуру, наличие всех required packs, frontmatter skills, обязательные поля agents, workflow/eval покрытие, ключевые шаблоны и отсутствие очевидных секретов в текстовых файлах.

## Как Использовать

1. Начинай с `project-discovery`, чтобы собрать минимальную карту проекта.
2. Переводи цели в backlog через `backlog-management`.
3. Для плановой работы запускай `sprint-planning`; для срочных задач используй kanban/incident mode.
4. Для платформенных изменений обязательно подключай `xops-platform-*` skills и оставляй `access-map.yaml`, `runbook.md`, `observability.md`.
5. Перед закрытием задачи запускай `technical-review` и `artifact-handoff`.
6. Если агент ошибся или процесс повторяется вручную, запускай `skill-evolution-loop`.

## Правило Для Доступов

Агент может написать:

```yaml
provider: vault
path: kv/platform/prod/argocd/admin
key: password
access_role: platform-prod-admin
```

Агент не может написать реальное значение пароля, токена, private key или base64 Kubernetes Secret.
