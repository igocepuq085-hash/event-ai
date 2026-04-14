from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from io import BytesIO
from datetime import datetime
import json
import os
import re

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
AI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

railway_mount_path = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")
if railway_mount_path:
    DATA_DIR = Path(railway_mount_path) / "event_ai_data"
else:
    DATA_DIR = Path("data")

DATA_DIR.mkdir(parents=True, exist_ok=True)
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"


class QuestionnaireSubmission(BaseModel):
    eventType: str  # wedding | jubilee

    # common
    clientName: str
    phone: str
    eventDate: str
    city: str
    venue: str
    startTime: Optional[str] = ""
    guestCount: Optional[str] = ""
    childrenInfo: Optional[str] = ""
    atmosphere: Optional[str] = ""
    fears: Optional[str] = ""
    hostWishes: Optional[str] = ""
    references: Optional[str] = ""
    musicLikes: Optional[str] = ""
    musicBans: Optional[str] = ""

    # wedding
    groomName: Optional[str] = ""
    brideName: Optional[str] = ""
    weddingTraditions: Optional[str] = ""
    groomParents: Optional[str] = ""
    brideParents: Optional[str] = ""
    grandparents: Optional[str] = ""
    loveStory: Optional[str] = ""
    coupleValues: Optional[str] = ""
    importantDates: Optional[str] = ""
    proposalStory: Optional[str] = ""
    nicknames: Optional[str] = ""
    insideJokes: Optional[str] = ""
    guestsList: Optional[str] = ""
    conflictTopics: Optional[str] = ""
    likedFormats: Optional[str] = ""

    # jubilee
    celebrantName: Optional[str] = ""
    celebrantAge: Optional[str] = ""
    familyMembers: Optional[str] = ""
    anniversaryAtmosphere: Optional[str] = ""
    keyMoments: Optional[str] = ""
    biographyStory: Optional[str] = ""
    achievements: Optional[str] = ""
    lifeStages: Optional[str] = ""
    characterTraits: Optional[str] = ""
    funnyFacts: Optional[str] = ""
    importantGuests: Optional[str] = ""
    jubileeConflictTopics: Optional[str] = ""
    jubileeLikedFormats: Optional[str] = ""
    whatCannotBeDone: Optional[str] = ""


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


def get_questionnaire_labels() -> dict:
    return {
        "eventType": "Тип мероприятия",
        "clientName": "Название заявки",
        "phone": "Телефон",
        "eventDate": "Дата события",
        "city": "Город",
        "venue": "Площадка",
        "startTime": "Время начала / сбор гостей",
        "guestCount": "Количество гостей",
        "childrenInfo": "Дети",
        "atmosphere": "Атмосфера",
        "fears": "Страхи и переживания",
        "hostWishes": "Пожелания к ведущему",
        "references": "Референсы и ориентиры",
        "musicLikes": "Любимая музыка",
        "musicBans": "Что нельзя включать",

        "groomName": "Имя жениха",
        "brideName": "Имя невесты",
        "weddingTraditions": "Свадебные традиции",
        "groomParents": "Родители жениха",
        "brideParents": "Родители невесты",
        "grandparents": "Бабушки и дедушки",
        "loveStory": "История знакомства",
        "coupleValues": "Ценности пары",
        "importantDates": "Важные даты и события",
        "proposalStory": "История предложения",
        "nicknames": "Ласковые имена",
        "insideJokes": "Внутренние шутки",
        "guestsList": "Список гостей и описания",
        "conflictTopics": "Конфликтные темы или чувствительные фигуры",
        "likedFormats": "Нравящиеся конкурсы / форматы",

        "celebrantName": "Имя юбиляра",
        "celebrantAge": "Возраст юбиляра",
        "familyMembers": "Семья юбиляра",
        "anniversaryAtmosphere": "Атмосфера юбилея",
        "keyMoments": "Обязательные моменты юбилея",
        "biographyStory": "История юбиляра",
        "achievements": "Достижения и чем гордятся",
        "lifeStages": "Важные этапы жизни",
        "characterTraits": "Характер и особенности юбиляра",
        "funnyFacts": "Смешные факты / любимые фразы",
        "importantGuests": "Важные гости",
        "jubileeConflictTopics": "Чувствительные темы на юбилее",
        "jubileeLikedFormats": "Нравящиеся форматы на юбилее",
        "whatCannotBeDone": "Чего нельзя делать на юбилее",
    }


