import telebot
import pandas as pd
import random
import json
import csv
import os
import signal
import sys
import time
import numpy as np
import ssl
import requests
import urllib3
from urllib3.poolmanager import PoolManager
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CustomHTTPAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = ctx
        return super().proxy_manager_for(*args, **kwargs)

session = requests.Session()
adapter = CustomHTTPAdapter()
session.mount('https://', adapter)
session.verify = False

bot = telebot.TeleBot('8366317823:AAFcEZTf-HcBIcTC74Z4nizbXIgRBT_tIXQ')

def get_bot_with_custom_session():
    import telebot.apihelper
    telebot.apihelper.session = session
    return bot

bot = get_bot_with_custom_session()

stop_bot = False

def signal_handler(sig, frame):
    global stop_bot
    print("\n\n⚠️ Получен сигнал остановки. Завершаю работу...")
    stop_bot = True
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

data_file = 'data/books.xlsx'
if not os.path.exists(data_file):
    df = pd.DataFrame({
        'title': ['Граф Монте-Кристо том 1', 'Граф Монте-Кристо том 2', 'Что делать?', 'Гроза', 'Герой нашего времени', 'Над пропастью во ржи', 'Кому на Руси жить хорошо', 'Так говорил Заратустра', 'Одиссея капитана Блада', 'Продавец воздуха', 'Морской волчонок', 'Лебединая песня', 'Лекарство от меланхолии', 'Мёртвые души', 'История о конфетах', 'Светлый человек', 'Похититель детей', 'Кокай Наькъаш', 'Монстры Акслин: Хранители цитадели', 'Дубровский. Повести Белкина', 'Фараон', 'Маленький принц', 'Алхимик', 'Падение дома Ашеров', 'Горе от ума', 'Цветы для Элджернона', 'Гранатовый браслет', 'Капитанская дочка', 'Бархат фиалки', 'Джейн Эйр', 'Книжный вор', 'Преступление и наказание', 'Искусство войны', '451 градус по Фаренгейту', 'Илиада. Одиссея', 'Тайна чёрного дракона', 'Общество мёртвых поэтов', 'Самое красное яблоко', 'Дом, в котором 1', 'Дом, в котором 2', 'Дом, в котором 3', 'Чувства и чувствительность', 'Фауст', 'Морфий. Повести и рассказы', 'Рождение науки и искусства', 'Записки на салфетках', 'Призрак оперы', 'Мадонна в чёрном', 'Отель с привидениями', 'Не говори никому', 'Человек недостойный', 'Администратор Instagram', 'Креативы', 'Революция надежды', 'Маленькие женщины', 'Коучинг', 'Как устроена экономика', 'Дизайн привычных вещей', 'Стратегия голубого океана', 'Бизнес-модели', 'Как оценить бизнес по аналогии', 'Найден более быстрый маршрут', 'Amazon', 'Управленческие концепции в бизнес-модели: полное руководство', 'Гений коммуникации', 'Управляй как Шейх', '5 капиталов', 'Антихрупкость', 'Четвёртая промышленная революция', 'Принципы: жизнь и работа', 'Не верьте цифрам', 'Самый богатый человек в Вавилоне', 'Большие продажи без компромиссов и оправданий', 'Экономика впечатлений', 'Чистый код', 'Как завоёвывать друзей и оказывать влияние на людей', 'Женские презентации', 'Не мешай себе жить', 'Самый великий торговец в мире', 'Договориться можно обо всем!', 'Шаблоны программирования для начинающих с примерами на Python', 'Дети деньги не зарабатывают', 'Продавая незримое', 'Как продать что угодно кому угодно', 'Дело не в кофе', 'Простой сложный разговор', 'Как приготовить проект', 'Просто криптография', 'Дорога к свободе: беседы с Кахой Бендукидзе', 'Деньги без дураков', 'Разговоры, которые сближают', 'Сборник задач по математике', '12 недель в году', 'Суперобучение', 'Теория игр', 'Практики регулярного менеджмента', 'Работа с возражениями и отказами', 'Flash Boys', 'Реклама: игра на эмоциях', 'Hooked: на крючке', 'Ritz-Carlton: совершенство побеждает', 'Настольная книга финансового директора', 'Как решить любую проблему', 'Управление по целям и ключевым результатам', 'Скорбь Сатаны', 'Нортенгерское аббатство', 'Дао Toyota', 'Это база', 'Скандинавский дизайн', 'Социальный капитал', 'Карьера менеджера', 'Переговоры: полный курс', 'Sony. Сделано в Японии', 'Одураченные случайностью', 'Бизнес-план на 100%', 'Эмоциональный интеллект', 'Скрипты продаж', 'Додо: от подвала до миллиарда', 'Стратегия чистого листа', 'Не просто речь'],
        'author': ['Александр Дюма', 'Александр Дюма', 'Николай Чернышевский', 'Александр Островский', 'Михаил Лермонтов', 'Дж. Д. Сэлинджер', 'Николай Некрасов', 'Фридрих Ницше', 'Рафаэль Сабатини', 'А. Р. Беляев', 'Майн Рид', 'Эдмунд Криспин', 'Рэй Брэдбери', 'Николай Васильевич Гоголь', 'Ши Мэр', 'Макс Максимов', 'Бром', 'Эсет Газдиева', 'Лаура Гальего', 'Александр Пушкин', 'Болеслав Прус', 'Антуан де Сент-Экзюпери', 'Пауло Коэльо', 'Эдгар Аллан По', 'Александр Грибоедов', 'Дэниел Киз', 'Александр Куприн', 'Александр Пушкин', 'Элина Базоркина', 'Шарлотта Бронте', 'Маркус Зусак', 'Фёдор Достоевский', 'Сунь-Цзы', 'Рэй Брэдбери', 'Гомер', 'Анна Джейн', 'Н. Г. Клейнбаум', 'Джезебел Морган', 'Мариам Петросян', 'Мариам Петросян', 'Мариам Петросян', 'Джейн Остин', 'Иоганн Вольфганг Гёте', 'Михаил Булгаков', 'Леонардо да Винчи', 'Гарт Каллахан', 'Гастон Леру', 'Рюноске Акутагава', 'Мелки Коллинз', 'Харлан Кобен', 'Осаму Дазай', 'Дмитрий Кудряшов, Евгений Козлов', 'Генри Тодд', 'Эрих Фромм', 'Луиза Мэй Олкотт', 'Джон Уитмор', 'Ха-Джун Чанг', 'Дон Норман', 'В. Чан Ким, Рене Моборн', 'Оливер Гассман', 'Елена Чиркова', 'Илья Балахнин', 'Наталья Берг, Мия Найтс', 'Пол Хейг', 'Дейв Керпен', 'Ясар Джаррар', 'Татьяна Волкова', 'Нассим Николас Талеб', 'Клаус Шваб', 'Рэй Далио', 'Джон Богл', 'Джордж Клейсон', 'Сергей Семёнов', 'Джозеф Б. Пайн II, Джеймс Х. Гилмор', 'Роберт Мартин', 'Дейл Карнеги', 'Дэн Кеннеди, Дастин Мэтьюс', 'Марк Гоулстон', 'Ог Мандино', 'Гэвин Кеннеди', 'Дэвид Бернштейн', 'Ирина Марьевич', 'Гарри Беквит', 'Джо Джирард', 'Говард Бехар', 'Элисон Вуд Брукс', 'Егор Ганин', 'Виктор де Касто', 'Владимир Федорин', 'Александр Силаев', 'Павел Лебедько', 'М. И. Сканави', 'Брайан Моран, Майкл Леннингтон', 'Скотт Янг', 'Авинаш Диксит, Барри Нейлбафф', 'Павел Безручко', 'Дмитрий Ткаченко', 'Майкл Льюис', 'Алексей Иванов', 'Нир Эяль, Райан Хувер', 'Шульце Хорст', 'Стивен Брег', 'ТРИЗ', 'Ветри Веллор', 'Мария Корелли', 'Джейн Остин', 'Джеффри Лайкер', 'Максим Батырев', 'Катя Карлинг', 'Станиславов Натапов', 'Ли Якокка', 'Гэвин Кеннеди', 'Акио Морита', 'Нассим Николас Талеб', 'Ронда Абрамс', 'Дэниел Гоулман', 'Дмитрий Ткаченко', 'Александр Кияткин', 'Марк Розин', 'Лариса Зорина'],
        'жанр': ['Роман, Приключение, Классика, История', 'Роман, Приключение, Классика, История', 'Роман, Социальная утопия', 'Драма', 'Психологический роман, Классика', 'Роман, Классика, Современная проза', 'Поэма-эпопея, Классика', 'Философский трактат, Притча', 'Приключенческий роман, Исторические приключения', 'Научная фантастика, Классика', 'Приключенческий роман, Классика', 'Детектив, Классический детектив', 'Сборник рассказов, Фантастика', 'Поэма (роман), Классика', 'Современная проза, Романтика', 'Современная проза, Драма', 'Хоррор, Темное фэнтези', 'Проза, Ингушская литература', 'Фэнтези, Молодежная литература', 'Роман, Повести, Классика', 'Исторический роман, Классика', 'Сказка-притча, Философская сказка', 'Роман-притча, Философия', 'Рассказ, Готика, Ужасы', 'Комедия в стихах, Драматургия', 'Научная фантастика, Психологическая драма', 'Повесть, Классика, Любовь', 'Исторический роман, Классика', 'Проза, Современная литература', 'Роман, Готика, Классика', 'Исторический роман, Молодежная литература', 'Психологический роман, Классика', 'Трактат, Философия, Стратегия', 'Антиутопия, Научная фантастика', 'Эпопея, Античная литература', 'Фэнтези, Детектив', 'Роман, Драма', 'Современная проза, Драма', 'Магический реализм, Роман', 'Магический реализм, Роман', 'Магический реализм, Роман', 'Роман, Классика, Любовь', 'Трагедия, Философская поэма', 'Рассказы, Повести, Классика', 'Трактат, Искусствоведение', 'Бизнес, Менеджмент', 'Готический роман, Ужасы', 'Рассказы, Японская классика', 'Ужасы, Триллер', 'Триллер, Детектив', 'Роман, Японская классика', 'Маркетинг, SMM', 'Реклама, Маркетинг', 'Философия, Психология', 'Роман, Классика', 'Бизнес, Саморазвитие', 'Экономика, Нон-фикшн', 'Дизайн, Психология', 'Бизнес, Стратегия', 'Бизнес, Менеджмент', 'Финансы, Оценка бизнеса', 'Бизнес, Маркетинг', 'Бизнес, История компаний', 'Менеджмент, Бизнес', 'Коммуникации, Саморазвитие', 'Менеджмент, Лидерство', 'Финансы, Личные финансы', 'Философия, Экономика', 'Технологии, Общество', 'Биография, Менеджмент', 'Финансы, Инвестиции', 'Финансы, Саморазвитие', 'Продажи, Бизнес', 'Бизнес, Маркетинг', 'Программирование, IT', 'Психология, Саморазвитие', 'Ораторское искусство, Бизнес', 'Психология, Саморазвитие', 'Мотивация, Саморазвитие', 'Переговоры, Бизнес', 'Программирование, Python', 'Финансовая грамотность, Дети', 'Маркетинг, Услуги', 'Продажи, Бизнес', 'Бизнес, Корпоративная культура', 'Коммуникации, Психология', 'Управление проектами, IT', 'Криптография, IT', 'Биография, Экономика', 'Финансы, Личные финансы', 'Коммуникации, Психология', 'Учебник, Математика', 'Тайм-менеджмент, Бизнес', 'Саморазвитие, Обучение', 'Экономика, Математика', 'Менеджмент, Бизнес', 'Продажи, Переговоры', 'Финансы, Нон-фикшн', 'Маркетинг, Реклама', 'Продуктовый дизайн, Психология', 'Бизнес, Сервис', 'Финансы, Управление', 'Инженерия, Креативность', 'Менеджмент, OKR', 'Роман, Мистика', 'Роман, Классика, Сатира', 'Менеджмент, Производство', 'Бизнес, Менеджмент', 'Дизайн, Искусство', 'Социология, Экономика', 'Биография, Менеджмент', 'Переговоры, Бизнес', 'Биография, Бизнес', 'Философия, Вероятность', 'Бизнес, Планирование', 'Психология, Саморазвитие', 'Продажи, Бизнес', 'Бизнес, История компаний', 'Бизнес, Стратегия', 'Ораторское искусство, Риторика'],
        'кол_страниц': [768, 576, 576, 105, 288, 304, 448, 416, 416, 224, 256, 256, 320, 352, 280, 320, 448, 240, 352, 224, 704, 96, 192, 48, 128, 320, 128, 224, 288, 448, 544, 544, 128, 224, 704, 320, 224, 288, 640, 640, 640, 352, 352, 224, 320, 224, 352, 192, 288, 416, 224, 224, 224, 320, 448, 224, 320, 384, 288, 224, 224, 224, 288, 320, 224, 224, 224, 544, 224, 544, 320, 192, 224, 320, 416, 320, 224, 288, 192, 320, 320, 192, 288, 224, 288, 288, 224, 224, 320, 224, 224, 448, 224, 288, 416, 288, 224, 320, 224, 224, 224, 448, 224, 224, 448, 288, 320, 224, 224, 288, 320, 320, 320, 320, 320, 320, 384, 224, 320, 224, 224],
        'rating': [0] * 121
    })
    df.to_excel(data_file, index=False)

