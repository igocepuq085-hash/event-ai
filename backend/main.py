from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import json
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

app = FastAPI(title="Event AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://frontend-production-c187.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

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
            return json.load(file)
    except json.JSONDecodeError:
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
    print("1. Начали собирать контекст анкеты")
    context = build_questionnaire_context(questionnaire)
    print("2. Контекст собран, отправляем запрос в OpenAI")

    system_prompt = """
Ты — сильный event-стратег, сценарист, режиссер программы и помощник профессионального ведущего.
Работаешь только на русском языке.
Твоя задача — создавать внутренний рабочий документ только для ведущего.
Ты не пишешь текст для клиента.
Ты не должен быть шаблонным.
Ты должен мыслить как человек, который реально готовит сильное мероприятие.

Требования к результату:
- максимальная практичность
- живая, современная, профессиональная подача
- без воды
- без пошлости
- без кринжа
- без устаревших конкурсов
- без унижения гостей
- учитывать ограничения, риски, состав гостей, атмосферу и стиль ведущего
- если данных мало, не выдумывай лишнего, а аккуратно работай с тем, что есть

Нужно вернуть строго JSON со следующей структурой:
{
  "summary": "содержательное резюме события для ведущего",
  "audience": "разбор аудитории и как с ней работать",
  "risks": [
    "риск 1",
    "риск 2",
    "риск 3",
    "риск 4"
  ],
  "opening": "готовый вариант красивого открытия вечера",
  "program_blocks": [
    {
      "title": "название блока",
      "goal": "цель блока",
      "host_action": "что делает ведущий",
      "notes": "тон, настроение, важные нюансы"
    },
    {
      "title": "название блока",
      "goal": "цель блока",
      "host_action": "что делает ведущий",
      "notes": "тон, настроение, важные нюансы"
    },
    {
      "title": "название блока",
      "goal": "цель блока",
      "host_action": "что делает ведущий",
      "notes": "тон, настроение, важные нюансы"
    },
    {
      "title": "название блока",
      "goal": "цель блока",
      "host_action": "что делает ведущий",
      "notes": "тон, настроение, важные нюансы"
    },
    {
      "title": "название блока",
      "goal": "цель блока",
      "host_action": "что делает ведущий",
      "notes": "тон, настроение, важные нюансы"
    },
    {
      "title": "название блока",
      "goal": "цель блока",
      "host_action": "что делает ведущий",
      "notes": "тон, настроение, важные нюансы"
    }
  ],
  "jokes": [
    "шутка или легкая ироничная подводка 1",
    "шутка или легкая ироничная подводка 2",
    "шутка или легкая ироничная подводка 3"
  ],
  "interactives": [
    "идея интерактива 1",
    "идея интерактива 2",
    "идея интерактива 3"
  ],
  "recommendations": [
    "рекомендация 1",
    "рекомендация 2",
    "рекомендация 3",
    "рекомендация 4",
    "рекомендация 5",
    "рекомендация 6"
  ],
  "final_strategy": "главная стратегия ведения этого вечера"
}
"""

    user_prompt = f"""
Вот анкета клиента:

{context}

На основе этих данных сформируй для ведущего:
1. Краткое, но глубокое резюме события.
2. Разбор аудитории.
3. Ключевые риски.
4. Красивое открытие вечера.
5. Полную структуру программы из 6 блоков.
6. 3 уместные мягкие шутки или ироничные персональные подводки.
7. 3 уместные интерактива.
8. Практические рекомендации ведущему.
9. Финальную стратегию ведения.

Важно:
- не быть общим
- не быть банальным
- не писать воду
- если информации мало, делать аккуратные выводы на основе имеющегося
- ответ только в JSON
"""

    try:
        response = client.responses.create(
            model="gpt-5.4-mini",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        print("3. Ответ от OpenAI получен")
        content = response.output_text
        print("4. Разбираем JSON")
        result = try_parse_json(content)
        print("5. JSON успешно разобран")
        return result
    except Exception as error:
        print("Ошибка внутри generate_ai_program:", error)
        raise


@app.get("/")
def root():
    return {"status": "ok", "message": "Event AI backend is running"}


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

    print("Получена анкета:")
    print(submission_data)

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
        print("Ошибка генерации программы:", error)
        raise HTTPException(status_code=500, detail=f"Ошибка генерации программы: {error}")

    return {
        "status": "success",
        "submissionId": submission_id,
        "program": program
    }