from __future__ import annotations

import json
import os
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from docx import Document
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


load_dotenv()

SUPPORTED_EVENT_TYPES = {"wedding", "jubilee"}
PROGRAM_SCHEMA_VERSION = 2
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

client = OpenAI(api_key=OPENAI_API_KEY, timeout=60.0) if OpenAI and OPENAI_API_KEY else None

app = FastAPI(title="Event AI Backend", version="1.1.0")
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
        data = json.loads(SUBMISSIONS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_submissions(submissions: list[dict[str, Any]]) -> None:
    SUBMISSIONS_FILE.write_text(json.dumps(submissions, ensure_ascii=False, indent=2), encoding="utf-8")


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
        "groomParents": "Как зовут родителей жениха",
        "brideParents": "Как зовут родителей невесты",
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
        "biographyStory": "Истории, которые можно использовать",
        "achievements": "Важные достижения",
        "lifeStages": "Важные этапы жизни",
        "characterTraits": "Главные качества юбиляра",
        "funnyFacts": "Любимые фразы / шутки / мемы",
        "importantGuests": "Важные гости",
        "jubileeConflictTopics": "Конфликтные темы / чувствительные фигуры",
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
    return items[:8] if items else fallback


def build_fallback_program(questionnaire: dict[str, Any]) -> dict[str, Any]:
    event_type = questionnaire["eventType"]
    is_wedding = event_type == "wedding"
    atmosphere = questionnaire.get("atmosphere") or questionnaire.get("anniversaryAtmosphere") or "теплая, живая, современная"
    timing_anchor = questionnaire.get("startTime", "").strip() or "18:00"
    city = questionnaire.get("city", "")
    venue = questionnaire.get("venue", "")
    event_date = questionnaire.get("eventDate", "")
    main_hero = (
        f"{questionnaire.get('groomName', '').strip()} и {questionnaire.get('brideName', '').strip()}".strip()
        if is_wedding
        else questionnaire.get("celebrantName", "").strip()
    )
    key_moments = list_from_text(
        questionnaire.get("keyMoments", ""),
        [
            "сильное открытие без затяжной официальности",
            "эмоциональное ядро вечера",
            "мягкое вовлечение гостей без кринжа",
            "танцевальная волна",
            "чистый, теплый финал",
        ],
    )
    hard_bans = list_from_text(
        questionnaire.get("musicBans", "") + "\n" + questionnaire.get("whatCannotBeDone", ""),
        ["кринжовые конкурсы", "токсичный юмор", "жесткое давление на гостей"],
    )
    sensitive_topics = list_from_text(
        questionnaire.get("conflictTopics", "") + "\n" + questionnaire.get("jubileeConflictTopics", ""),
        ["чувствительные темы без согласования"],
    )

    opening_main = (
        f"Добрый вечер. Сегодня зал собирается не ради формального праздника, а ради живой истории {main_hero}. "
        "Хороший вечер никогда не начинается с шума ради шума. Он начинается с правильного тона: с уважения к людям, "
        "с красивого темпа, с точных слов, которые не давят, а открывают пространство. "
        "Поэтому сегодня мы будем двигаться не по шаблону, а по внутренней логике этого события: там, где нужен свет, дадим свет; "
        "там, где нужна улыбка, не будем заменять ее громкостью; там, где нужна эмоция, не испугаемся тишины."
    )
    family_block_intro = (
        "Есть люди, рядом с которыми любая история становится глубже. Именно они помнят не только яркие кадры, "
        "но и то, что остается за ними: маленькие привычки, тихую поддержку, характер, который не видно на фотографиях. "
        "И сейчас важно дать слово не формальности, а близости."
    )

    return {
        "event_passport": {
            "event_type": event_type,
            "format_name": "Рабочий сценарий для ведущего Event AI",
            "city": city,
            "venue": venue,
            "event_date": event_date,
            "working_timeline_note": "Сценарий собран в fallback-режиме, чтобы система оставалась стабильной и рабочей.",
            "main_goal": "Собрать цельный, современный, персонализированный вечер, пригодный для реальной площадки.",
            "atmosphere": atmosphere,
            "style": "живой, дорогой по ощущению, режиссерски точный, без шаблонной пустоты",
            "mandatory_points": key_moments,
            "hard_bans": hard_bans,
            "timing_anchor": timing_anchor,
        },
        "quality_panel": {
            "scenario_verdict": "Сценарий пригоден как рабочая база для площадки и уже содержит управленческую логику.",
            "director_verdict": "Ритм выстроен волнами: знакомство, раскрытие, эмоциональный пик, энергия, финал.",
            "critic_verdict": "Нужно уточнить несколько деталей по гостям и таймингу кухни, но скелет вечера уже собран профессионально.",
            "final_ready": True,
            "fixed_issues": [
                "Убраны устаревшие конкурсы и токсичные приемы.",
                "Сценарий ориентирован на персонализацию, а не на универсальные штампы.",
                "DJ-блок и риски даны прикладно, а не общими словами.",
            ],
        },
        "concept": {
            "big_idea": f"Вечер, в котором в центре не шаблон праздника, а реальные люди вокруг истории {main_hero}.",
            "main_director_thesis": "Не давить форматом, а вести зал через вкус, внимание к деталям и постепенное раскрытие эмоции.",
            "main_emotional_result": "Гости чувствуют, что были не наблюдателями программы, а частью живого и красивого события.",
            "why_this_event_will_be_remembered": "Потому что здесь работают личные смыслы, точный темп и уважительная, взрослая драматургия вечера.",
        },
        "trend_layer": {
            "trend_summary": "Сценарий строится на современной event-логике: персонализация, режиссура, мягкое вовлечение и музыкальная драматургия.",
            "applied_trends": [
                "отказ от кринжовых активностей в пользу точных персональных заходов",
                "сильные, но не крикливые речевые блоки ведущего",
                "гибкий темп с музыкальными волнами вместо монотонного застолья",
                "бережная работа с чувствительными темами и уместностью гостей",
            ],
            "rejected_outdated_patterns": [
                "навязчивые конкурсы ради заполнения пауз",
                "шаблонные тосты без привязки к людям",
                "свадебные и юбилейные штампы, звучащие как чужой текст",
            ],
        },
        "key_host_commands": [
            f"Не трогать без необходимости темы: {', '.join(sensitive_topics)}.",
            "Первыми поднимать самых открытых и поддерживающих атмосферу гостей.",
            "Не жертвовать эмоциональным ядром ради случайного шумного интерактива.",
            "Святые точки вечера заранее проговорить с заказчиком и держать их в тайминге до последнего.",
            "Если зал тяжелый на старт, сначала собирать доверие, а не форсировать веселье.",
        ],
        "questions_to_clarify_before_event": [
            "Есть ли точный тайминг горячего, торта, сюрпризов и технических включений?",
            "Кого точно нельзя вовлекать в активные блоки?",
            "Есть ли обязательные поздравления по списку и каков приоритет этих людей?",
            "Есть ли сюрпризы от гостей или семьи, которые нужно встроить заранее?",
        ],
        "director_logic": {
            "opening_logic": "Открытие строится через доверие и красивое включение зала, без шума ради шума.",
            "development_logic": "Вечер развивается через чередование смысловых точек, гостевого участия и музыкальных волн.",
            "family_or_core_emotional_logic": "Эмоциональное ядро ставится тогда, когда зал уже слушает и готов переживать, а не только наблюдать.",
            "final_logic": "Финал не растягивается, а собирает вечер в ясную, теплую и запоминающуюся точку.",
        },
        "scenario_timeline": [
            {
                "time_from": timing_anchor,
                "time_to": "18:20",
                "block_title": "Сбор гостей и мягкий welcome",
                "block_purpose": "Снять стартовое напряжение и собрать зал в единое поле внимания.",
                "what_happens": "Гости заходят, рассаживаются, атмосфера собирается через музыку и спокойное присутствие ведущего.",
                "host_action": "Ведущий приветствует, ориентирует и аккуратно задает тон вечера.",
                "host_text": "Первое впечатление о вечере складывается раньше, чем прозвучат главные слова. Поэтому старт этого события должен быть не суетливым, а красивым: с воздухом, с ощущением заботы, с внутренним спокойствием. Зал еще только собирается, а мы уже закладываем главный принцип вечера: здесь никто не будет гнаться за шумом, здесь будут создавать настроение тоньше и точнее.",
                "dj_task": "Держать стильный welcome без резких переходов и громких вокальных пиков.",
                "director_move": "Сначала атмосфера, потом акценты.",
                "risk_control": "Не перегружать зал объявлениями, пока гости физически не собраны.",
                "transition": "Когда в зале большинство гостей и внимание стабилизируется, перевести пространство к основному открытию.",
            },
            {
                "time_from": "18:20",
                "time_to": "18:40",
                "block_title": "Главное открытие",
                "block_purpose": "Задать характер вечера, стиль общения и эмоциональный вектор.",
                "what_happens": "Ведущий открывает событие, обозначает интонацию и внутреннюю логику вечера.",
                "host_action": "Говорить образно, но точно, без банальностей и лишнего пафоса.",
                "host_text": opening_main,
                "dj_task": "Короткий кинематографичный вход, затем чистый музыкальный уход под речь.",
                "director_move": "Сформировать доверие к ведущему и желание слушать дальше.",
                "risk_control": "Если зал шумный, использовать короткую версию открытия и вернуться к большой речи позже.",
                "transition": "После открытия перевести внимание к первой содержательной точке вечера.",
            },
            {
                "time_from": "18:40",
                "time_to": "19:20",
                "block_title": "Первое смысловое ядро",
                "block_purpose": "Дать залу не только информацию, но и эмоциональную глубину.",
                "what_happens": "Через близких, историю или важные факты вечер получает человеческий объем и персональную основу.",
                "host_action": "Управлять темпом речей и не превращать теплый блок в затянутую официальность.",
                "host_text": family_block_intro,
                "dj_task": "Мягкие инструментальные подложки, поддерживающие речь, а не спорящие с ней.",
                "director_move": "Углубить зал, прежде чем поднимать энергию.",
                "risk_control": "Если блок затягивается, аккуратно резать количество выходов, а не растягивать эмоцию до усталости.",
                "transition": "После теплой глубины вывести зал в более живое движение через легкий интерактив или музыкальный переход.",
            },
            {
                "time_from": "19:20",
                "time_to": "20:00",
                "block_title": "Мягкое вовлечение гостей",
                "block_purpose": "Поднять энергию, не ломая достоинство вечера.",
                "what_happens": "Работа с гостями строится через ассоциации, личные истории и уместные точечные включения.",
                "host_action": "Поднимать только тех, кто подходит по энергии и уместности; не вытаскивать людей насильно.",
                "host_text": "Самый хороший интерактив это тот, после которого гости чувствуют не неловкость, а удовольствие от того, что их увидели и услышали. Поэтому сейчас важна не форма ради формы, а точность: кого вовлечь, в каком объеме и в какой интонации.",
                "dj_task": "Дать короткие отбивки и музыкальные мосты, не скатываясь в мемность и клоунаду.",
                "director_move": "Переключить зал из слушания в живое присутствие.",
                "risk_control": "Стоп-лист гостей и тем держать в голове постоянно.",
                "transition": "На хорошем уровне энергии перевести вечер к танцу, гастрономической паузе или следующему смысловому блоку.",
            },
            {
                "time_from": "20:00",
                "time_to": "21:00",
                "block_title": "Танцевальная волна и энергетический пик",
                "block_purpose": "Дать залу телесную энергию и ощущение праздника без потери вкуса.",
                "what_happens": "Через выстроенную музыкальную волну гости включаются в движение, а вечер выходит на пик живости.",
                "host_action": "Не мешать музыке лишним микрофоном, а запускать танцпол короткими точными командами.",
                "host_text": "Есть моменты, которые не нужно подробно объяснять. Их нужно просто вовремя отпустить в музыку. И если до этого вечер раскрывался словами и смыслами, то сейчас он должен задышать шире, свободнее, телеснее. Именно так праздник становится не просто красивым, а по-настоящему прожитым.",
                "dj_task": "Начать с комфортного узнавания, затем поднять зал на более яркую, но не безвкусную энергию.",
                "director_move": "Пик должен ощущаться как естественный рост, а не как внезапная попытка раскачать зал.",
                "risk_control": "Если танцпол не идет, сначала дать более знакомый материал средней энергии, а не сразу бить в максимальную громкость.",
                "transition": "После активной волны вернуть внимание к финальному смысловому завершению.",
            },
            {
                "time_from": "21:00",
                "time_to": "21:30",
                "block_title": "Финальное эмоциональное собирание",
                "block_purpose": "Собрать вечер в чистую и запоминающуюся финальную точку.",
                "what_happens": "Финальные слова, важный общий момент, при необходимости общий жест, торт или завершающая музыкальная композиция.",
                "host_action": "Говорить коротко, сильно и тепло, не растягивая финал.",
                "host_text": "Хороший вечер заканчивается не в тот момент, когда выключают музыку, а в тот, когда у людей внутри остается ясное чувство: это было не случайное собрание, а настоящее событие. И если сегодня каждый унесет с собой это ощущение, значит все было не зря.",
                "dj_task": "Подложить объединяющую композицию и аккуратно собрать зал в финальный эмоциональный кадр.",
                "director_move": "Завершить мягко, но собранно, без провисания.",
                "risk_control": "Если гости устали, убрать лишние слова и не превращать финал в второй финал.",
                "transition": "После официального завершения оставить залу свободный мягкий хвост вечера.",
            },
        ],
        "host_script": {
            "opening_main": opening_main,
            "opening_short": "Добрый вечер. Пусть это событие с первых минут будет красивым, точным и по-настоящему вашим.",
            "welcome_line": "Пусть сегодня все начнется не с суеты, а с ощущения, что вы попали именно туда, где должны быть.",
            "first_core_intro": "Прежде чем идти дальше по ритму вечера, важно открыть ту часть истории, без которой все остальное было бы просто внешней формой.",
            "family_block_intro": family_block_intro,
            "surprise_intro": "Следующий момент важен не как эффект ради эффекта, а как живая эмоция, которая останется после праздника дольше любой декорации.",
            "dance_block_intro": "А теперь вечеру пора сменить походку: от красивого разговора перейти в музыку, движение и свободную энергию зала.",
            "final_block_intro": "Перед тем как отпустить этот вечер дальше, хочется собрать его в одну ясную и честную мысль.",
            "closing_words": "Спасибо за атмосферу, за внимание друг к другу и за то, что этот вечер получился не громким, а настоящим. Именно такие события люди вспоминают дольше всего.",
        },
        "dj_guidance": {
            "overall_music_policy": "Музыкальная линия должна расти волнами: стильный welcome, чистое открытие, аккуратная поддержка смысловых сцен, затем уверенный танцевальный подъем и теплый финал.",
            "welcome_music": "Nu-disco, soft funk, elegant pop, lounge-pop, современный легкий groove без навязчивого давления вокалом.",
            "opening_music": "Короткий кинематографичный старт с мягким спадом под голос ведущего.",
            "table_background": "Soul-pop, soft disco, легкий funk, негромкий ритм, чтобы не спорить с речами гостей.",
            "emotional_blocks_music": "Piano, strings, atmospheric pads, инструментальные версии без чрезмерной сентиментальности.",
            "dance_block_1": "Поднять через знакомые треки средней энергии, чтобы зал не испугался входа в танец.",
            "dance_block_2": "Основной пик: уверенные sing-along треки, стильные disco edits, узнаваемые хиты без безвкусной мешанины.",
            "dance_block_3": "Финальный блок подбирать по возрасту и составу гостей, сохраняя вкус и энергию до конца.",
            "final_block_music": "Теплая объединяющая композиция без агрессивного бита, чтобы финал был красивым, а не шумным.",
            "final_music": "Финальный трек должен оставлять ощущение завершенности, а не провоцировать хаотичное добивание танцпола.",
            "stop_list": hard_bans,
            "technical_notes": [
                "Не перебивать ведущего джинглами и мемными звуками.",
                "На эмоциональных блоках держать запас по громкости.",
                "Перед выходами гостей давать чистый музыкальный коридор.",
                "После трогательных блоков поднимать энергию постепенно, а не резким скачком.",
            ],
        },
        "guest_management": {
            "active_people": ["Первыми работать с самыми открытыми и поддерживающими атмосферу гостями."],
            "shy_people": ["Не выводить в центр без предварительного контакта и явного согласия."],
            "important_people": ["Родители, близкие родственники, люди с реальной эмоциональной ценностью для вечера."],
            "do_not_involve": sensitive_topics,
            "sensitive_people_or_topics": sensitive_topics,
            "management_notes": [
                "Не превращать персональную историю в публичный допрос.",
                "Балансировать внимание между героями вечера и залом.",
                "Каждый гость должен чувствовать уважение, даже если он не включен активно.",
            ],
        },
        "risk_map": [
            {
                "risk": "Провал по динамике в первой трети вечера",
                "why_it_matters": "Если старт вялый, зал позже сложнее собрать в единый ритм.",
                "how_to_prevent": "Короткое сильное открытие, быстрая сборка внимания и ранняя персональная точка.",
                "what_to_do_if_triggered": "Сократить длинные речи и раньше перевести вечер в живой формат включения гостей.",
            },
            {
                "risk": "Неудачное касание чувствительной темы",
                "why_it_matters": "Это способно резко разрушить доверие к ведущему и атмосферу события.",
                "how_to_prevent": "Заранее собрать стоп-лист и не импровизировать на спорных темах.",
                "what_to_do_if_triggered": "Быстро увести фокус на нейтральный теплый блок без оправданий и долгих комментариев.",
            },
            {
                "risk": "Танцпол не включается с первого захода",
                "why_it_matters": "Слишком жесткий вход в танец может посадить энергию зала еще сильнее.",
                "how_to_prevent": "Начинать с узнаваемого материала средней энергии и правильно подводить зал речью.",
                "what_to_do_if_triggered": "Сделать короткий откат, дать еще одну смысловую точку и вернуться к танцу через 7-10 минут.",
            },
        ],
        "plan_b": [
            {
                "situation": "Гости долго рассаживаются или задерживается старт",
                "solution": "Продлить welcome, укоротить первое официальное открытие и сместить основной смысловой блок, не ломая общую драматургию.",
            },
            {
                "situation": "Поздравительные речи затягиваются",
                "solution": "Ограничить количество живых выходов, часть сообщений перевести в более компактный формат или перенести после следующей волны энергии.",
            },
            {
                "situation": "Техника или музыка дают сбой",
                "solution": "Ведущий уходит в короткий живой текст и ручное удержание внимания, пока команда тихо чинит техническую часть.",
            },
        ],
        "final_print_version": {
            "title": f"Краткая версия: {main_hero or 'событие'}",
            "summary": "Современный, персонализированный, режиссерски собранный вечер с фокусом на уместность, вкус и живую атмосферу.",
            "timeline_short": [
                f"{timing_anchor} — сбор гостей и welcome",
                "главное открытие",
                "первое смысловое ядро",
                "мягкое вовлечение гостей",
                "танцевальная волна",
                "финальное собирание",
            ],
            "must_do": [
                "держать ритм волнами, а не сплошным шумом",
                "работать через личные смыслы и точные формулировки",
                "согласовать критические точки вечера заранее",
            ],
            "must_not_do": hard_bans,
            "host_focus": [
                "доверие зала",
                "бережность к людям",
                "точность тона",
                "контроль тайминга ключевых блоков",
            ],
            "dj_focus": [
                "чистые музыкальные коридоры",
                "поддержка эмоциональных сцен",
                "безопасный и вкусный разгон танцпола",
            ],
        },
    }


def build_system_prompt() -> str:
    return """
Ты — сильный event-режиссер, сценарист ведущих и редактор финального рабочего документа.

Работаешь только с двумя типами мероприятий:
- wedding
- jubilee

Твоя задача: на основе анкеты собрать ГОТОВЫЙ рабочий сценарий для ведущего.
Это не обзор анкеты и не список советов.
Это должен быть прикладной документ, пригодный для настоящей работы на площадке.

Критические требования:
- один основной сильный вызов
- никакой воды
- никакого канцелярита
- никакой шаблонной романтической или юбилейной банальности
- не предлагай кринжовые конкурсы, токсичный юмор и устаревшие форматы
- стиль речи ведущего должен быть образным, метафоричным, сценичным, но пригодным к чтению вслух
- ключевые тексты ведущего должны быть длинными и содержательными
- DJ guidance должен быть прикладным, с музыкальной логикой, а не абстракцией
- если данных не хватает, не ломайся: строй лучший рабочий вариант и отдельно выноси уточнения

Верни строго JSON со следующими ключами:
event_passport
quality_panel
concept
trend_layer
key_host_commands
questions_to_clarify_before_event
director_logic
scenario_timeline
host_script
dj_guidance
guest_management
risk_map
plan_b
final_print_version
"""


def normalize_program(program: dict[str, Any], questionnaire: dict[str, Any]) -> dict[str, Any]:
    fallback = build_fallback_program(questionnaire)
    for key, value in fallback.items():
        if key not in program or not program[key]:
            program[key] = value
    for key in [
        "event_passport",
        "quality_panel",
        "concept",
        "trend_layer",
        "director_logic",
        "host_script",
        "dj_guidance",
        "guest_management",
        "final_print_version",
    ]:
        if not isinstance(program.get(key), dict):
            program[key] = fallback[key]
    for key in ["key_host_commands", "questions_to_clarify_before_event", "risk_map", "plan_b"]:
        if not isinstance(program.get(key), list):
            program[key] = fallback[key]
    if not isinstance(program.get("scenario_timeline"), list) or not program["scenario_timeline"]:
        program["scenario_timeline"] = fallback["scenario_timeline"]
    return program


def parse_json_response(raw_text: str) -> dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise RuntimeError("OpenAI вернул невалидный JSON")
        return json.loads(raw_text[start : end + 1])


def is_program_actual(program: Any) -> bool:
    if not isinstance(program, dict):
        return False
    if program.get("_schema_version") != PROGRAM_SCHEMA_VERSION:
        return False
    required_keys = {
        "event_passport",
        "quality_panel",
        "concept",
        "trend_layer",
        "key_host_commands",
        "questions_to_clarify_before_event",
        "director_logic",
        "scenario_timeline",
        "host_script",
        "dj_guidance",
        "guest_management",
        "risk_map",
        "plan_b",
        "final_print_version",
    }
    return required_keys.issubset(program.keys())


def generate_agent_program(questionnaire: dict[str, Any]) -> dict[str, Any]:
    fallback_program = build_fallback_program(questionnaire)
    fallback_program["_schema_version"] = PROGRAM_SCHEMA_VERSION
    if client is None:
        return fallback_program

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
        program = parse_json_response(raw_text)
        program = normalize_program(program, questionnaire)
        program["_schema_version"] = PROGRAM_SCHEMA_VERSION
        return program
    except Exception:
        return fallback_program


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


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


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

    document.add_heading("2. Сценарий ведущего", level=1)

    passport = as_dict(program.get("event_passport"))
    document.add_heading("2.1 Паспорт события", level=2)
    for field, title in [
        ("event_type", "Тип"),
        ("format_name", "Формат"),
        ("city", "Город"),
        ("venue", "Площадка"),
        ("event_date", "Дата"),
        ("working_timeline_note", "Рабочая пометка по таймингу"),
        ("main_goal", "Главная цель"),
        ("atmosphere", "Атмосфера"),
        ("style", "Стиль"),
        ("timing_anchor", "Тайминговый якорь"),
    ]:
        add_label_value(document, title, passport.get(field, ""))
    document.add_paragraph("Обязательные точки:")
    add_list(document, as_list(passport.get("mandatory_points")))
    document.add_paragraph("Жесткие запреты:")
    add_list(document, as_list(passport.get("hard_bans")))

    quality = as_dict(program.get("quality_panel"))
    document.add_heading("2.2 Качество результата", level=2)
    add_label_value(document, "Сценарный вердикт", quality.get("scenario_verdict", ""))
    add_label_value(document, "Режиссерский вердикт", quality.get("director_verdict", ""))
    add_label_value(document, "Критический вердикт", quality.get("critic_verdict", ""))
    add_label_value(document, "Готово к работе", "Да" if quality.get("final_ready") else "Нет")
    document.add_paragraph("Исправленные слабые места:")
    add_list(document, as_list(quality.get("fixed_issues")))

    concept = as_dict(program.get("concept"))
    document.add_heading("2.3 Концепция", level=2)
    for field, title in [
        ("big_idea", "Большая идея"),
        ("main_director_thesis", "Главный режиссерский тезис"),
        ("main_emotional_result", "Эмоциональный результат"),
        ("why_this_event_will_be_remembered", "Почему вечер запомнится"),
    ]:
        add_label_value(document, title, concept.get(field, ""))

    trend_layer = as_dict(program.get("trend_layer"))
    document.add_heading("2.4 Современная логика", level=2)
    add_label_value(document, "Резюме", trend_layer.get("trend_summary", ""))
    document.add_paragraph("Что применено:")
    add_list(document, as_list(trend_layer.get("applied_trends")))
    document.add_paragraph("Что отброшено как устаревшее:")
    add_list(document, as_list(trend_layer.get("rejected_outdated_patterns")))

    document.add_heading("2.5 Ключевые команды ведущему", level=2)
    add_list(document, as_list(program.get("key_host_commands")))

    document.add_heading("2.6 Что нужно уточнить до мероприятия", level=2)
    add_list(document, as_list(program.get("questions_to_clarify_before_event")))

    logic = as_dict(program.get("director_logic"))
    document.add_heading("2.7 Режиссерская логика вечера", level=2)
    for field, title in [
        ("opening_logic", "Логика открытия"),
        ("development_logic", "Логика развития"),
        ("family_or_core_emotional_logic", "Логика эмоционального ядра"),
        ("final_logic", "Логика финала"),
    ]:
        add_label_value(document, title, logic.get(field, ""))

    document.add_heading("2.8 Пошаговый тайминг", level=2)
    for index, block in enumerate(as_list(program.get("scenario_timeline")), start=1):
        block = as_dict(block)
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

    script = as_dict(program.get("host_script"))
    document.add_heading("2.9 Тексты ведущего", level=2)
    for field, title in [
        ("opening_main", "Opening main"),
        ("opening_short", "Opening short"),
        ("welcome_line", "Welcome line"),
        ("first_core_intro", "First core intro"),
        ("family_block_intro", "Family block intro"),
        ("surprise_intro", "Surprise intro"),
        ("dance_block_intro", "Dance block intro"),
        ("final_block_intro", "Final block intro"),
        ("closing_words", "Closing words"),
    ]:
        add_label_value(document, title, script.get(field, ""))

    dj = as_dict(program.get("dj_guidance"))
    document.add_heading("2.10 DJ guidance", level=2)
    for field, title in [
        ("overall_music_policy", "Overall music policy"),
        ("welcome_music", "Welcome music"),
        ("opening_music", "Opening music"),
        ("table_background", "Table background"),
        ("emotional_blocks_music", "Emotional blocks music"),
        ("dance_block_1", "Dance block 1"),
        ("dance_block_2", "Dance block 2"),
        ("dance_block_3", "Dance block 3"),
        ("final_block_music", "Final block music"),
        ("final_music", "Final music"),
    ]:
        add_label_value(document, title, dj.get(field, ""))
    document.add_paragraph("Stop list:")
    add_list(document, as_list(dj.get("stop_list")))
    document.add_paragraph("Technical notes:")
    add_list(document, as_list(dj.get("technical_notes")))

    guest_management = as_dict(program.get("guest_management"))
    document.add_heading("2.11 Работа с гостями", level=2)
    for field, title in [
        ("active_people", "Активные люди"),
        ("shy_people", "Скромные люди"),
        ("important_people", "Важные люди"),
        ("do_not_involve", "Кого не вовлекать"),
        ("sensitive_people_or_topics", "Чувствительные люди и темы"),
        ("management_notes", "Рабочие заметки"),
    ]:
        document.add_paragraph(f"{title}:")
        add_list(document, as_list(guest_management.get(field)))

    document.add_heading("2.12 Риски", level=2)
    for item in as_list(program.get("risk_map")):
        item = as_dict(item)
        add_label_value(document, "Риск", item.get("risk", ""))
        add_label_value(document, "Почему важен", item.get("why_it_matters", ""))
        add_label_value(document, "Как предотвратить", item.get("how_to_prevent", ""))
        add_label_value(document, "Что делать, если сработало", item.get("what_to_do_if_triggered", ""))

    document.add_heading("2.13 План Б", level=2)
    for item in as_list(program.get("plan_b")):
        item = as_dict(item)
        add_label_value(document, "Ситуация", item.get("situation", ""))
        add_label_value(document, "Решение", item.get("solution", ""))

    final_print = as_dict(program.get("final_print_version"))
    document.add_heading("2.14 Краткая версия для печати", level=2)
    add_label_value(document, "Название", final_print.get("title", ""))
    add_label_value(document, "Краткое резюме", final_print.get("summary", ""))
    for field, title in [
        ("timeline_short", "Короткий таймлайн"),
        ("must_do", "Must do"),
        ("must_not_do", "Must not do"),
        ("host_focus", "Фокус ведущего"),
        ("dj_focus", "Фокус диджея"),
    ]:
        document.add_paragraph(f"{title}:")
        add_list(document, as_list(final_print.get(field)))

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
    if is_program_actual(submission.get("program")):
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
    if not is_program_actual(program):
        try:
            program = generate_agent_program(submission["questionnaire"])
            submissions[index]["program"] = program
            save_submissions(submissions)
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Ошибка генерации перед экспортом: {error}") from error

    try:
        buffer = build_docx(submission, program)
        client_name = safe_filename(submission["questionnaire"].get("clientName", "client"))
        event_type = safe_filename(submission["questionnaire"].get("eventType", "event"))
        filename = f"{event_type}_{client_name}_{submission_id}.docx"
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Ошибка Word-выгрузки: {error}") from error