def build_questionnaire_context(questionnaire: dict) -> str:
    labels = get_questionnaire_labels()
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


def generate_agent_program(questionnaire: dict) -> dict:
    context = build_questionnaire_context(questionnaire)
    event_type = questionnaire.get("eventType", "").strip().lower()

    system_prompt = """
Ты — сильный event-стратег, сценарист ведущих, режиссер мероприятий и редактор финального документа.
Работаешь только с двумя типами мероприятий:
- wedding
- jubilee

Твоя задача: на основе анкеты сразу собрать ГОТОВЫЙ рабочий документ ведущего.

Это не обзор анкеты.
Это не список советов.
Это не черновые заметки.

Это должен быть готовый продукт для работы ведущего.

Критические требования:
- только один цельный сильный результат
- никакой воды
- никакой банальности
- никакой пустой красивости
- текст должен быть полезен в реальном зале
- стиль ведущего должен быть образным, метафоричным, живым
- можно немного переборщить с метафорами, если речь звучит красиво и сценично
- ведущий должен не комментировать, а вести зал словом
- ключевые блоки должны содержать длинный, пригодный для чтения текст
- если блок предполагает речь 3–5 минут, текст должен быть действительно длинным
- музыка должна быть описана конкретно
- диджей должен получить не абстракцию, а понятные треки, связки, логику заходов и стоп-лист
- wedding и jubilee должны ощущаться абсолютно по-разному
- нужно встроить современные подходы к ведению: персональность, режиссура, мягкое вовлечение, отказ от кринжовых форматов, музыкальная драматургия, ритмические волны
- НЕ упоминай поиск трендов, интернет или источники
- просто используй современную event-логику как часть финального решения

Что обязательно сделать:
1. выделить паспорт события
2. собрать ключевые команды ведущему
3. собрать вопросы, которые нужно уточнить до мероприятия, если данных не хватает
4. построить режиссерскую логику вечера
5. построить ПОШАГОВЫЙ ТАЙМИНГ
6. на каждый блок дать:
   - цель
   - что происходит
   - действие ведущего
   - длинный текст ведущего
   - задачу диджея
   - режиссерский ход
   - контроль риска
   - переход
7. дать отдельный блок текстов ведущего
8. дать отдельный блок рекомендаций диджею
9. дать работу с гостями
10. дать риски
11. дать план Б
12. дать краткую версию для печати

Правила безопасности и качества:
- нельзя использовать унизительные конкурсы
- нельзя предлагать рискованный или токсичный юмор
- нельзя повторять грубые формулировки клиента буквально, если они звучат опасно или обидно
- если нет времени старта, строй разумный рабочий расчет и честно это укажи
- если данных не хватает, не срывай сценарий, а строй лучший рабочий вариант и отдельно выноси уточнения
- не делай все блоки одинаковыми по длине
- самые важные блоки делай сильнее и длиннее

Верни строго JSON:
{
  "event_passport": {
    "event_type": "",
    "format_name": "",
    "city": "",
    "venue": "",
    "event_date": "",
    "working_timeline_note": "",
    "main_goal": "",
    "atmosphere": "",
    "style": "",
    "mandatory_points": [],
    "hard_bans": [],
    "timing_anchor": ""
  },
  "quality_panel": {
    "scenario_verdict": "",
    "director_verdict": "",
    "critic_verdict": "",
    "final_ready": true,
    "fixed_issues": []
  },
  "concept": {
    "big_idea": "",
    "main_director_thesis": "",
    "main_emotional_result": "",
    "why_this_event_will_be_remembered": ""
  },
  "trend_layer": {
    "trend_summary": "",
    "applied_trends": [],
    "rejected_outdated_patterns": []
  },
  "key_host_commands": [],
  "questions_to_clarify_before_event": [],
  "director_logic": {
    "opening_logic": "",
    "development_logic": "",
    "family_or_core_emotional_logic": "",
    "final_logic": ""
  },
  "scenario_timeline": [
    {
      "time_from": "",
      "time_to": "",
      "block_title": "",
      "block_purpose": "",
      "what_happens": "",
      "host_action": "",
      "host_text": "",
      "dj_task": "",
      "director_move": "",
      "risk_control": "",
      "transition": ""
    }
  ],
  "host_script": {
    "opening_main": "",
    "opening_short": "",
    "welcome_line": "",
    "first_core_intro": "",
    "family_block_intro": "",
    "surprise_intro": "",
    "dance_block_intro": "",
    "final_block_intro": "",
    "closing_words": ""
  },
  "dj_guidance": {
    "overall_music_policy": "",
    "welcome_music": "",
    "opening_music": "",
    "table_background": "",
    "emotional_blocks_music": "",
    "dance_block_1": "",
    "dance_block_2": "",
    "dance_block_3": "",
    "final_block_music": "",
    "final_music": "",
    "stop_list": [],
    "technical_notes": []
  },
  "guest_management": {
    "active_people": [],
    "shy_people": [],
    "important_people": [],
    "do_not_involve": [],
    "sensitive_people_or_topics": [],
    "management_notes": []
  },
  "risk_map": [
    {
      "risk": "",
      "why_it_matters": "",
      "how_to_prevent": "",
      "what_to_do_if_triggered": ""
    }
  ],
  "plan_b": [
    {
      "situation": "",
      "solution": ""
    }
  ],
  "final_print_version": {
    "title": "",
    "summary": "",
    "timeline_short": [],
    "must_do": [],
    "must_not_do": [],
    "host_focus": [],
    "dj_focus": []
  }
}
"""

    user_prompt = f"""
Тип мероприятия: {event_type}

Анкета:
{context}

Собери финальный рабочий сценарий.
Верни только JSON.
"""

    response = client.responses.create(
        model=AI_MODEL,
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
    document.add_heading("Анкета мероприятия и режиссерская программа ведущего", 0)

    add_label_value(document, "ID заявки", submission["id"])
    add_label_value(document, "Создано", submission["created_at"])

    add_heading(document, "1. Анкета клиента", level=1)
    for key, label in labels.items():
      արժեք = questionnaire.get(key, "")
      add_label_value(document, label, արժեք)

    add_heading(document, "2. Готовый сценарий ведущего", level=1)

    passport = program.get("event_passport", {})
    add_heading(document, "2.1. Паспорт события", level=2)
    add_label_value(document, "Тип", passport.get("event_type", ""))
    add_label_value(document, "Формат", passport.get("format_name", ""))
    add_label_value(document, "Город", passport.get("city", ""))
    add_label_value(document, "Площадка", passport.get("venue", ""))
    add_label_value(document, "Дата", passport.get("event_date", ""))
    add_label_value(document, "Рабочая пометка по таймингу", passport.get("working_timeline_note", ""))
    add_label_value(document, "Главная цель", passport.get("main_goal", ""))
    add_label_value(document, "Атмосфера", passport.get("atmosphere", ""))
    add_label_value(document, "Стиль", passport.get("style", ""))
    add_label_value(document, "Тайминговый якорь", passport.get("timing_anchor", ""))
    document.add_paragraph("Обязательные точки:")
    add_list(document, passport.get("mandatory_points", []))
    document.add_paragraph("Жесткие запреты:")
    add_list(document, passport.get("hard_bans", []))

    quality_panel = program.get("quality_panel", {})
    add_heading(document, "2.2. Внутренняя проверка качества", level=2)
    add_label_value(document, "Вердикт сценариста", quality_panel.get("scenario_verdict", ""))
    add_label_value(document, "Вердикт режиссера", quality_panel.get("director_verdict", ""))
    add_label_value(document, "Вердикт критика", quality_panel.get("critic_verdict", ""))
    add_label_value(document, "Готово к работе", "Да" if quality_panel.get("final_ready", False) else "Нет")
    document.add_paragraph("Что было исправлено:")
    add_list(document, quality_panel.get("fixed_issues", []))

    concept = program.get("concept", {})
    add_heading(document, "2.3. Концепция", level=2)
    add_label_value(document, "Большая идея", concept.get("big_idea", ""))
    add_label_value(document, "Главный режиссерский тезис", concept.get("main_director_thesis", ""))
    add_label_value(document, "Главный эмоциональный результат", concept.get("main_emotional_result", ""))
    add_label_value(document, "Почему вечер запомнится", concept.get("why_this_event_will_be_remembered", ""))

    trend_layer = program.get("trend_layer", {})
    add_heading(document, "2.4. Современная логика сценария", level=2)
    add_label_value(document, "Краткое резюме", trend_layer.get("trend_summary", ""))
    document.add_paragraph("Что применено:")
    add_list(document, trend_layer.get("applied_trends", []))
    document.add_paragraph("Что отброшено как устаревшее:")
    add_list(document, trend_layer.get("rejected_outdated_patterns", []))

    add_heading(document, "2.5. Ключевые команды ведущему", level=2)
    add_list(document, program.get("key_host_commands", []))

    add_heading(document, "2.6. Что уточнить до мероприятия", level=2)
    add_list(document, program.get("questions_to_clarify_before_event", []))

    director_logic = program.get("director_logic", {})
    add_heading(document, "2.7. Режиссерская ось", level=2)
    add_label_value(document, "Логика открытия", director_logic.get("opening_logic", ""))
    add_label_value(document, "Логика развития", director_logic.get("development_logic", ""))
    add_label_value(document, "Логика эмоционального ядра", director_logic.get("family_or_core_emotional_logic", ""))
    add_label_value(document, "Логика финала", director_logic.get("final_logic", ""))

    add_heading(document, "2.8. Пошаговый тайминг", level=2)
    for index, block in enumerate(program.get("scenario_timeline", []), start=1):
        document.add_paragraph(
            f"{index}. {block.get('time_from', '')}–{block.get('time_to', '')} | {block.get('block_title', 'Блок')}"
        )
        add_label_value(document, "Цель", block.get("block_purpose", ""))
        add_label_value(document, "Что происходит", block.get("what_happens", ""))
        add_label_value(document, "Действие ведущего", block.get("host_action", ""))
        add_label_value(document, "Текст ведущего", block.get("host_text", ""))
        add_label_value(document, "Задача диджея", block.get("dj_task", ""))
        add_label_value(document, "Режиссерский ход", block.get("director_move", ""))
        add_label_value(document, "Контроль риска", block.get("risk_control", ""))
        add_label_value(document, "Переход", block.get("transition", ""))

    host_script = program.get("host_script", {})
    add_heading(document, "2.9. Тексты ведущего", level=2)
    add_label_value(document, "Основное открытие", host_script.get("opening_main", ""))
    add_label_value(document, "Короткое открытие", host_script.get("opening_short", ""))
    add_label_value(document, "Welcome-фраза", host_script.get("welcome_line", ""))
    add_label_value(document, "Подводка к первому ключевому блоку", host_script.get("first_core_intro", ""))
    add_label_value(document, "Подводка к семейному блоку", host_script.get("family_block_intro", ""))
    add_label_value(document, "Подводка к сюрпризу", host_script.get("surprise_intro", ""))
    add_label_value(document, "Подводка к танцевальному блоку", host_script.get("dance_block_intro", ""))
    add_label_value(document, "Подводка к финальному блоку", host_script.get("final_block_intro", ""))
    add_label_value(document, "Финальные слова", host_script.get("closing_words", ""))

    dj_guidance = program.get("dj_guidance", {})
    add_heading(document, "2.10. Рекомендации диджею", level=2)
    add_label_value(document, "Общая музыкальная политика", dj_guidance.get("overall_music_policy", ""))
    add_label_value(document, "Музыка на welcome", dj_guidance.get("welcome_music", ""))
    add_label_value(document, "Музыка на открытие", dj_guidance.get("opening_music", ""))
    add_label_value(document, "Музыка на застольный фон", dj_guidance.get("table_background", ""))
    add_label_value(document, "Музыка на эмоциональные блоки", dj_guidance.get("emotional_blocks_music", ""))
    add_label_value(document, "Танцевальный блок 1", dj_guidance.get("dance_block_1", ""))
    add_label_value(document, "Танцевальный блок 2", dj_guidance.get("dance_block_2", ""))
    add_label_value(document, "Танцевальный блок 3", dj_guidance.get("dance_block_3", ""))
    add_label_value(document, "Музыка на финальный блок", dj_guidance.get("final_block_music", ""))
    add_label_value(document, "Финальная музыка", dj_guidance.get("final_music", ""))
    document.add_paragraph("Стоп-лист:")
    add_list(document, dj_guidance.get("stop_list", []))
    document.add_paragraph("Технические заметки:")
    add_list(document, dj_guidance.get("technical_notes", []))

    guest_management = program.get("guest_management", {})
    add_heading(document, "2.11. Работа с гостями", level=2)
    document.add_paragraph("Активные люди:")
    add_list(document, guest_management.get("active_people", []))
    document.add_paragraph("Скромные люди:")
    add_list(document, guest_management.get("shy_people", []))
    document.add_paragraph("Важные люди:")
    add_list(document, guest_management.get("important_people", []))
    document.add_paragraph("Кого не вовлекать:")
    add_list(document, guest_management.get("do_not_involve", []))
    document.add_paragraph("Чувствительные люди и темы:")
    add_list(document, guest_management.get("sensitive_people_or_topics", []))
    document.add_paragraph("Управленческие заметки:")
    add_list(document, guest_management.get("management_notes", []))

    add_heading(document, "2.12. Риски", level=2)
    for index, risk in enumerate(program.get("risk_map", []), start=1):
        document.add_paragraph(f"{index}. {risk.get('risk', 'Риск')}")
        add_label_value(document, "Почему важно", risk.get("why_it_matters", ""))
        add_label_value(document, "Как предотвратить", risk.get("how_to_prevent", ""))
        add_label_value(document, "Что делать, если случилось", risk.get("what_to_do_if_triggered", ""))

    add_heading(document, "2.13. План Б", level=2)
    for index, item in enumerate(program.get("plan_b", []), start=1):
        document.add_paragraph(f"{index}. {item.get('situation', 'Ситуация')}")
        add_label_value(document, "Решение", item.get("solution", ""))

    final_print = program.get("final_print_version", {})
    add_heading(document, "2.14. Краткая версия для печати", level=2)
    add_label_value(document, "Название", final_print.get("title", ""))
    add_label_value(document, "Краткое резюме", final_print.get("summary", ""))
    document.add_paragraph("Короткий таймлайн:")
    add_list(document, final_print.get("timeline_short", []))
    document.add_paragraph("Обязательно сделать:")
    add_list(document, final_print.get("must_do", []))
    document.add_paragraph("Нельзя делать:")
    add_list(document, final_print.get("must_not_do", []))
    document.add_paragraph("Фокус ведущего:")
    add_list(document, final_print.get("host_focus", []))
    document.add_paragraph("Фокус диджея:")
    add_list(document, final_print.get("dj_focus", []))

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
        "model": AI_MODEL,
        "supported_event_types": ["wedding", "jubilee"],
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
    if payload.eventType not in ["wedding", "jubilee"]:
        raise HTTPException(status_code=400, detail="Поддерживаются только wedding и jubilee")

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
        program = generate_agent_program(found_item["questionnaire"])
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
        program = generate_agent_program(found_item["questionnaire"])
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