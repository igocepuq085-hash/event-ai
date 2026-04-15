# Event AI

Проект собран под стек:

- Frontend: `Next.js`, `App Router`, `TypeScript`, `Tailwind CSS`
- Backend: `FastAPI`, `Python`, `OpenAI Responses API`, `python-docx`
- Хранение: `Railway Volume`, `submissions.json`
- Деплой: `Railway`, `frontend` и `backend` как отдельные сервисы

## Что уже есть

### Frontend

- главная страница с выбором только двух форматов
- отдельные анкеты `wedding` и `jubilee`
- страница `/login`
- закрытая через `middleware` host-панель `/host`
- страница заявки `/host/[id]`
- вход по `httpOnly` cookie

### Backend

- `GET /`
- `GET /health`
- `POST /api/questionnaire`
- `GET /api/submissions`
- `GET /api/submissions/{id}`
- `POST /api/submissions/{id}/generate-program`
- `GET /api/submissions/{id}/export-docx`

## Локальный запуск

### 1. Backend

```powershell
cd C:\Users\Николай\event-ai
python -m venv backend\venv
backend\venv\Scripts\python -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
backend\venv\Scripts\python -m uvicorn backend.main:app --reload
```

Backend откроется на `http://127.0.0.1:8000`, Swagger на `http://127.0.0.1:8000/docs`.

### 2. Frontend

```powershell
cd C:\Users\Николай\event-ai\frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Frontend откроется на `http://127.0.0.1:3000`.

## Переменные окружения

### Backend `.env`

- `OPENAI_API_KEY`
- `OPENAI_MODEL=gpt-5.4-mini`
- `FRONTEND_ORIGINS=http://localhost:3000`
- `RAILWAY_VOLUME_MOUNT_PATH=`

### Frontend `.env.local`

- `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`
- `HOST_PANEL_PASSWORD=change-me`

## Поведение генерации

- Если `OPENAI_API_KEY` доступен и сеть есть, backend использует `OpenAI Responses API`.
- Если ключ не указан или сеть недоступна, включается локальный fallback, чтобы продукт оставался рабочим.
- Данные по умолчанию хранятся в `backend/data/submissions.json`.
- Для Railway лучше задавать `RAILWAY_VOLUME_MOUNT_PATH`, чтобы данные жили в volume и не терялись после redeploy.

## Railway

Разворачивать лучше как два сервиса:

### `backend` service

- Root Directory: `backend`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Volume mount path: например `/data`
- Env:
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`
  - `FRONTEND_ORIGINS`
  - `RAILWAY_VOLUME_MOUNT_PATH=/data`

### `frontend` service

- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Start Command: `npm run start`
- Env:
  - `NEXT_PUBLIC_API_URL=<url backend service>`
  - `HOST_PANEL_PASSWORD=<your password>`
