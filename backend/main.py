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

# Для более сильной агентной логики лучше держать полноценную reasoning-модель.
AI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
TREND_MODEL = os.getenv("OPENAI_TREND_MODEL", "gpt-5")

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
            cleaned = content[start : end + 1]
            return json.loads(cleaned)
        raise


def call_model_json(
    system_prompt: str,
    user_prompt: str,
    *,
    model: Optional[str] = None,
    enable_web_search: bool = False,
) -> dict:
    kwargs = {
        "model": model or AI_MODEL,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    # Web search в Responses API включается через tools.
    if enable_web_search:
        kwargs["tools"] = [{"type": "web_search"}]

    response = client.responses.create(**kwargs)
    return try_parse_json(response.output_text)


def get_current_event_trends(event_type: str, questionnaire_context: str) -> dict:
    today_str = datetime.now().strftime("%Y-%m-%d")

    trend_system = """
Ты — тренд-аналитик event-индустрии.
Твоя задача: через web search собрать только актуальные, реально полезные тренды на текущую дату для конкретного типа мероприятия.

Правила:
- обязательно используй web search
- работай только с актуальными трендами на сегодня
- не тащи случайные идеи, которые невозможно применить ведущему на практике
- особенно смотри:
  1. тренды по свадебной/корпоративной/event-драматургии
  2. тренды по вовлечению гостей
  3. тренды по тону ведения и стилю речи
  4. тренды по музыкальным решениям и DJ-логике
  5. что уже считается устаревшим
- вывод нужен без ссылок и без цитат внутри JSON
- нужен прикладной, рабочий результат для ведущего мероприятий

Верни строго JSON:
{
  "trend_summary": "",
  "current_trends": [],
  "outdated_patterns_to_avoid": [],
  "guest_engagement_trends": [],
  "music_and_dj_trends": [],
  "script_style_trends": [],
  "how_to_apply_to_this_case": []
}
"""

    trend_user = f"""
Текущая дата: {today_str}
Тип мероприятия: {event_type}

Контекст анкеты:
{questionnaire_context}

Нужны тренды именно на текущую дату и именно в прикладной event-логике.
Верни только JSON.
"""

    return call_model_json(
        trend_system,
        trend_user,
        model=TREND_MODEL,
        enable_web_search=True,
    )


def generate_agent_program(questionnaire: dict) -> dict:
    context = build_questionnaire_context(questionnaire)
    event_type = questionnaire.get("eventType", "").strip().lower()

    # 1. Аналитик
    analyst_system = """
Ты — аналитик event-проекта.
Твоя задача: на основе анкеты вытащить только полезные факты для построения реального сценария.

Правила:
- не пиши обзор
- не пиши воду
- только факты, ограничения, риски, эмоциональные опоры, материалы для речи ведущего
- если есть тайминговый якорь вроде "торт в 22:00", обязательно выделяй его как базу для построения расчетного сценария
- обязательно выделяй особенности именно для данного типа мероприятия: свадьба, корпоратив, день рождения, частный праздник

Верни строго JSON:
{
  "event_profile": {
    "event_type": "",
    "format_name": "",
    "city": "",
    "venue": "",
    "event_date": "",
    "main_goal": "",
    "desired_atmosphere": "",
    "preferred_host_style": "",
    "tempo": "",
    "interaction_mode": "",
    "modern_vs_classic": ""
  },
  "hard_requirements": [],
  "hard_bans": [],
  "mandatory_moments": [],
  "timing_anchors": [],
  "story_material": {
    "core_story": "",
    "personal_details": [],
    "emotional_points": [],
    "usable_safe_jokes": [],
    "taboo_topics": []
  },
  "audience": {
    "core_audience": "",
    "active_guests": [],
    "shy_guests": [],
    "important_guests": [],
    "do_not_involve": [],
    "children_notes": ""
  },
  "music": {
    "preferences": "",
    "favorite_artists": [],
    "banned_music": [],
    "dance_blocks_requested": ""
  },
  "risk_map": [
    {
      "risk": "",
      "why": ""
    }
  ],
  "missing_but_inferable": {
    "start_time_assumption": "",
    "timeline_strategy": ""
  }
}
"""

    analyst_user = f"""
Вот анкета клиента:

{context}

Верни только JSON.
"""
    analyst_result = call_model_json(analyst_system, analyst_user)

    # 2. Тренды через web search
    trend_result = get_current_event_trends(event_type, context)

    # 3. Сценарист
    writer_system = """
Ты — сильный сценарист мероприятий.
Твоя задача: построить первый подробный сценарный черновик на основе анкеты, аналитики и актуальных трендов.

Главный приоритет:
- это уже почти готовый рабочий сценарий
- он должен быть по типу мероприятия: свадьба отдельно, корпоратив отдельно, остальные события отдельно
- тайминг должен быть расчетным и практичным
- каждый блок должен содержать полноценную режиссерскую логику
- текст ведущего должен быть развернутым
- стиль ведущего должен быть ОБРАЗНЫМ, МЕТАФОРИЧНЫМ, чуть художественным
- допустимо даже чуть переборщить с метафорами, если текст остается произносимым и красивым

Критические требования:
- если у блока ведущий должен говорить 3-5 минут, текст должен быть действительно длинным, как реальная речь
- host_text внутри таймлайна пиши полноценным, пригодным для чтения и адаптации
- ведущий должен не только комментировать, а управлять залом словом
- в речи должно быть больше образов, сравнений, атмосферных формул
- учитывай актуальные тренды на текущую дату
- dj_task не должен быть общим: пиши конкретно, что включать, как заходить, что делать по динамике
- отделяй работу ведущего, диджея и зала
- каждый блок должен ощущаться режиссерски

Для свадьбы особенно важно:
- драматургия семьи
- история пары
- ритуалы
- пики эмоций
- танцевальные волны
- красивый финал

Верни строго JSON:
{
  "concept": {
    "big_idea": "",
    "tone": "",
    "main_emotional_result": "",
    "why_this_event_will_be_memorable": ""
  },
  "director_axis": {
    "wave_1": "",
    "wave_2": "",
    "wave_3": "",
    "wave_4": ""
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
    "first_toast_intro": "",
    "first_dance_intro": "",
    "family_block_intro": "",
    "surprise_intro": "",
    "dance_block_intro": "",
    "cake_intro": "",
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
    "cake_music": "",
    "final_music": "",
    "stop_list": [],
    "technical_notes": []
  }
}
"""

    writer_user = f"""
Тип мероприятия: {event_type}

Анкета клиента:
{context}

Аналитика:
{json.dumps(analyst_result, ensure_ascii=False, indent=2)}

Актуальные тренды:
{json.dumps(trend_result, ensure_ascii=False, indent=2)}

Верни только JSON.
"""
    writer_result = call_model_json(writer_system, writer_user)

    # 4. Режиссер
    director_system = """
Ты — режиссер события.
Твоя задача: критично проверить сценарный черновик с точки зрения постановки, ритма, кульминаций и сценической логики.

Правила:
- ищи слабые места
- отмечай провалы ритма
- отмечай слабые переходы
- отмечай недостаток режиссерских ходов
- отмечай, где ведущему не хватает действия или дыхания сцены
- особенно проверяй, не слишком ли короткие тексты ведущего
- особенно проверяй, достаточно ли музыкально конкретны задачи диджея
- если тексты короткие и не тянут на реальную речь, считай это серьезным недостатком
- проверь, интегрированы ли актуальные тренды, а не просто перечислены

Верни строго JSON:
{
  "verdict": "",
  "strengths": [],
  "weaknesses": [],
  "timeline_fixes": [],
  "direction_fixes": [],
  "dj_fixes": [],
  "host_text_fixes": [],
  "trend_integration_fixes": [],
  "must_improve_before_final": []
}
"""

    director_user = f"""
Анкета:
{context}

Аналитика:
{json.dumps(analyst_result, ensure_ascii=False, indent=2)}

Тренды:
{json.dumps(trend_result, ensure_ascii=False, indent=2)}

Черновик сценариста:
{json.dumps(writer_result, ensure_ascii=False, indent=2)}

Верни только JSON.
"""
    director_result = call_model_json(director_system, director_user)

    # 5. Критик
    critic_system = """
Ты — жесткий, но профессиональный критик event-продукта.
Твоя задача: проверить, действительно ли сценарий полезен ведущему в работе.

Ищи:
- банальности
- пустые места
- советы вместо продукта
- слабый юмор
- плохую конкретику
- отсутствие пошагового действия
- слабую работу для диджея
- короткие тексты, которые нельзя реально читать в зале
- слишком общий плейлист без трековой конкретики
- слабую режиссуру
- невыразительный финал
- недостаток образности и авторского стиля ведущего
- если метафоры слабы — укажи это
- если тренды не встроены в сценарий — укажи это

Верни строго JSON:
{
  "verdict": "",
  "what_is_too_generic": [],
  "what_is_not_practical_enough": [],
  "what_is_weak_for_host": [],
  "what_is_weak_for_dj": [],
  "what_is_weak_in_style": [],
  "what_is_risky": [],
  "must_fix_now": [],
  "final_readiness_score": 0
}
"""

    critic_user = f"""
Анкета:
{context}

Аналитика:
{json.dumps(analyst_result, ensure_ascii=False, indent=2)}

Тренды:
{json.dumps(trend_result, ensure_ascii=False, indent=2)}

Черновик сценариста:
{json.dumps(writer_result, ensure_ascii=False, indent=2)}

Замечания режиссера:
{json.dumps(director_result, ensure_ascii=False, indent=2)}

Верни только JSON.
"""
    critic_result = call_model_json(critic_system, critic_user)

    # 6. Финальная сборка
    final_system = """
Ты — главный редактор итогового сценария мероприятия.
Твоя задача: собрать финальную, готовую к работе программу для ведущего.

Ты должен взять:
- анкету клиента
- аналитику
- актуальные тренды текущей даты
- черновик сценариста
- правки режиссера
- замечания критика

И выдать ГОТОВЫЙ ПРОДУКТ:
- не обзор
- не советы
- не методичку
- а реальный рабочий сценарий мероприятия

Это очень важно:
- результат должен быть пригоден для реальной работы ведущего
- блоки должны идти как пошаговое действие
- тайминг должен быть расчетным и практичным
- тексты ведущего должны быть длинными и читаемыми
- если речь в блоке ощущается как 3–5 минут, напиши длинный текст
- стиль ведущего должен быть метафорическим, образным, живым
- можно чуть переборщить с метафорами, но речь должна оставаться произносимой
- рекомендации диджею должны быть конкретными, с трековой логикой, примерами треков и связок
- свадьбы, корпоративы и другие мероприятия должны ощущаться по-разному
- тренды текущей даты должны быть не отдельной болтовней, а встроенной логикой сценария
- внутренние роли сценарист, режиссер и критик уже договорились между собой — в финале нужен только сильный итог

Формат работы с музыкой:
- допустимо рекомендовать конкретные известные треки и артистов как ориентиры
- для каждого музыкального блока пиши не только настроение, но и примеры 5-10 треков/ориентиров или трековых связок
- стоп-лист должен быть конкретным
- технические заметки должны быть прикладными

Формат работы с речью ведущего:
- opening_main и closing_words должны быть длиннее обычного
- host_text в сценарных блоках должен быть действительно полезным
- допускается писать вариативно, но текст должен быть плотным
- не надо бояться длины, если длина делает документ рабочим
- в речи должны быть: образ, метафора, интонационный рисунок, смена температуры

Правила качества:
- никаких пустых общих фраз
- юмор только безопасный
- все должно быть применимо на площадке
- нельзя повторять грубые формулировки клиента буквально, если это небезопасно
- если нет точного времени старта, но есть якорь, построй реалистичную расчетную сетку и укажи, что это рабочий расчет
- не делай все блоки одинаковыми по объему: ключевые блоки должны быть развернуты сильнее
- добавь отдельный блок с ключевыми командами ведущему
- добавь отдельный блок с тем, что нужно уточнить у клиента до мероприятия, если в анкете есть пробелы

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
    "first_toast_intro": "",
    "first_dance_intro": "",
    "family_block_intro": "",
    "surprise_intro": "",
    "dance_block_intro": "",
    "cake_intro": "",
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
    "cake_music": "",
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

    final_user = f"""
Тип мероприятия: {event_type}

Анкета:
{context}

Аналитика:
{json.dumps(analyst_result, ensure_ascii=False, indent=2)}

Актуальные тренды:
{json.dumps(trend_result, ensure_ascii=False, indent=2)}

Черновик сценариста:
{json.dumps(writer_result, ensure_ascii=False, indent=2)}

Правки режиссера:
{json.dumps(director_result, ensure_ascii=False, indent=2)}

Замечания критика:
{json.dumps(critic_result, ensure_ascii=False, indent=2)}

Собери финальный рабочий сценарий.
Верни только JSON.
"""
    final_result = call_model_json(final_system, final_user)

    return final_result


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
        value = questionnaire.get(key, "")
        add_label_value(document, label, value)

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
    add_heading(document, "2.4. Актуальные тренды, встроенные в сценарий", level=2)
    add_label_value(document, "Краткое резюме", trend_layer.get("trend_summary", ""))
    document.add_paragraph("Что применено:")
    add_list(document, trend_layer.get("applied_trends", []))
    document.add_paragraph("Что сознательно отброшено как устаревшее:")
    add_list(document, trend_layer.get("rejected_outdated_patterns", []))

    add_heading(document, "2.5. Ключевые команды ведущему", level=2)
    add_list(document, program.get("key_host_commands", []))

    add_heading(document, "2.6. Что уточнить у клиента до мероприятия", level=2)
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
    add_label_value(document, "Подводка к первому тосту", host_script.get("first_toast_intro", ""))
    add_label_value(document, "Подводка к первому танцу", host_script.get("first_dance_intro", ""))
    add_label_value(document, "Подводка к семейному блоку", host_script.get("family_block_intro", ""))
    add_label_value(document, "Подводка к сюрпризу", host_script.get("surprise_intro", ""))
    add_label_value(document, "Подводка к танцевальному блоку", host_script.get("dance_block_intro", ""))
    add_label_value(document, "Подводка к торту", host_script.get("cake_intro", ""))
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
    add_label_value(document, "Музыка на торт", dj_guidance.get("cake_music", ""))
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
        "trend_model": TREND_MODEL,
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