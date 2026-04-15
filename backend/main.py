from __future__ import annotations

import json
import os
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator
from docx import Document

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


load_dotenv()

SUPPORTED_EVENT_TYPES = {"wedding", "jubilee"}
AI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000")
RAILWAY_VOLUME_MOUNT_PATH = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "").strip()

DATA_DIR = (
    Path(RAILWAY_VOLUME_MOUNT_PATH) / "event_ai_data"
    if RAILWAY_VOLUME_MOUNT_PATH
    else Path(__file__).resolve().parent / "data"
)
DATA_DIR.mkdir(parents=True, exist_ok=True)
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"

client = OpenAI(api_key=OPENAI_API_KEY) if OpenAI and OPENAI_API_KEY else None

app = FastAPI(title="Event AI Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in FRONTEND_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionnaireSubmission(BaseModel):
    eventType: str
    clientName: str = Field(min_length=1)
    phone: str = ""
    eventDate: str = Field(min_length=1)
    city: str = Field(min_length=1)
    venue: str = Field(min_length=1)
    startTime: str = Field(default="")
    guestCount: str = ""
    childrenInfo: str = ""
    atmosphere: str = ""
    fears: str = ""
    hostWishes: str = ""
    references: str = ""
    musicLikes: str = ""
    musicBans: str = ""

    groomName: str = ""
    brideName: str = ""
    weddingTraditions: str = ""
    groomParents: str = ""
    brideParents: str = ""
    grandparents: str = ""
    loveStory: str = ""
    coupleValues: str = ""
    importantDates: str = ""
    proposalStory: str = ""
    nicknames: str = ""
    insideJokes: str = ""
    guestsList: str = ""
    conflictTopics: str = ""
    likedFormats: str = ""
    keyMoments: str = ""

    celebrantName: str = ""
    celebrantAge: str = ""
    familyMembers: str = ""
    anniversaryAtmosphere: str = ""
    biographyStory: str = ""
    achievements: str = ""
    lifeStages: str = ""
    characterTraits: str = ""
    funnyFacts: str = ""
    importantGuests: str = ""
    jubileeConflictTopics: str = ""
    jubileeLikedFormats: str = ""
    whatCannotBeDone: str = ""

    @model_validator(mode="after")
    def validate_business_rules(self) -> "QuestionnaireSubmission":
        if self.eventType not in SUPPORTED_EVENT_TYPES:
            raise ValueError("Поддерживаются только wedding и jubilee")
        if not self.startTime.strip():
            raise ValueError("Поле startTime обязательно")
        if self.eventType == "wedding" and (not self.groomName.strip() or not self.brideName.strip()):
            raise ValueError("Для wedding обязательны groomName и brideName")
        if self.eventType == "jubilee" and not self.celebrantName.strip():
            raise ValueError("Для jubilee обязательно celebrantName")
        return self


def load_submissions() -> list[dict[str, Any]]:
    if not SUBMISSIONS_FILE.exists():
        return []
    try:
        return json.loads(SUBMISSIONS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def save_submissions(submissions: list[dict[str, Any]]) -> None:
    SUBMISSIONS_FILE.write_text(
        json.dumps(submissions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_questionnaire_labels() -> dict[str, str]:
    return {
        "eventType": "Тип мероприятия",
        "clientName": "Название заявки",
        "phone": "Телефон",
        "eventDate": "Дата события",
        "city": "Город",
        "venue": "Площадка / ресторан",
        "startTime": "Время начала / сбор гостей",
        "guestCount": "Количество гостей",
        "childrenInfo": "Будут ли дети",
        "atmosphere": "Атмосфера",
        "fears": "Страхи и переживания",
        "hostWishes": "Пожелания к ведущему",
        "references": "Референсы по стилю вечера",
        "musicLikes": "Какая музыка нравится",
        "musicBans": "Что из музыки нельзя включать",
        "groomName": "Имя жениха",
        "brideName": "Имя невесты",
        "weddingTraditions": "Какие свадебные традиции нужны",
        "groomParents": "Родители жениха",
        "brideParents": "Родители невесты",
        "grandparents": "Бабушки и дедушки",
        "loveStory": "История знакомства",
        "coupleValues": "Главные ценности пары",
        "importantDates": "Важные даты и события пары",
        "proposalStory": "История предложения",
        "nicknames": "Как ласково называют друг друга",
        "insideJokes": "Внутренние шутки / мемы",
        "guestsList": "Имена гостей и характеристики",
        "conflictTopics": "Конфликтные темы / чувствительные фигуры",
        "likedFormats": "Какие форматы нравятся",
        "keyMoments": "Какие 3-5 моментов самые важные",
        "celebrantName": "Имя юбиляра",
        "celebrantAge": "Возраст юбиляра",
        "familyMembers": "Семья юбиляра",
        "anniversaryAtmosphere": "Атмосфера юбилея",
        "biographyStory": "Истории из жизни",
        "achievements": "Важные достижения",
        "lifeStages": "Важные этапы жизни",
        "characterTraits": "Главные качества юбиляра",
        "funnyFacts": "Любимые фразы / шутки / мемы",
        "importantGuests": "Важные гости",
        "jubileeConflictTopics": "Конфликтные темы",
        "jubileeLikedFormats": "Какие форматы нравятся",
        "whatCannotBeDone": "Чего нельзя делать",
    }


def build_questionnaire_context(questionnaire: dict[str, Any]) -> str:
    labels = get_questionnaire_labels()
    lines: list[str] = []
    for key, label in labels.items():
        value = str(questionnaire.get(key, "")).strip()
        if value:
            lines.append(f"{label}: {value}")
    return "\n".join(lines)


def list_from_text(value: str, fallback: list[str]) -> list[str]:
    items = [item.strip(" -•\t") for item in re.split(r"[\n,;]+", value or "") if item.strip(" -•\t")]
    return items[:6] if items else fallback


def build_mock_program(questionnaire: dict[str, Any]) -> dict[str, Any]:
    event_type = questionnaire["eventType"]
    atmosphere = questionnaire.get("atmosphere") or questionnaire.get("anniversaryAtmosphere") or "теплая, живая, современная"
    main_person = (
        f"{questionnaire.get('groomName', '').strip()} и {questionnaire.get('brideName', '').strip()}".strip()
        if event_type == "wedding"
        else questionnaire.get("celebrantName", "").strip()
    )
    timing_anchor = questionnaire.get("startTime", "").strip() or "18:00"
    key_moments = list_from_text(
        questionnaire.get("keyMoments", ""),
        ["сильное открытие", "эмоциональный основной блок", "мягкий танцевальный разгон", "сильный финал"],
    )
    hard_bans = list_from_text(
        questionnaire.get("musicBans", "") + "\n" + questionnaire.get("whatCannotBeDone", ""),
        ["кринжовые конкурсы", "жесткий интерактив против воли гостей"],
    )
    sensitive_topics = list_from_text(
        questionnaire.get("conflictTopics", "") + "\n" + questionnaire.get("jubileeConflictTopics", ""),
        ["не выносить в центр зала чувствительные темы без согласования"],
    )

    return {
        "event_passport": {
            "event_type": event_type,
            "format_name": "Сценарий для ведущего Event AI",
            "city": questionnaire.get("city", ""),
            "venue": questionnaire.get("venue", ""),
            "event_date": questionnaire.get("eventDate", ""),
            "working_timeline_note": "Сценарий собран в быстром базовом режиме без OpenAI API.",
            "main_goal": "Провести живой, собранный и персонализированный вечер без просадок по ритму.",
            "atmosphere": atmosphere,
            "style": "современный, персональный, режиссерски собранный",
            "mandatory_points": key_moments,
            "hard_bans": hard_bans,
            "timing_anchor": timing_anchor,
        },
        "quality_panel": {
            "scenario_verdict": "Рабочая базовая версия готова к адаптации под площадку.",
            "director_verdict": "Ритм построен от мягкого входа к сильному эмоциональному пику.",
            "critic_verdict": "Нужна живая донастройка после уточнения гостей и тайминга кухни.",
            "final_ready": True,
            "fixed_issues": [
                "Собран безопасный тайминг без токсичных и устаревших механик.",
                "Учтены запреты и чувствительные темы из анкеты.",
            ],
        },
        "concept": {
            "big_idea": f"Вечер про людей, ради которых собираются рядом с {main_person}.",
            "main_director_thesis": "Не форсировать шум, а постепенно раскрывать зал через личные смыслы и точный музыкальный ритм.",
            "main_emotional_result": "Гости чувствуют не набор активностей, а цельный вечер с характером.",
            "why_this_event_will_be_remembered": "Потому что в центре не шаблоны, а реальные люди, их история и правильный темп.",
        },
        "trend_layer": {
            "trend_summary": "Сценарий опирается на персонализацию, мягкое вовлечение и аккуратную музыкальную драматургию.",
            "applied_trends": [
                "минимум неловкого интерактива",
                "личные истории вместо штампов",
                "сильные, но короткие речевые заходы между блоками",
            ],
            "rejected_outdated_patterns": [
                "принудительные конкурсы",
                "шаблонные тосты без привязки к героям вечера",
            ],
        },
        "key_host_commands": [
            "С первых минут задать спокойную уверенную тональность и не спешить с разгоном.",
            "Главных героев вечера держать в центре, но не перегружать обязательными выходами.",
            "С чувствительными темами работать только через заранее согласованные формулировки.",
            "Не жертвовать эмоциональным ядром ради случайного интерактива.",
        ],
        "questions_to_clarify_before_event": [
            "Есть ли точный тайминг подачи горячего и торта?",
            "Нужны ли официальные поздравления по списку и в каком порядке?",
            "Есть ли сюрпризы от гостей, которые надо встроить в программу?",
        ],
        "director_logic": {
            "opening_logic": "Вход в вечер через теплое знакомство с залом и аккуратную сборку внимания.",
            "development_logic": "Чередование общения, смысловых точек и музыкальных волн без провисаний.",
            "family_or_core_emotional_logic": "Самый личный блок ставится в момент, когда зал уже доверяет ведущему и готов слушать.",
            "final_logic": "Финал собирает всех в одном эмоциональном фокусе и оставляет ощущение завершенности.",
        },
        "scenario_timeline": [
            {
                "time_from": timing_anchor,
                "time_to": "18:20",
                "block_title": "Сбор гостей и мягкий welcome",
                "block_purpose": "Снять напряжение и собрать зал в единое поле внимания.",
                "what_happens": "Гости заходят, музыка работает фоном, ведущий мягко приветствует ключевых людей.",
                "host_action": "Следить за входом, называть людей по имени, не форсировать шум.",
                "host_text": f"Сегодня мы собираемся не просто отметить дату, а бережно сложить вечер вокруг истории {main_person}. Пусть у каждого будет время оглядеться, почувствовать атмосферу и войти в этот ритм без спешки.",
                "dj_task": "Держать теплый, современный фон без резких переходов и лишней громкости.",
                "director_move": "Сначала доверие, потом динамика.",
                "risk_control": "Не перегружать старт микрофоном, если гости еще рассаживаются.",
                "transition": "Когда большинство в зале, переводим внимание к официальному открытию.",
            },
            {
                "time_from": "18:20",
                "time_to": "18:40",
                "block_title": "Открытие вечера",
                "block_purpose": "Обозначить характер вечера и правила тональности.",
                "what_happens": "Ведущий собирает внимание, обозначает героя вечера и маршрут программы.",
                "host_action": "Говорить ярко, но без пафоса, задать ритм и уважительную энергетику.",
                "host_text": "У хорошего вечера всегда есть свой пульс. Не тот, что шумит ради шума, а тот, который держит людей рядом. Сегодня мы будем двигаться именно так: с юмором, с теплом, с точностью к важным моментам и без всего лишнего.",
                "dj_task": "Подложка на открытие, затем аккуратный уход под речь.",
                "director_move": "Сформировать доверие к ведущему и интерес к следующему блоку.",
                "risk_control": "Если зал шумный, начать с короткой версии открытия и добрать внимание позже.",
                "transition": "После открытия переводим зал к первому содержательному блоку.",
            },
            {
                "time_from": "18:40",
                "time_to": "19:20",
                "block_title": "Первый ключевой смысловой блок",
                "block_purpose": "Дать вечеру личную глубину через историю и близких людей.",
                "what_happens": "Подводка к главным людям, первые тосты или важные слова, эмоциональная сборка зала.",
                "host_action": "Держать темп, не растягивать длинные выходы, бережно работать с эмоциями.",
                "host_text": f"У каждого по-настоящему важного вечера есть внутренний свет. Он появляется не от декора и не от громкости колонок, а от людей, которые знают, каким {main_person} бывает вне праздничной картинки. И именно им сейчас хочется дать слово.",
                "dj_task": "Поддержать эмоциональные выходы мягкими инструментальными подложками.",
                "director_move": "Углубить контакт зала с историей события.",
                "risk_control": "Следить, чтобы эмоциональный блок не ушел в затяжную официальность.",
                "transition": "После теплой глубины вывести вечер в более живое, но не резкое движение.",
            },
            {
                "time_from": "19:20",
                "time_to": "20:00",
                "block_title": "Интерактив и вовлечение без кринжа",
                "block_purpose": "Вовлечь гостей мягко и персонально, не разрушая достоинство вечера.",
                "what_happens": "Короткий интерактив по гостям, историям, ассоциациям или заранее собранным фактам.",
                "host_action": "Поднимать только уместных людей и не вытаскивать тех, кому некомфортно.",
                "host_text": "Иногда лучший способ оживить зал это не заставить его что-то делать, а точно поймать людей в их живых реакциях. Поэтому сейчас работаем не по шаблону, а по тем людям, которые уже сами задают настроение.",
                "dj_task": "Короткие музыкальные отбивки, без клоунады и резких мемных вставок.",
                "director_move": "Поднять энергию и не потерять вкус.",
                "risk_control": f"Не вовлекать темы: {', '.join(sensitive_topics)}.",
                "transition": "После разгона логично вывести гостей в танец или гастрономическую паузу.",
            },
            {
                "time_from": "20:00",
                "time_to": "21:00",
                "block_title": "Танцевальная волна и второй пик",
                "block_purpose": "Переключить вечер из общения в телесную, живую энергию.",
                "what_happens": "Танцевальный блок, затем короткая остановка под следующий смысловой заход.",
                "host_action": "Запускать танец короткими командами и не мешать музыке работать.",
                "host_text": "Есть моменты, которые не нужно объяснять словами. Их нужно просто вовремя отпустить в музыку. Поэтому сейчас вечер перестает сидеть за столами и начинает дышать шире.",
                "dj_task": "Построить волну от знакомого комфортного ритма к более яркому танцевальному ядру.",
                "director_move": "Дать телу зала движение, не потеряв управляемость.",
                "risk_control": "Если танцпол не идет, начать с хитов средней энергии и знакомого грува.",
                "transition": "На пике энергии вернуть внимание к финальному смысловому блоку.",
            },
            {
                "time_from": "21:00",
                "time_to": "21:30",
                "block_title": "Финал",
                "block_purpose": "Собрать вечер в понятную эмоциональную точку.",
                "what_happens": "Финальные слова, важный общий момент, завершение программы.",
                "host_action": "Говорить точнее и теплее, чем в начале, без формальной торжественности.",
                "host_text": "Хороший вечер заканчивается не тогда, когда выключают музыку. Он заканчивается тогда, когда каждый уносит с собой чувство, что был сегодня не зрителем, а частью чего-то настоящего. Именно это важно сохранить сейчас.",
                "dj_task": "Подложить финальную композицию и аккуратно собрать зал в общий жест.",
                "director_move": "Не пересластить, а завершить чисто и по-человечески.",
                "risk_control": "Не растягивать финал, если гости уже устали.",
                "transition": "После официального финала возможен свободный хвост вечера.",
            },
        ],
        "host_script": {
            "opening_main": "Добрый вечер. Сегодня здесь собрались люди, которые умеют превращать дату в память, а встречу в историю. И если у этого вечера есть главная задача, то она не в том, чтобы просто красиво пройти по таймингу, а в том, чтобы сделать каждую важную точку живой и настоящей.",
            "opening_short": "Добрый вечер. Начинаем спокойно, красиво и по-настоящему про вас.",
            "welcome_line": "Пусть этот вечер с первых минут будет не шумным, а своим.",
            "first_core_intro": "Прежде чем разгоняться дальше, важно дать место тем словам, на которых вообще держится атмосфера таких вечеров.",
            "family_block_intro": "Есть люди, рядом с которыми любая история становится глубже. И именно им сейчас хочется уступить центр внимания.",
            "surprise_intro": "Следующий момент не про эффект ради эффекта, а про то самое тепло, которое остается после праздника дольше всего.",
            "dance_block_intro": "А теперь вечеру пора менять походку. Из красивого разговора переходим в живую энергию зала.",
            "final_block_intro": "Перед тем как отпустить этот вечер дальше, хочется собрать его в одну ясную мысль.",
            "closing_words": "Спасибо за доверие, за внимание друг к другу и за ту атмосферу, которую невозможно заказать отдельно. Ее создают только люди.",
        },
        "dj_guidance": {
            "overall_music_policy": "Двигаться от комфортного современного welcome к более яркой энергии, не ломая эмоциональные сцены резкими включениями.",
            "welcome_music": "Nu-disco, light pop, soft funk, спокойные русские и международные треки без навязчивого вокального давления.",
            "opening_music": "Короткий кинематографичный заход, затем чистый уход под микрофон.",
            "table_background": "Негромкий groove, soul-pop, lounge-pop, мягкий funk.",
            "emotional_blocks_music": "Инструментальные версии, piano / strings / atmospheric pads.",
            "dance_block_1": "Знакомые хиты средней энергии, чтобы безопасно поднять танцпол.",
            "dance_block_2": "Основной пик: современные поп-хиты, disco edits, singalong без кринжа.",
            "dance_block_3": "Финальный легкий добор с учетом возраста и состава гостей.",
            "final_block_music": "Теплая, объединяющая композиция без агрессивного бита.",
            "final_music": "Трек на общее чувство завершения, а не на максимальную громкость.",
            "stop_list": hard_bans,
            "technical_notes": [
                "Не перебивать микрофон подводками и мемными джинглами.",
                "На эмоциональных блоках держать запас по громкости.",
                "Перед танцем дать ведущему 5-7 секунд чистого входа.",
            ],
        },
        "guest_management": {
            "active_people": ["Поднимать первыми самых открытых и поддерживающих атмосферу гостей."],
            "shy_people": ["Не вытаскивать в центр без предварительного контакта и согласия."],
            "important_people": ["Родные, ключевые друзья, гости с особыми смысловыми ролями."],
            "do_not_involve": sensitive_topics,
            "sensitive_people_or_topics": sensitive_topics,
            "management_notes": [
                "Следить за балансом внимания между главными героями и гостями.",
                "Не превращать персональные истории в публичный допрос.",
            ],
        },
        "risk_map": [
            {
                "risk": "Провал по динамике в первой трети вечера",
                "why_it_matters": "Если старт вялый, зал позже сложнее собрать в единый ритм.",
                "how_to_prevent": "Короткое открытие, быстрый переход к людям и первым живым реакциям.",
                "what_to_do_if_triggered": "Срезать длинные речи и раньше выводить вечер в музыкальный или интерактивный блок.",
            },
            {
                "risk": "Неудачное касание чувствительных тем",
                "why_it_matters": "Это может резко испортить доверие к ведущему.",
                "how_to_prevent": "Держать стоп-лист под рукой и заранее согласовать формулировки.",
                "what_to_do_if_triggered": "Быстро увести фокус на нейтральный теплый блок без самооправданий со сцены.",
            },
        ],
        "plan_b": [
            {
                "situation": "Гости долго рассаживаются",
                "solution": "Продлить welcome, сократить первое официальное открытие и сместить основной смысловой блок на 10-15 минут.",
            },
            {
                "situation": "Танцпол не включается с первого захода",
                "solution": "Начать с более узнаваемых и комфортных треков, добавить короткий речевой подогрев и повторный заход через 7-10 минут.",
            },
        ],
        "final_print_version": {
            "title": f"Краткий план {event_type}",
            "summary": "Собранный, современный вечер с упором на персонализацию, ритм и уважение к гостям.",
            "timeline_short": [
                f"{timing_anchor} welcome",
                "открытие",
                "ключевой смысловой блок",
                "мягкое вовлечение",
                "танцевальная волна",
                "финал",
            ],
            "must_do": [
                "держать темп",
                "работать через личные смыслы",
                "согласовать важные выходы заранее",
            ],
            "must_not_do": hard_bans,
            "host_focus": [
                "доверие зала",
                "точность формулировок",
                "бережный контроль энергии",
            ],
            "dj_focus": [
                "мягкие переходы",
                "поддержка смысловых блоков",
                "безопасный разгон танцпола",
            ],
        },
    }


def build_system_prompt() -> str:
    return """
Ты создаешь рабочую режиссерскую программу для ведущего.
Работаешь только с типами wedding и jubilee.
Нельзя возвращать обзор анкеты, советы без структуры, кринжовые конкурсы, токсичный юмор и шаблонные банальности.
Нужно вернуть строго JSON с ключами:
event_passport, quality_panel, concept, trend_layer, key_host_commands,
questions_to_clarify_before_event, director_logic, scenario_timeline,
host_script, dj_guidance, guest_management, risk_map, plan_b, final_print_version.
Каждый блок должен быть прикладным и пригодным для реальной работы ведущего и диджея.
"""


def generate_agent_program(questionnaire: dict[str, Any]) -> dict[str, Any]:
    if client is None:
        return build_mock_program(questionnaire)

    try:
        response = client.responses.create(
            model=AI_MODEL,
            reasoning={"effort": "low"},
            input=[
                {"role": "system", "content": build_system_prompt()},
                {
                    "role": "user",
                    "content": (
                        f"Тип мероприятия: {questionnaire['eventType']}\n\n"
                        "Анкета:\n"
                        f"{build_questionnaire_context(questionnaire)}\n\n"
                        "Верни только валидный JSON."
                    ),
                },
            ],
        )
        raw_text = response.output_text.strip()
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            start = raw_text.find("{")
            end = raw_text.rfind("}")
            if start == -1 or end == -1:
                raise RuntimeError("OpenAI вернул невалидный JSON")
            return json.loads(raw_text[start : end + 1])
    except Exception:
        return build_mock_program(questionnaire)


def safe_filename(value: str) -> str:
    translit_map = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch", "ы": "y",
        "э": "e", "ю": "yu", "я": "ya", "ь": "", "ъ": "",
    }
    value = value.strip().lower()
    result: list[str] = []
    for char in value:
        if char in translit_map:
            result.append(translit_map[char])
        elif char.isalnum():
            result.append(char)
        elif char in {" ", "-", "_"}:
            result.append("_")
    return re.sub(r"_+", "_", "".join(result)).strip("_") or "event_ai"


def add_label_value(document: Document, label: str, value: Any) -> None:
    paragraph = document.add_paragraph()
    paragraph.add_run(f"{label}: ").bold = True
    paragraph.add_run(str(value).strip() if str(value).strip() else "Не указано")


def add_list(document: Document, items: list[Any]) -> None:
    if not items:
        document.add_paragraph("Не указано")
        return
    for item in items:
        document.add_paragraph(str(item), style="List Bullet")


def build_docx(submission: dict[str, Any], program: dict[str, Any]) -> BytesIO:
    questionnaire = submission["questionnaire"]
    labels = get_questionnaire_labels()

    document = Document()
    document.add_heading("Event AI: анкета и программа ведущего", 0)
    add_label_value(document, "ID заявки", submission["id"])
    add_label_value(document, "Создано", submission["created_at"])

    document.add_heading("1. Анкета клиента", level=1)
    for key, label in labels.items():
        add_label_value(document, label, questionnaire.get(key, ""))

    document.add_heading("2. Сценарий", level=1)

    passport = program.get("event_passport", {})
    document.add_heading("2.1 Паспорт события", level=2)
    for field, title in [
        ("event_type", "Тип"),
        ("format_name", "Формат"),
        ("city", "Город"),
        ("venue", "Площадка"),
        ("event_date", "Дата"),
        ("working_timeline_note", "Примечание по таймингу"),
        ("main_goal", "Главная цель"),
        ("atmosphere", "Атмосфера"),
        ("style", "Стиль"),
        ("timing_anchor", "Тайминговый якорь"),
    ]:
        add_label_value(document, title, passport.get(field, ""))
    document.add_paragraph("Обязательные точки:")
    add_list(document, passport.get("mandatory_points", []))
    document.add_paragraph("Жесткие запреты:")
    add_list(document, passport.get("hard_bans", []))

    quality = program.get("quality_panel", {})
    document.add_heading("2.2 Проверка качества", level=2)
    add_label_value(document, "Вердикт сценариста", quality.get("scenario_verdict", ""))
    add_label_value(document, "Вердикт режиссера", quality.get("director_verdict", ""))
    add_label_value(document, "Вердикт критика", quality.get("critic_verdict", ""))
    add_label_value(document, "Готово к работе", "Да" if quality.get("final_ready") else "Нет")
    document.add_paragraph("Исправленные слабые места:")
    add_list(document, quality.get("fixed_issues", []))

    concept = program.get("concept", {})
    document.add_heading("2.3 Концепция", level=2)
    for field, title in [
        ("big_idea", "Большая идея"),
        ("main_director_thesis", "Главный режиссерский тезис"),
        ("main_emotional_result", "Эмоциональный результат"),
        ("why_this_event_will_be_remembered", "Почему вечер запомнится"),
    ]:
        add_label_value(document, title, concept.get(field, ""))

    document.add_heading("2.4 Команды ведущему", level=2)
    add_list(document, program.get("key_host_commands", []))

    document.add_heading("2.5 Что уточнить", level=2)
    add_list(document, program.get("questions_to_clarify_before_event", []))

    logic = program.get("director_logic", {})
    document.add_heading("2.6 Режиссерская логика", level=2)
    for field, title in [
        ("opening_logic", "Логика открытия"),
        ("development_logic", "Логика развития"),
        ("family_or_core_emotional_logic", "Логика эмоционального ядра"),
        ("final_logic", "Логика финала"),
    ]:
        add_label_value(document, title, logic.get(field, ""))

    document.add_heading("2.7 Тайминг", level=2)
    for index, block in enumerate(program.get("scenario_timeline", []), start=1):
        document.add_paragraph(f"{index}. {block.get('time_from', '')} - {block.get('time_to', '')}: {block.get('block_title', '')}")
        for field, title in [
            ("block_purpose", "Цель"),
            ("what_happens", "Что происходит"),
            ("host_action", "Действие ведущего"),
            ("host_text", "Текст ведущего"),
            ("dj_task", "Задача диджея"),
            ("director_move", "Режиссерский ход"),
            ("risk_control", "Контроль риска"),
            ("transition", "Переход"),
        ]:
            add_label_value(document, title, block.get(field, ""))

    script = program.get("host_script", {})
    document.add_heading("2.8 Тексты ведущего", level=2)
    for field, title in [
        ("opening_main", "Основное открытие"),
        ("opening_short", "Короткое открытие"),
        ("welcome_line", "Welcome line"),
        ("first_core_intro", "Подводка к первому ключевому блоку"),
        ("family_block_intro", "Подводка к семейному блоку"),
        ("surprise_intro", "Подводка к сюрпризу"),
        ("dance_block_intro", "Подводка к танцевальному блоку"),
        ("final_block_intro", "Подводка к финалу"),
        ("closing_words", "Финальные слова"),
    ]:
        add_label_value(document, title, script.get(field, ""))

    dj = program.get("dj_guidance", {})
    document.add_heading("2.9 DJ guidance", level=2)
    for field, title in [
        ("overall_music_policy", "Общая музыкальная логика"),
        ("welcome_music", "Welcome music"),
        ("opening_music", "Opening music"),
        ("table_background", "Table background"),
        ("emotional_blocks_music", "Emotional blocks"),
        ("dance_block_1", "Dance block 1"),
        ("dance_block_2", "Dance block 2"),
        ("dance_block_3", "Dance block 3"),
        ("final_block_music", "Final block"),
        ("final_music", "Final music"),
    ]:
        add_label_value(document, title, dj.get(field, ""))
    document.add_paragraph("Stop list:")
    add_list(document, dj.get("stop_list", []))
    document.add_paragraph("Technical notes:")
    add_list(document, dj.get("technical_notes", []))

    guest_management = program.get("guest_management", {})
    document.add_heading("2.10 Работа с гостями", level=2)
    for field, title in [
        ("active_people", "Активные люди"),
        ("shy_people", "Скромные люди"),
        ("important_people", "Важные люди"),
        ("do_not_involve", "Кого не вовлекать"),
        ("sensitive_people_or_topics", "Чувствительные темы"),
        ("management_notes", "Заметки по управлению"),
    ]:
        document.add_paragraph(f"{title}:")
        add_list(document, guest_management.get(field, []))

    document.add_heading("2.11 Риски", level=2)
    for item in program.get("risk_map", []):
        add_label_value(document, "Риск", item.get("risk", ""))
        add_label_value(document, "Почему важно", item.get("why_it_matters", ""))
        add_label_value(document, "Как предотвратить", item.get("how_to_prevent", ""))
        add_label_value(document, "Если сработало", item.get("what_to_do_if_triggered", ""))

    document.add_heading("2.12 План Б", level=2)
    for item in program.get("plan_b", []):
        add_label_value(document, "Ситуация", item.get("situation", ""))
        add_label_value(document, "Решение", item.get("solution", ""))

    final_print = program.get("final_print_version", {})
    document.add_heading("2.13 Краткая версия", level=2)
    add_label_value(document, "Название", final_print.get("title", ""))
    add_label_value(document, "Краткое резюме", final_print.get("summary", ""))
    for field, title in [
        ("timeline_short", "Короткий таймлайн"),
        ("must_do", "Обязательно сделать"),
        ("must_not_do", "Нельзя делать"),
        ("host_focus", "Фокус ведущего"),
        ("dj_focus", "Фокус диджея"),
    ]:
        document.add_paragraph(f"{title}:")
        add_list(document, final_print.get(field, []))

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer


def get_submission_or_404(submission_id: str) -> tuple[list[dict[str, Any]], int]:
    submissions = load_submissions()
    for index, submission in enumerate(submissions):
        if submission["id"] == submission_id:
            return submissions, index
    raise HTTPException(status_code=404, detail="Анкета не найдена")


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "status": "ok",
        "message": "Event AI backend is running",
        "data_path": str(SUBMISSIONS_FILE),
        "using_railway_volume": bool(RAILWAY_VOLUME_MOUNT_PATH),
        "model": AI_MODEL,
        "openai_enabled": bool(client),
        "supported_event_types": sorted(SUPPORTED_EVENT_TYPES),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/api/questionnaire")
def submit_questionnaire(payload: QuestionnaireSubmission) -> dict[str, Any]:
    submission = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "created_at": datetime.now().isoformat(),
        "questionnaire": payload.model_dump(),
    }
    submissions = load_submissions()
    submissions.append(submission)
    save_submissions(submissions)
    return {
        "status": "success",
        "message": "Анкета сохранена",
        "clientName": payload.clientName,
        "eventType": payload.eventType,
        "savedId": submission["id"],
    }


@app.get("/api/submissions")
def get_submissions() -> dict[str, Any]:
    submissions = load_submissions()
    return {"status": "success", "count": len(submissions), "items": submissions}


@app.get("/api/submissions/{submission_id}")
def get_submission(submission_id: str) -> dict[str, Any]:
    submissions, index = get_submission_or_404(submission_id)
    return {"status": "success", "item": submissions[index]}


@app.post("/api/submissions/{submission_id}/generate-program")
def generate_program(submission_id: str) -> dict[str, Any]:
    submissions, index = get_submission_or_404(submission_id)
    submission = submissions[index]
    if isinstance(submission.get("program"), dict):
        return {
            "status": "success",
            "submissionId": submission_id,
            "program": submission["program"],
            "cached": True,
        }

    try:
        program = generate_agent_program(submission["questionnaire"])
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации программы: {error}") from error

    submissions[index]["program"] = program
    save_submissions(submissions)
    return {"status": "success", "submissionId": submission_id, "program": program, "cached": False}


@app.get("/api/submissions/{submission_id}/export-docx")
def export_docx(submission_id: str) -> StreamingResponse:
    submissions, index = get_submission_or_404(submission_id)
    submission = submissions[index]
    program = submission.get("program")
    if not isinstance(program, dict):
        program = generate_agent_program(submission["questionnaire"])
        submissions[index]["program"] = program
        save_submissions(submissions)

    buffer = build_docx(submission, program)
    client_name = safe_filename(submission["questionnaire"].get("clientName", "client"))
    event_type = safe_filename(submission["questionnaire"].get("eventType", "event"))
    filename = f"{event_type}_{client_name}_{submission_id}.docx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'},
    )
