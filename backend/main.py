from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from io import BytesIO
import json
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI
from docx import Document


load_dotenv()

app = FastAPI(title="Event AI Backend")

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


def get_questionnaire_labels() -> dict:
    return {
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


def safe_filename(value: str) -> str:
    translit_map = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
        "е": "e", "ё": "e", "ж": "zh", "з": "z", "и": "i",
        "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
        "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
        "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch",
        "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "",
        "э": "e", "ю": "yu", "я": "ya",
    }

    value = value.strip().lower()
    result = []

    for char in value:
        lower_char = char.lower()
        if lower_char in translit_map:
            result.append(translit_map[lower_char])
        elif char.isalnum():
            result.append(char)
        elif char in [" ", "-", "_"]:
            result.append("_")

    cleaned = "".join(result)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")

    return cleaned or "anketa"


def add_heading(document: Document, text: str, level: int = 1) -> None:
    document.add_heading(text, level=level)


def add_label_value(document: Document, label: str, value: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.add_run(f"{label}: ").bold = True
    paragraph.add_run(value if value else "Не указано")


def add_list(document: Document, items: list[str]) -> None:
    if not items:
        document.add_paragraph("Не указано")
        return

    for item in items:
        document.add_paragraph(item, style="List Bullet")


def build_docx(submission: dict, program: dict) -> BytesIO:
    questionnaire = submission["questionnaire"]
    labels = get_questionnaire_labels()

    document = Document()
    document.add_heading("Анкета мероприятия и рабочая программа ведущего", 0)

    add_label_value(document, "ID заявки", submission["id"])
    add_label_value(document, "Создано", submission["created_at"])

    add_heading(document, "1. Анкета клиента", level=1)
    for key, label in labels.items():
        value = questionnaire.get(key, "")
        add_label_value(document, label, value)

    add_heading(document, "2. Рабочая программа ведущего", level=1)

    event_brief = program.get("event_brief", {})
    add_heading(document, "2.1. Бриф события", level=2)
    add_label_value(document, "Формат", event_brief.get("format", ""))
    add_label_value(document, "Город", event_brief.get("city", ""))
    add_label_value(document, "Площадка", event_brief.get("venue", ""))
    add_label_value(document, "Дата", event_brief.get("date", ""))
    add_label_value(document, "Атмосфера", event_brief.get("atmosphere", ""))
    add_label_value(document, "Главная цель", event_brief.get("main_goal", ""))
    add_label_value(document, "Тайминговый якорь", event_brief.get("timing_anchor", ""))
    document.add_paragraph("Ключевые моменты:")
    add_list(document, event_brief.get("key_moments", []))
    document.add_paragraph("Жесткие ограничения:")
    add_list(document, event_brief.get("hard_limits", []))

    director_concept = program.get("director_concept", {})
    add_heading(document, "2.2. Режиссерская идея", level=2)
    add_label_value(document, "Идея", director_concept.get("idea", ""))
    add_label_value(document, "Эмоциональная дуга", director_concept.get("emotional_arc", ""))
    add_label_value(document, "Роль ведущего", director_concept.get("host_role", ""))
    add_label_value(
        document,
        "Какое впечатление должны унести гости",
        director_concept.get("main_impression_for_guests", ""),
    )

    add_heading(document, "2.3. Красные флаги", level=2)
    red_flags = program.get("red_flags", [])
    if red_flags:
        for index, item in enumerate(red_flags, start=1):
            document.add_paragraph(f"{index}. {item.get('risk', 'Риск')}")
            add_label_value(document, "Почему важно", item.get("why_it_matters", ""))
            add_label_value(document, "Как отработать", item.get("how_to_handle", ""))
    else:
        document.add_paragraph("Не указано")

    audience_map = program.get("audience_map", {})
    add_heading(document, "2.4. Карта аудитории", level=2)
    add_label_value(document, "Ядро аудитории", audience_map.get("core_audience", ""))
    add_label_value(document, "Дети", audience_map.get("children_notes", ""))
    document.add_paragraph("Активные гости:")
    add_list(document, audience_map.get("active_guests", []))
    document.add_paragraph("Скромные гости:")
    add_list(document, audience_map.get("shy_guests", []))
    document.add_paragraph("Важные гости:")
    add_list(document, audience_map.get("important_guests", []))
    document.add_paragraph("Кого не вовлекать:")
    add_list(document, audience_map.get("guests_not_to_involve", []))

    add_heading(document, "2.5. План вечера", level=2)
    timeline_plan = program.get("timeline_plan", [])
    if timeline_plan:
        for index, block in enumerate(timeline_plan, start=1):
            document.add_paragraph(f"{index}. {block.get('block_title', 'Блок')}")
            add_label_value(document, "Цель", block.get("block_goal", ""))
            add_label_value(document, "Примерная длительность", block.get("approx_duration", ""))
            add_label_value(document, "Что происходит", block.get("what_happens", ""))
            add_label_value(document, "Задача ведущего", block.get("host_task", ""))
            add_label_value(document, "Переход дальше", block.get("transition_to_next", ""))
    else:
        document.add_paragraph("Не указано")

    host_lines = program.get("host_lines", {})
    add_heading(document, "2.6. Реплики ведущего", level=2)
    add_label_value(document, "Основное открытие", host_lines.get("opening_main", ""))
    add_label_value(document, "Короткое открытие", host_lines.get("opening_short", ""))
    add_label_value(document, "Подводка к первому танцу", host_lines.get("intro_first_dance", ""))
    add_label_value(document, "Подводка к семейному блоку", host_lines.get("intro_family_block", ""))
    add_label_value(document, "Подводка к сюрпризу", host_lines.get("intro_surprise_block", ""))
    add_label_value(document, "Подводка к торту", host_lines.get("intro_cake", ""))
    add_label_value(document, "Финальные слова", host_lines.get("closing_lines", ""))

    add_heading(document, "2.7. Интерактивы", level=2)
    interactive_blocks = program.get("interactive_blocks", [])
    if interactive_blocks:
        for index, item in enumerate(interactive_blocks, start=1):
            document.add_paragraph(f"{index}. {item.get('title', 'Интерактив')}")
            add_label_value(document, "Цель", item.get("goal", ""))
            add_label_value(document, "Когда лучше", item.get("best_moment", ""))
            add_label_value(document, "Как провести", item.get("how_to_run", ""))
            add_label_value(document, "Почему безопасно", item.get("why_it_is_safe", ""))
    else:
        document.add_paragraph("Не указано")

    add_heading(document, "2.8. Банк мягкого юмора", level=2)
    humor_bank = program.get("humor_bank", [])
    if humor_bank:
        for index, item in enumerate(humor_bank, start=1):
            document.add_paragraph(f"{index}. {item.get('line', 'Шутка')}")
            add_label_value(document, "Тон", item.get("tone", ""))
            add_label_value(document, "Где использовать", item.get("where_to_use", ""))
            add_label_value(document, "Примечание по безопасности", item.get("safety_note", ""))
    else:
        document.add_paragraph("Не указано")

    add_heading(document, "2.9. План Б", level=2)
    plan_b = program.get("plan_b", [])
    if plan_b:
        for index, item in enumerate(plan_b, start=1):
            document.add_paragraph(f"{index}. {item.get('situation', 'Ситуация')}")
            add_label_value(document, "Что делать", item.get("response", ""))
    else:
        document.add_paragraph("Не указано")

    final_strategy = program.get("final_strategy", {})
    add_heading(document, "2.10. Финальная стратегия", level=2)
    add_label_value(document, "Как вести этот вечер", final_strategy.get("how_to_lead_this_event", ""))
    add_label_value(document, "Чего избегать", final_strategy.get("what_to_avoid", ""))
    add_label_value(
        document,
        "Что сделает вечер сильным",
        final_strategy.get("what_will_make_this_event_strong", ""),
    )

    print_version = program.get("print_version", {})
    add_heading(document, "2.11. Краткая печатная версия", level=2)
    add_label_value(document, "Название", print_version.get("title", ""))
    add_label_value(document, "Краткое резюме", print_version.get("event_summary", ""))
    document.add_paragraph("Ключевые люди:")
    add_list(document, print_version.get("key_people", []))
    document.add_paragraph("Обязательные блоки:")
    add_list(document, print_version.get("must_do_blocks", []))
    document.add_paragraph("Нельзя делать:")
    add_list(document, print_version.get("do_not_do", []))
    document.add_paragraph("Короткий таймлайн:")
    add_list(document, print_version.get("short_timeline", []))
    document.add_paragraph("Фокус ведущего:")
    add_list(document, print_version.get("host_focus_points", []))

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer


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


@app.get("/api/submissions/{submission_id}/export-docx")
def export_docx(submission_id: str):
    submissions = load_submissions()
    found_item = next((item for item in submissions if item["id"] == submission_id), None)

    if not found_item:
        raise HTTPException(status_code=404, detail="Анкета не найдена")

    try:
        program = generate_ai_program(found_item["questionnaire"])
        file_buffer = build_docx(found_item, program)

        client_name = safe_filename(found_item["questionnaire"].get("clientName", "anketa"))
        event_type = safe_filename(found_item["questionnaire"].get("eventType", "event"))
        filename = f"{event_type}_{client_name}_{submission_id}.docx"

        return StreamingResponse(
            file_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Ошибка выгрузки Word: {error}")