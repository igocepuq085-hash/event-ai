from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import json
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

app = FastAPI(title="Event AI Backend")

# Можно дополнять новыми доменами фронта через переменную FRONTEND_ORIGINS
extra_origins = os.getenv("FRONTEND_ORIGINS", "")
parsed_extra_origins = [item.strip() for item in extra_origins.split(",") if item.strip()]

allowed_origins = [
    "http://localhost:3000",
    "https://frontend-production-c187.up.railway.app",
    *parsed_extra_origins,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()

# Если есть Railway Volume, храним там. Иначе локально в ./data
railway_mount_path = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")
if railway_mount_path:
    DATA_DIR = Path(railway_mount_path) / "event_ai_data"
else:
    DATA_DIR = Path("data")

DATA_DIR.mkdir(parents=True, exist_ok=True)

SUBMISSIONS_FILE = DATA_DIR / "submissions.json"


class QuestionnaireSubmission(BaseModel):
    eventType: str
    clientName: str
    secondName: Optional[str] = ""
    phone: str
    eventDate: str
    city: str
    venue: Optional[str] = ""
    guestCount: Optional[str] = ""
    guestAge: Optional[str] = ""
    guestComposition: Optional[str] = ""

    eventGoal: Optional[str] = ""
    desiredAtmosphere: Optional[str] = ""
    idealImpression: Optional[str] = ""
    mustHaveMoments: Optional[str] = ""
    forbiddenTopics: Optional[str] = ""
    fears: Optional[str] = ""

    mainHeroes: Optional[str] = ""
    personalityTraits: Optional[str] = ""
    values: Optional[str] = ""
    importantStories: Optional[str] = ""
    internalJokes: Optional[str] = ""
    safeTopics: Optional[str] = ""
    tabooTopics: Optional[str] = ""

    hostStyle: Optional[str] = ""
    humorPreference: Optional[str] = ""
    tempoPreference: Optional[str] = ""
    interactionPreference: Optional[str] = ""
    touchingMoments: Optional[str] = ""
    modernVsClassic: Optional[str] = ""

    activeGuests: Optional[str] = ""
    shyGuests: Optional[str] = ""
    importantGuests: Optional[str] = ""
    conflictRisks: Optional[str] = ""
    childrenPresence: Optional[str] = ""
    whoNotToInvolve: Optional[str] = ""

    musicPreferences: Optional[str] = ""
    favoriteArtists: Optional[str] = ""
    bannedMusic: Optional[str] = ""
    danceBlockNeed: Optional[str] = ""
    ceremonyNeed: Optional[str] = ""
    surpriseNeed: Optional[str] = ""

    contestsNo: Optional[str] = ""
    sensitiveTopics: Optional[str] = ""
    culturalLimits: Optional[str] = ""
    logisticsLimits: Optional[str] = ""
    timingNotes: Optional[str] = ""
    hardNo: Optional[str] = ""

    finalWishes: Optional[str] = ""
    additionalDetails: Optional[str] = ""
    references: Optional[str] = ""


def load_submissions() -> list:
    if not SUBMISSIONS_FILE.exists():
        return []

    try:
        with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_submissions(submissions: list) -> None:
    with open(SUBMISSIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(submissions, file, ensure_ascii=False, indent=2)


def build_questionnaire_context(questionnaire: dict) -> str:
    labels = {
        "eventType": "Тип мероприятия",
        "clientName": "Имя клиента",
        "secondName": "Второй главный герой",
        "phone": "Телефон",
        "eventDate": "Дата мероприятия",
        "city": "Город",
        "venue": "Площадка",
        "guestCount": "Количество гостей",
        "guestAge": "Возраст гостей",
        "guestComposition": "Состав гостей",
        "eventGoal": "Главная цель мероприятия",
        "desiredAtmosphere": "Желаемая атмосфера",
        "idealImpression": "Какое впечатление должно остаться",
        "mustHaveMoments": "Обязательные моменты",
        "forbiddenTopics": "Что не должно появиться в программе",
        "fears": "Страхи и переживания",
        "mainHeroes": "Главные герои",
        "personalityTraits": "Черты характера",
        "values": "Ценности",
        "importantStories": "Важные истории",
        "internalJokes": "Внутренние шутки",
        "safeTopics": "Безопасные темы для юмора",
        "tabooTopics": "Табу-темы",
        "hostStyle": "Предпочтительный стиль ведущего",
        "humorPreference": "Отношение к юмору",
        "tempoPreference": "Предпочтительный темп",
        "interactionPreference": "Отношение к интерактивам",
        "touchingMoments": "Нужны ли трогательные моменты",
        "modernVsClassic": "Современность или классика",
        "activeGuests": "Активные гости",
        "shyGuests": "Скромные гости",
        "importantGuests": "Важные гости",
        "conflictRisks": "Риски и конфликтные моменты",
        "childrenPresence": "Дети на мероприятии",
        "whoNotToInvolve": "Кого нельзя вовлекать",
        "musicPreferences": "Музыкальные предпочтения",
        "favoriteArtists": "Любимые артисты",
        "bannedMusic": "Нежелательная музыка",
        "danceBlockNeed": "Нужен ли танцевальный блок",
        "ceremonyNeed": "Церемонии и официальные блоки",
        "surpriseNeed": "Сюрпризы",
        "contestsNo": "Нежелательные конкурсы и приемы",
        "sensitiveTopics": "Чувствительные темы",
        "culturalLimits": "Культурные и личные ограничения",
        "logisticsLimits": "Логистические ограничения",
        "timingNotes": "Замечания по таймингу",
        "hardNo": "Жесткое нет",
        "finalWishes": "Финальные пожелания",
        "additionalDetails": "Дополнительные детали",
        "references": "Референсы и ориентиры",
    }

    lines = []
    for key, value in questionnaire.items():
        if isinstance(value, str) and value.strip():
            label = labels.get(key, key)
            lines.append(f"{label}: {value.strip()}")

    return "\n".join(lines)


def try_parse_json(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = content[start:end + 1]
            return json.loads(cleaned)
        raise


def generate_ai_program(questionnaire: dict) -> dict:
    context = build_questionnaire_context(questionnaire)

    system_prompt = """
Ты — профессиональный сценарист, режиссер мероприятия и помощник ведущего.
Работаешь только на русском языке.
Ты создаешь не обзор анкеты, а рабочий документ для ведущего.

Главные принципы:
- не пересказывай анкету
- не делай статистику ответов
- не пиши воду
- не пиши слишком общие советы
- не делай шаблонный текст
- не предлагай пошлые, унизительные или устаревшие конкурсы
- не используй рискованный юмор
- если информации мало, строй аккуратные и безопасные решения

Ответ возвращай строго в JSON по структуре:
{
  "event_brief": {
    "format": "",
    "city": "",
    "venue": "",
    "date": "",
    "atmosphere": "",
    "main_goal": "",
    "key_moments": [],
    "hard_limits": [],
    "timing_anchor": ""
  },
  "director_concept": {
    "idea": "",
    "emotional_arc": "",
    "host_role": "",
    "main_impression_for_guests": ""
  },
  "red_flags": [
    {
      "risk": "",
      "why_it_matters": "",
      "how_to_handle": ""
    }
  ],
  "audience_map": {
    "core_audience": "",
    "active_guests": [],
    "shy_guests": [],
    "important_guests": [],
    "guests_not_to_involve": [],
    "children_notes": ""
  },
  "timeline_plan": [
    {
      "block_title": "",
      "block_goal": "",
      "approx_duration": "",
      "what_happens": "",
      "host_task": "",
      "transition_to_next": ""
    }
  ],
  "host_lines": {
    "opening_main": "",
    "opening_short": "",
    "intro_first_dance": "",
    "intro_family_block": "",
    "intro_surprise_block": "",
    "intro_cake": "",
    "closing_lines": ""
  },
  "interactive_blocks": [
    {
      "title": "",
      "goal": "",
      "best_moment": "",
      "how_to_run": "",
      "why_it_is_safe": ""
    }
  ],
  "humor_bank": [
    {
      "line": "",
      "tone": "",
      "where_to_use": "",
      "safety_note": ""
    }
  ],
  "plan_b": [
    {
      "situation": "",
      "response": ""
    }
  ],
  "final_strategy": {
    "how_to_lead_this_event": "",
    "what_to_avoid": "",
    "what_will_make_this_event_strong": ""
  },
  "print_version": {
    "title": "",
    "event_summary": "",
    "key_people": [],
    "must_do_blocks": [],
    "do_not_do": [],
    "short_timeline": [],
    "host_focus_points": []
  }
}
"""

    user_prompt = f"""
Ниже анкета клиента.
Преврати ее в рабочий документ для ведущего, а не в обзор ответов.

Вот анкета клиента:

{context}

Ответ только в JSON.
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return try_parse_json(response.output_text)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Event AI backend is running",
        "data_path": str(SUBMISSIONS_FILE),
        "using_railway_volume": bool(railway_mount_path),
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/submissions")
def get_submissions():
    submissions = load_submissions()
    return {
        "status": "success",
        "count": len(submissions),
        "items": submissions
    }


@app.post("/api/questionnaire")
def submit_questionnaire(payload: QuestionnaireSubmission):
    submission_data = payload.model_dump()

    record = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "created_at": datetime.now().isoformat(),
        "questionnaire": submission_data,
    }

    submissions = load_submissions()
    submissions.append(record)
    save_submissions(submissions)

    return {
        "status": "success",
        "message": "Анкета успешно получена",
        "clientName": payload.clientName,
        "eventType": payload.eventType,
        "savedId": record["id"]
    }


@app.get("/api/submissions/{submission_id}")
def get_submission_by_id(submission_id: str):
    submissions = load_submissions()
    found_item = next((item for item in submissions if item["id"] == submission_id), None)

    if not found_item:
        raise HTTPException(status_code=404, detail="Анкета не найдена")

    return {
        "status": "success",
        "item": found_item
    }


@app.post("/api/submissions/{submission_id}/generate-program")
def generate_program(submission_id: str):
    submissions = load_submissions()
    found_item = next((item for item in submissions if item["id"] == submission_id), None)

    if not found_item:
        raise HTTPException(status_code=404, detail="Анкета не найдена")

    try:
        program = generate_ai_program(found_item["questionnaire"])
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации программы: {error}")

    return {
        "status": "success",
        "submissionId": submission_id,
        "program": program
    }