q = pd.read_excel(data_file)
q = q.fillna('')
q['жанр'] = q['жанр'].str.split(', ')

tfidf = TfidfVectorizer(stop_words='english')
q['текст_для_вектора'] = q['жанр'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x))
tfidf_matrix = tfidf.fit_transform(q['текст_для_вектора'])

def train_ml_model():
    global tfidf, tfidf_matrix
    q['текст_для_вектора'] = q['жанр'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x))
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(q['текст_для_вектора'])
    return tfidf, tfidf_matrix

def ml_recommend(prefs, mood, rating_importance, volume_pref):
    user_profile = ' '.join(prefs)
    user_vec = tfidf.transform([user_profile])
    similarities = cosine_similarity(user_vec, tfidf_matrix).flatten()
    
    scores = {}
    for idx, sim in enumerate(similarities):
        score = sim * 10
        row = q.iloc[idx]
        genres = row['жанр'] if isinstance(row['жанр'], list) else []
        
        if mood == 'веселое' and any(g in ['Приключение', 'Романтика', 'Комедия'] for g in genres):
            score += 2
        elif mood == 'грустное' and any(g in ['Драма', 'Психологическая драма'] for g in genres):
            score += 2
        elif mood == 'напряженное' and any(g in ['Триллер', 'Детектив', 'Ужасы'] for g in genres):
            score += 2
        
        if rating_importance == 'хиты' and row['rating'] >= 4:
            score += 3
        elif rating_importance == 'новинки' and row['rating'] < 4 and row['rating'] > 0:
            score += 2
        
        pages = row['кол_страниц']
        if volume_pref == 'маленькая' and pages < 200:
            score += 1
        elif volume_pref == 'средняя' and 200 <= pages <= 400:
            score += 1
        elif volume_pref == 'большая' and pages > 400:
            score += 1
        
        scores[idx] = score
    
    sorted_books = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_idx = [x[0] for x in sorted_books[:3]]
    
    recommendations = []
    for idx in top_idx:
        row = q.iloc[idx]
        recommendations.append({
            'title': row['title'],
            'author': row['author'],
            'genre': ', '.join(row['жанр']) if isinstance(row['жанр'], list) else row['жанр'],
            'pages': row['кол_страниц'],
            'rating': row['rating'],
            'score': round(scores[idx], 2),
            'ml_score': round(similarities[idx] * 100, 2)
        })
    
    recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)
    
    return recommendations

