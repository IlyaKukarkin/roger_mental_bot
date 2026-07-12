# Roger Mental Bot

Телеграм-бот психологической самопомощи: каждый вечер спрашивает у пользователя
настроение (🟢🟡🟠🔴), показывает слова поддержки от других людей, ведёт
статистику настроения, поддерживает «друзей», волонтёрство и годовые отчёты.

## Архитектура

Монорепо из трёх рантаймов поверх одной MongoDB (`roger-bot-db`):

| Компонент | Технологии | Роль |
| --- | --- | --- |
| `python/roger` | Python 3.11, aiogram 2.x (polling) | Основной бот: настроение, друзья, статистика, поддержка |
| `python/jimmy` | Python, aiogram | Бот модерации сообщений (аппрув/блок от волонтёров) |
| Next.js (`pages`, `lib`, `components`) | Next.js 13, TypeScript | Веб-отчёты, API-роуты-краны и генерация PNG-картинок статистики (`@vercel/og`) |

Краны (`crons/*.sh` на VPS и `bin/*-cron.yaml` в GitHub Actions) дёргают
API-роуты `pages/api/*-cron`, которые вызывают логику из `lib/api/*`.

**Интеграции:** Doppler (секреты), MongoDB Atlas, Contentful (медиа),
Amplitude (аналитика), Cutt.ly (короткие ссылки), OpenAI, Healthchecks.io
(мониторинг кранов), Docker Compose на VPS.

## Локальный запуск

### Next.js (веб + API)

```bash
yarn install
yarn dev          # http://localhost:3000
```

Нужна переменная `MONGODB_URI` (через Doppler или `.env.local`).

### Python-боты

См. подробную инструкцию в [python/README.md](python/README.md). Кратко:

```bash
cd python/roger
source roger-venv/bin/activate
pip install -r requirements.txt
doppler run -- python3 main.py
```

## Краны

Описание всех кранов, включая ежедневный бэкап БД в Cloudflare R2, —
в [crons/README.md](crons/README.md).

## Деплой

Боты и Next.js крутятся в Docker Compose на VPS
(`python/docker-compose.yml`). Перезапуск — через GitHub Action `restart`
(`.github/workflows/restart.yaml`).