def init_files():
    files = ['uu.txt', 'hh.txt', 'aa.txt', 'll.txt', 'tt.txt', 'admin.txt']
    for f in files:
        if not os.path.exists(f):
            open(f, 'w').close()
    if not os.path.exists('logs'):
        os.makedirs('logs')

init_files()
train_ml_model()

def is_admin(uid):
    if not os.path.exists('admin.txt'):
        return False
    with open('admin.txt', 'r') as f:
        content = f.read().strip()
        if not content:
            return False
        return str(uid) in content.split(',')

def get_user_prefs(uid):
    if not os.path.exists('uu.txt'):
        return None
    with open('uu.txt', 'r') as f:
        for line in f:
            if line.strip() and str(uid) in line:
                parts = line.strip().split(':', 1)
                if len(parts) > 1:
                    return parts[1]
    return None

def save_user_prefs(uid, data):
    lines = []
    found = False
    if os.path.exists('uu.txt'):
        with open('uu.txt', 'r') as f:
            for line in f:
                if line.strip() and str(uid) in line:
                    lines.append(f"{uid}:{data}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"{uid}:{data}\n")
    with open('uu.txt', 'w') as f:
        f.writelines(lines)

def get_history(uid):
    if not os.path.exists('hh.txt'):
        return []
    with open('hh.txt', 'r') as f:
        for line in f:
            if line.strip() and str(uid) in line:
                parts = line.strip().split(':', 1)
                if len(parts) > 1 and parts[1]:
                    return parts[1].split(',')
                return []
    return []

def save_history(uid, books):
    lines = []
    found = False
    if os.path.exists('hh.txt'):
        with open('hh.txt', 'r') as f:
            for line in f:
                if line.strip() and str(uid) in line:
                    lines.append(f"{uid}:{','.join(books)}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"{uid}:{','.join(books)}\n")
    with open('hh.txt', 'w') as f:
        f.writelines(lines)

def get_step(uid):
    if not os.path.exists('aa.txt'):
        return 0
    with open('aa.txt', 'r') as f:
        for line in f:
            if line.strip() and str(uid) in line:
                parts = line.strip().split(':', 1)
                if len(parts) > 1:
                    try:
                        return int(parts[1])
                    except:
                        return 0
                return 0
    return 0

def save_step(uid, step):
    lines = []
    found = False
    if os.path.exists('aa.txt'):
        with open('aa.txt', 'r') as f:
            for line in f:
                if line.strip() and str(uid) in line:
                    lines.append(f"{uid}:{step}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"{uid}:{step}\n")
    with open('aa.txt', 'w') as f:
        f.writelines(lines)

def get_temp(uid):
    if not os.path.exists('ll.txt'):
        return {}
    with open('ll.txt', 'r') as f:
        for line in f:
            if line.strip() and str(uid) in line:
                parts = line.strip().split(':', 1)
                if len(parts) > 1 and parts[1]:
                    try:
                        return json.loads(parts[1])
                    except:
                        return {}
                return {}
    return {}

def save_temp(uid, data):
    lines = []
    found = False
    if os.path.exists('ll.txt'):
        with open('ll.txt', 'r') as f:
            for line in f:
                if line.strip() and str(uid) in line:
                    lines.append(f"{uid}:{json.dumps(data)}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"{uid}:{json.dumps(data)}\n")
    with open('ll.txt', 'w') as f:
        f.writelines(lines)

def get_pref(uid):
    if not os.path.exists('tt.txt'):
        return None
    with open('tt.txt', 'r') as f:
        for line in f:
            if line.strip() and str(uid) in line:
                parts = line.strip().split(':', 1)
                if len(parts) > 1:
                    return parts[1]
                return None
    return None

def save_pref(uid, pref):
    lines = []
    found = False
    if os.path.exists('tt.txt'):
        with open('tt.txt', 'r') as f:
            for line in f:
                if line.strip() and str(uid) in line:
                    if pref is not None:
                        lines.append(f"{uid}:{pref}\n")
                    found = True
                else:
                    lines.append(line)
    if not found and pref is not None:
        lines.append(f"{uid}:{pref}\n")
    with open('tt.txt', 'w') as f:
        f.writelines(lines)

def get_all_genres():
    all_genres = set()
    for genres in q['жанр']:
        if isinstance(genres, list):
            for g in genres:
                if g and g.strip():
                    all_genres.add(g.strip())
    return sorted(list(all_genres))

def get_rating_stars(rating):
    if rating == 0:
        return '⭐ не оценена'
    stars = '⭐' * min(5, int(rating))
    return stars

def log_activity(uid, action):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    with open('logs/activity.log', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()}|{uid}|{action}\n")

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    log_activity(uid, 'start')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton('📚 Начать опрос'),
        KeyboardButton('🎲 Случайная книга'),
        KeyboardButton('🔄 Получить новую подборку'),
        KeyboardButton('👤 Профиль'),
        KeyboardButton('📖 История'),
        KeyboardButton('⭐ Оценить книгу')
    )
    if is_admin(uid):
        markup.add(
            KeyboardButton('📊 Статистика'),
            KeyboardButton('📤 Экспорт'),
            KeyboardButton('📥 Импорт'),
            KeyboardButton('👥 Пользователи'),
            KeyboardButton('📋 Логи')
        )
    bot.send_message(
        message.chat.id,
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я бот-рекомендатор книг с ML моделью! 🧠📚\n\n"
        "Я использую машинное обучение для подбора книг.\n\n"
        "Нажми '📚 Начать опрос' чтобы ответить на вопросы, или '🎲 Случайная книга' для быстрой рекомендации.",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def help_cmd(message):
    uid = message.from_user.id
    log_activity(uid, 'help')
    help_text = (
        "📖 **Помощь по боту**\n\n"
        "🤖 **Основные команды:**\n"
        "/start - Запустить бота\n"
        "/help - Показать эту справку\n"
        "/again - Получить новую подборку (без повторного опроса)\n"
        "/profile - Посмотреть/изменить свои предпочтения\n"
        "/random - Быстрая рекомендация без опроса\n"
        "/history - Список ранее прочитанных книг\n"
        "/grade - Оценить книгу\n\n"
        "🧠 **Как работает ML модель:**\n"
        "1. Я анализирую твои предпочтения\n"
        "2. Использую TF-IDF и косинусное сходство\n"
        "3. Нахожу книги, максимально похожие на твой профиль\n"
        "4. Учитываю настроение, рейтинг и объем книги\n\n"
        "🎯 **Совет:** Чем подробнее ответы, тем точнее рекомендации!"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['again'])
def again_cmd(message):
    uid = message.from_user.id
    log_activity(uid, 'again')
    pref = get_pref(uid)
    if pref:
        parts = pref.split('|')
        if len(parts) == 4:
            prefs, mood, rating, volume = parts
            recs = ml_recommend(prefs.split(','), mood, rating, volume)
            send_recommendations(message, recs)
        else:
            bot.send_message(message.chat.id, "Ошибка в данных предпочтений. Пройди опрос заново.")
    else:
        bot.send_message(message.chat.id, "Сначала пройди опрос! Нажми '📚 Начать опрос'.")

@bot.message_handler(commands=['profile'])
def profile_cmd(message):
    uid = message.from_user.id
    log_activity(uid, 'profile')
    pref = get_pref(uid)
    if pref:
        parts = pref.split('|')
        if len(parts) == 4:
            prefs, mood, rating, volume = parts
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("🔄 Изменить предпочтения", callback_data="change_prefs"),
                InlineKeyboardButton("❌ Очистить", callback_data="clear_prefs")
            )
            bot.send_message(
                message.chat.id,
                f"👤 **Ваш профиль:**\n\n"
                f"📚 Жанры: {', '.join(prefs.split(','))}\n"
                f"🎭 Настроение: {mood}\n"
                f"⭐ Рейтинг: {rating}\n"
                f"📖 Объем: {volume}\n\n"
                f"🧠 ML модель: TF-IDF + Cosine Similarity\n"
                f"📚 Всего книг в базе: {len(q)}",
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "Данные профиля повреждены. Пройди опрос заново.")
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📚 Пройти опрос", callback_data="start_quiz"))
        bot.send_message(message.chat.id, "Профиль не найден. Пройди опрос!", reply_markup=markup)

@bot.message_handler(commands=['random'])
def random_cmd(message):
    uid = message.from_user.id
    log_activity(uid, 'random')
    idx = random.randint(0, len(q) - 1)
    row = q.iloc[idx]
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("⭐ Оценить", callback_data=f"rate_{idx}"),
        InlineKeyboardButton("📥 В историю", callback_data=f"add_history_{idx}")
    )
    bot.send_message(
        message.chat.id,
        f"📖 **Случайная книга:**\n\n"
        f"📌 Название: {row['title']}\n"
        f"✍️ Автор: {row['author']}\n"
        f"📚 Жанр: {row['жанр'] if isinstance(row['жанр'], str) else ', '.join(row['жанр'])}\n"
        f"📄 Страниц: {row['кол_страниц']}\n"
        f"⭐ Рейтинг: {get_rating_stars(row['rating'])}",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['history'])
def history_cmd(message):
    uid = message.from_user.id
    log_activity(uid, 'history')
    history = get_history(uid)
    if history:
        books = []
        for title in history:
            book = q[q['title'] == title]
            if not book.empty:
                row = book.iloc[0]
                books.append(f"📌 {row['title']} - {row['author']} ({row['кол_страниц']} стр.)")
        if books:
            bot.send_message(message.chat.id, "📖 **История прочитанных книг:**\n\n" + '\n'.join(books[:10]), parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "История пуста. Начни читать! 📚")
    else:
        bot.send_message(message.chat.id, "История пуста. Начни читать! 📚")

@bot.message_handler(commands=['grade'])
def grade_cmd(message):
    uid = message.from_user.id
    log_activity(uid, 'grade')
    bot.send_message(message.chat.id, "Напиши название книги, которую хочешь оценить:")

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен. Требуются права администратора.")
        return
    log_activity(uid, 'stats')
    users = set()
    if os.path.exists('uu.txt'):
        with open('uu.txt', 'r') as f:
            for line in f:
                if line.strip() and ':' in line:
                    users.add(line.split(':')[0])
    
    total_books = len(q)
    total_users = len(users)
    total_ratings = len(q[q['rating'] > 0])
    
    stats_text = (
        f"📊 **Статистика бота:**\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"📚 Всего книг: {total_books}\n"
        f"⭐ Оценено книг: {total_ratings}\n"
        f"📈 Книг с рейтингом > 0: {total_ratings}\n"
        f"📊 Средний рейтинг: {q['rating'].mean():.2f}\n\n"
        f"🧠 ML модель: TF-IDF + Cosine Similarity"
    )
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

@bot.message_handler(commands=['export'])
def export_cmd(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен.")
        return
    log_activity(uid, 'export')
    try:
        q.to_csv('data/books_export.csv', index=False, encoding='utf-8-sig')
        q.to_json('data/books_export.json', orient='records', force_ascii=False, indent=2)
        with open('data/books_export.csv', 'rb') as f:
            bot.send_document(message.chat.id, f)
        with open('data/books_export.json', 'rb') as f:
            bot.send_document(message.chat.id, f)
        bot.send_message(message.chat.id, "✅ Экспорт выполнен успешно!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка экспорта: {str(e)}")

@bot.message_handler(commands=['import'])
def import_cmd(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен.")
        return
    log_activity(uid, 'import')
    bot.send_message(message.chat.id, "Отправь CSV файл с книгами для импорта.")

@bot.message_handler(commands=['users'])
def users_cmd(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен.")
        return
    log_activity(uid, 'users')
    users = []
    if os.path.exists('uu.txt'):
        with open('uu.txt', 'r') as f:
            for line in f:
                if line.strip() and ':' in line:
                    users.append(line.split(':')[0])
    if users:
        bot.send_message(message.chat.id, f"👥 **Активные пользователи:**\n\n" + '\n'.join(users[:20]), parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Нет активных пользователей.")

@bot.message_handler(commands=['logs'])
def logs_cmd(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен.")
        return
    log_activity(uid, 'logs')
    if os.path.exists('logs/activity.log'):
        with open('logs/activity.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()[-20:]
        if lines:
            bot.send_message(message.chat.id, "📋 **Последние логи:**\n\n" + ''.join(lines), parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Логи пусты.")
    else:
        bot.send_message(message.chat.id, "Логи не найдены.")

@bot.message_handler(commands=['add_book'])
def add_book_cmd(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен.")
        return
    save_step(uid, 100)
    bot.send_message(message.chat.id, "Введите данные книги в формате:\nНазвание|Автор|Жанры (через запятую)|Страниц|Рейтинг")

@bot.message_handler(commands=['delete_book'])
def delete_book_cmd(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен.")
        return
    save_step(uid, 101)
    bot.send_message(message.chat.id, "Введите название книги для удаления:")

@bot.message_handler(commands=['update_book'])
def update_book_cmd(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен.")
        return
    save_step(uid, 102)
    bot.send_message(message.chat.id, "Введите название книги для обновления:")

@bot.message_handler(commands=['create_admin'])
def create_admin_cmd(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен.")
        return
    save_step(uid, 103)
    bot.send_message(message.chat.id, "Введите ID пользователя для добавления в админы:")

@bot.message_handler(commands=['drop_admin'])
def drop_admin_cmd(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен.")
        return
    save_step(uid, 104)
    bot.send_message(message.chat.id, "Введите ID пользователя для удаления из админов:")

def send_recommendations(message, recs):
    if not recs:
        bot.send_message(message.chat.id, "Не найдено подходящих книг. Попробуй изменить предпочтения.")
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 Новая подборка", callback_data="new_recommendation"))
    
    text = "📚 **Твои рекомендации (ML):**\n\n"
    for i, rec in enumerate(recs, 1):
        medal = ""
        if i == 1:
            medal = "🥇 "
        elif i == 2:
            medal = "🥈 "
        elif i == 3:
            medal = "🥉 "
        
        text += f"{medal}{i}. **{rec['title']}**\n"
        text += f"   ✍️ Автор: {rec['author']}\n"
        text += f"   📚 Жанр: {rec['genre']}\n"
        text += f"   📄 Страниц: {rec['pages']}\n"
        text += f"   {get_rating_stars(rec['rating'])}\n"
        text += f"   🎯 Совпадение: {rec['score']}%\n"
        text += f"   🤖 ML точность: {rec['ml_score']}%\n\n"
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id
    
    if call.data == "start_quiz":
        start_quiz(call.message)
    
    elif call.data == "change_prefs":
        start_quiz(call.message)
    
    elif call.data == "clear_prefs":
        save_pref(uid, None)
        bot.send_message(call.message.chat.id, "✅ Предпочтения очищены!")
    
    elif call.data == "new_recommendation":
        pref = get_pref(uid)
        if pref:
            parts = pref.split('|')
            if len(parts) == 4:
                prefs, mood, rating, volume = parts
                recs = ml_recommend(prefs.split(','), mood, rating, volume)
                send_recommendations(call.message, recs)
            else:
                bot.send_message(call.message.chat.id, "Ошибка данных. Пройди опрос заново.")
        else:
            bot.send_message(call.message.chat.id, "Сначала пройди опрос!")
    
    elif call.data == "genres_done":
        temp = get_temp(uid)
        genres = temp.get('genres', [])
        
        if not genres:
            bot.send_message(call.message.chat.id, "Выбери хотя бы один жанр!")
            return
        
        if len(genres) > 5:
            bot.send_message(call.message.chat.id, "Можно выбрать не более 5 жанров!")
            return
        
        save_step(uid, 2)
        save_temp(uid, temp)
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("😊 Веселое", callback_data="mood_веселое"),
            InlineKeyboardButton("😢 Грустное", callback_data="mood_грустное"),
            InlineKeyboardButton("😰 Напряженное", callback_data="mood_напряженное")
        )
        bot.send_message(call.message.chat.id, "Какое настроение хочешь получить от книги?", reply_markup=markup)
    
    elif call.data.startswith("mood_"):
        mood = call.data.split('_')[1]
        temp = get_temp(uid)
        temp['mood'] = mood
        save_temp(uid, temp)
        save_step(uid, 3)
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⭐ Только хиты", callback_data="rating_хиты"),
            InlineKeyboardButton("🆕 Готов читать новинки", callback_data="rating_новинки"),
            InlineKeyboardButton("🤷 Без разницы", callback_data="rating_безразницы")
        )
        bot.send_message(call.message.chat.id, "Важен ли для тебя рейтинг книги?", reply_markup=markup)
    
    elif call.data.startswith("rating_"):
        rating = call.data.split('_')[1]
        temp = get_temp(uid)
        temp['rating'] = rating
        save_temp(uid, temp)
        save_step(uid, 4)
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("📖 Маленькая (<200 стр.)", callback_data="volume_маленькая"),
            InlineKeyboardButton("📚 Средняя (200-400 стр.)", callback_data="volume_средняя"),
            InlineKeyboardButton("📕 Большая (>400 стр.)", callback_data="volume_большая"),
            InlineKeyboardButton("🤷 Без разницы", callback_data="volume_безразницы")
        )
        bot.send_message(call.message.chat.id, "Какой объем книги предпочитаешь?", reply_markup=markup)
    
    elif call.data.startswith("volume_"):
        volume = call.data.split('_')[1]
        temp = get_temp(uid)
        temp['volume'] = volume
        save_temp(uid, temp)
        
        prefs = temp.get('genres', [])
        mood = temp.get('mood', '')
        rating = temp.get('rating', '')
        volume = temp.get('volume', '')
        
        pref_str = f"{','.join(prefs)}|{mood}|{rating}|{volume}"
        save_pref(uid, pref_str)
        save_user_prefs(uid, pref_str)
        save_step(uid, 0)
        
        recs = ml_recommend(prefs, mood, rating, volume)
        send_recommendations(call.message, recs)
    
    elif call.data.startswith("rate_"):
        idx = int(call.data.split('_')[1])
        save_step(uid, 200 + idx)
        bot.send_message(call.message.chat.id, "Оцени книгу от 1 до 5:")
    
    elif call.data.startswith("add_history_"):
        idx = int(call.data.split('_')[2])
        row = q.iloc[idx]
        history = get_history(uid)
        if row['title'] not in history:
            history.append(row['title'])
            save_history(uid, history)
            bot.send_message(call.message.chat.id, f"✅ Добавлено в историю: {row['title']}")
        else:
            bot.send_message(call.message.chat.id, f"📖 Книга уже в истории!")
    
    elif call.data.startswith("genre_"):
        genre = call.data.split('_')[1]
        temp = get_temp(uid)
        if 'genres' not in temp:
            temp['genres'] = []
        if genre in temp['genres']:
            temp['genres'].remove(genre)
        else:
            temp['genres'].append(genre)
        save_temp(uid, temp)
        show_genres(call.message, uid)

def show_genres(message, uid):
    genres = get_all_genres()
    temp = get_temp(uid)
    selected = temp.get('genres', [])
    
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for g in genres[:15]:
        prefix = '✅ ' if g in selected else '⬜ '
        buttons.append(InlineKeyboardButton(f"{prefix}{g}", callback_data=f"genre_{g}"))
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("📌 Готово", callback_data="genres_done"))
    
    bot.send_message(message.chat.id, f"Выбери жанры (до 5):\nВыбрано: {', '.join(selected[:5]) if selected else 'пока ничего'}", reply_markup=markup)

def start_quiz(message):
    uid = message.from_user.id
    save_step(uid, 1)
    temp = {}
    save_temp(uid, temp)
    show_genres(message, uid)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    uid = message.from_user.id
    step = get_step(uid)
    text = message.text
    
    if text == '📚 Начать опрос':
        start_quiz(message)
    
    elif text == '🎲 Случайная книга':
        random_cmd(message)
    
    elif text == '🔄 Получить новую подборку':
        again_cmd(message)
    
    elif text == '👤 Профиль':
        profile_cmd(message)
    
    elif text == '📖 История':
        history_cmd(message)
    
    elif text == '⭐ Оценить книгу':
        grade_cmd(message)
    
    elif text == '📊 Статистика' and is_admin(uid):
        stats_cmd(message)
    
    elif text == '📤 Экспорт' and is_admin(uid):
        export_cmd(message)
    
    elif text == '📥 Импорт' and is_admin(uid):
        import_cmd(message)
    
    elif text == '👥 Пользователи' and is_admin(uid):
        users_cmd(message)
    
    elif text == '📋 Логи' and is_admin(uid):
        logs_cmd(message)
    
    elif step == 100 and is_admin(uid):
        try:
            parts = text.split('|')
            if len(parts) == 5:
                title, author, genres, pages, rating = parts
                new_row = pd.DataFrame({
                    'title': [title.strip()],
                    'author': [author.strip()],
                    'жанр': [genres.strip()],
                    'кол_страниц': [int(pages.strip())],
                    'rating': [float(rating.strip())]
                })
                global q
                q = pd.concat([q, new_row], ignore_index=True)
                q.to_excel('data/books.xlsx', index=False)
                train_ml_model()
                bot.send_message(message.chat.id, f"✅ Книга '{title}' добавлена и ML модель переобучена!")
                save_step(uid, 0)
            else:
                bot.send_message(message.chat.id, "❌ Ошибка формата! Используй: Название|Автор|Жанр|Страниц|Рейтинг")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
    
    elif step == 101 and is_admin(uid):
        title = text.strip()
        q_filtered = q[q['title'] != title]
        if len(q_filtered) < len(q):
            q = q_filtered
            q.to_excel('data/books.xlsx', index=False)
            train_ml_model()
            bot.send_message(message.chat.id, f"✅ Книга '{title}' удалена и ML модель переобучена!")
        else:
            bot.send_message(message.chat.id, f"❌ Книга '{title}' не найдена!")
        save_step(uid, 0)
    
    elif step == 102 and is_admin(uid):
        save_temp(uid, {'old_title': text.strip()})
        save_step(uid, 1021)
        bot.send_message(message.chat.id, "Введите новые данные книги в формате:\nНазвание|Автор|Жанр|Страниц|Рейтинг")
    
    elif step == 1021 and is_admin(uid):
        temp = get_temp(uid)
        old_title = temp.get('old_title', '')
        try:
            parts = text.split('|')
            if len(parts) == 5:
                title, author, genres, pages, rating = parts
                idx = q[q['title'] == old_title].index
                if not idx.empty:
                    q.at[idx[0], 'title'] = title.strip()
                    q.at[idx[0], 'author'] = author.strip()
                    q.at[idx[0], 'жанр'] = genres.strip()
                    q.at[idx[0], 'кол_страниц'] = int(pages.strip())
                    q.at[idx[0], 'rating'] = float(rating.strip())
                    q.to_excel('data/books.xlsx', index=False)
                    train_ml_model()
                    bot.send_message(message.chat.id, f"✅ Книга обновлена и ML модель переобучена!")
                else:
                    bot.send_message(message.chat.id, f"❌ Книга '{old_title}' не найдена!")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка формата!")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
        save_step(uid, 0)
    
    elif step == 103 and is_admin(uid):
        try:
            new_admin = int(text.strip())
            admins = []
            if os.path.exists('admin.txt'):
                with open('admin.txt', 'r') as f:
                    content = f.read().strip()
                    if content:
                        admins = content.split(',')
            if str(new_admin) not in admins:
                admins.append(str(new_admin))
                with open('admin.txt', 'w') as f:
                    f.write(','.join(admins))
                bot.send_message(message.chat.id, f"✅ Пользователь {new_admin} добавлен в админы!")
            else:
                bot.send_message(message.chat.id, "❌ Пользователь уже админ!")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
        save_step(uid, 0)
    
    elif step == 104 and is_admin(uid):
        try:
            drop_admin = int(text.strip())
            admins = []
            if os.path.exists('admin.txt'):
                with open('admin.txt', 'r') as f:
                    content = f.read().strip()
                    if content:
                        admins = content.split(',')
            if str(drop_admin) in admins:
                admins.remove(str(drop_admin))
                with open('admin.txt', 'w') as f:
                    f.write(','.join(admins))
                bot.send_message(message.chat.id, f"✅ Пользователь {drop_admin} удален из админов!")
            else:
                bot.send_message(message.chat.id, "❌ Пользователь не админ!")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
        save_step(uid, 0)
    
    elif step >= 200 and step < 300:
        try:
            rating = float(text.strip())
            if 1 <= rating <= 5:
                idx = step - 200
                if idx < len(q):
                    q.at[idx, 'rating'] = rating
                    q.to_excel('data/books.xlsx', index=False)
                    bot.send_message(message.chat.id, f"✅ Оценка {rating}⭐ сохранена!")
                else:
                    bot.send_message(message.chat.id, "❌ Книга не найдена!")
                save_step(uid, 0)
            else:
                bot.send_message(message.chat.id, "Оценка должна быть от 1 до 5!")
        except:
            bot.send_message(message.chat.id, "Введи число от 1 до 5!")
    
    elif text.startswith('/'):
        pass
    
    else:
        bot.send_message(message.chat.id, "Не понял. Используй кнопки меню или команды /help")

if __name__ == '__main__':
    print("🤖 Бот запущен с ML моделью!")
    print("🧠 Используется: TF-IDF + Cosine Similarity")
    print("📚 База книг: " + str(len(q)))
    print("Для остановки нажмите Ctrl+C")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
            continue