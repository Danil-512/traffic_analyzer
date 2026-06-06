#!/usr/bin/env python3
# generate_normal_sql_dialogues_fixed.py

import random
import csv
import json
from datetime import datetime, timedelta
from typing import List, Dict

class SQLDialogueGenerator:
    """Генератор реалистичных диалогов с SQL-подобными словами"""
    
    def __init__(self):
        self.sql_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP',
            'UNION', 'JOIN', 'WHERE', 'FROM', 'INTO', 'TABLE', 'DATABASE',
            'INDEX', 'VIEW', 'TRIGGER', 'PROCEDURE', 'FUNCTION', 'TRANSACTION',
            'BEGIN', 'COMMIT', 'ROLLBACK', 'GRANT', 'REVOKE', 'BACKUP'
        ]
        
        # Безопасные контексты использования SQL-слов
        self.contexts = [
            "обсуждает запрос", "спрашивает про синтаксис", "объясняет коллеге",
            "пишет комментарий в коде", "обучает новичка", "проводит код-ревью",
            "документирует базу данных", "отвечает на форуме", "исправляет ошибку"
        ]
        
        self.users = [
            "Алексей", "Марина", "Дмитрий", "Елена", "Сергей", "Анна", "Игорь",
            "Светлана", "Павел", "Ольга", "Максим", "Владимир", "Татьяна", "Андрей",
            "Наталья", "Николай", "Михаил", "Юлия", "Александр", "Кристина", "Евгений"
        ]
        
        self.dialog_templates = self._init_dialog_templates()
        
    def _init_dialog_templates(self) -> List[tuple]:
        """Инициализация шаблонов диалогов (все строки, без кортежей)"""
        return [
            # SELECT диалоги
            ("Нужно SELECT все поля из таблицы users, но только активных", "Как правильно написать WHERE условие?"),
            ("SELECT * FROM orders WHERE date > '2024-01-01'", "Добавь еще сортировку по дате DESC"),
            ("Я написал SELECT name, email FROM customers", "А GROUP BY нужен? Нет, просто выборка"),
            ("SELECT COUNT(*) даст общее количество строк", "Добавь WHERE status = 'active' для фильтрации"),
            ("В SELECT можно использовать DISTINCT для уникальных значений", "Ага, чтобы убрать дубликаты"),
            ("Как оптимизировать SELECT запрос?", "Используй индексы и не выбирай лишние поля"),
            ("SELECT * FROM huge_table тормозит", "Укажи конкретные поля, а не звездочку"),
            
            # INSERT диалоги
            ("INSERT INTO logs (user_id, action) VALUES (1, 'login')", "Не забудь про timestamp"),
            ("Как сделать INSERT новых записей из другой таблицы?", "Используй INSERT INTO ... SELECT ..."),
            ("INSERT в таблицу с 10 миллионами строк", "Добавь индексы перед вставкой"),
            ("Можно ли INSERT сразу несколько строк?", "Да, VALUES (1,'a'), (2,'b'), (3,'c')"),
            
            # UPDATE диалоги
            ("UPDATE users SET last_login = NOW()", "Всегда добавляй WHERE, иначе обновишь всех!"),
            ("UPDATE products SET price = price * 1.1", "WHERE id IN (1,2,3) для выборочного обновления"),
            ("UPDATE слишком медленный", "Создай временную таблицу для массового обновления"),
            
            # DELETE диалоги
            ("DELETE FROM temp_table удалит все данные", "WHERE условие обязательно!"),
            ("DELETE FROM logs WHERE date < '2024-01-01'", "Сначала сделай SELECT, проверь что удаляешь"),
            ("TRUNCATE TABLE быстрее DELETE?", "Да, но нельзя откатить изменения"),
            
            # CREATE диалоги
            ("CREATE TABLE new_table (id INT PRIMARY KEY)", "Добавь еще поля name и created_at"),
            ("CREATE INDEX idx_email на ускорит поиск", "Для больших таблиц это важно"),
            ("CREATE VIEW показывает только нужные поля", "Полезно для безопасности данных"),
            
            # ALTER/DROP диалоги
            ("ALTER TABLE users ADD COLUMN phone VARCHAR(20)", "Проверь, нет ли такого поля уже"),
            ("DROP TABLE old_backup удалит таблицу безвозвратно", "Сначала сделай BACKUP!"),
            ("ALTER TABLE нужно всегда проверять", "Да, можно потерять данные"),
            
            # JOIN диалоги
            ("UNION объединяет результаты двух SELECT", "А UNION ALL сохраняет дубликаты"),
            ("Как работает JOIN?", "INNER JOIN возвращает только совпадающие записи"),
            ("LEFT JOIN включает все записи из левой таблицы", "Даже если нет совпадений в правой"),
            ("WHERE и HAVING - в чем разница?", "WHERE фильтрует строки, HAVING - группы"),
            
            # Транзакции
            ("BEGIN TRANSACTION начинает транзакцию", "Не забудь COMMIT или ROLLBACK"),
            ("ROLLBACK отменяет все изменения", "Полезно при ошибках"),
            ("COMMIT фиксирует изменения в БД", "Делай после проверки данных"),
            ("ACID свойства важны для надежности", "Atomicity, Consistency, Isolation, Durability"),
            
            # Общие обсуждения
            ("Где можно посмотреть план выполнения запроса?", "EXPLAIN перед SELECT покажет"),
            ("Как добавить комментарий в SQL?", "-- для однострочного, /* */ для многострочного"),
            ("Какие типы JOIN существуют?", "INNER, LEFT, RIGHT, FULL OUTER и CROSS"),
            ("Что такое первичный ключ?", "Уникальный идентификатор записи в таблице"),
            ("Внешний ключ связывает таблицы", "Обеспечивает ссылочную целостность"),
            ("Индексы ускоряют чтение, но замедляют запись", "Нужно найти баланс")
        ]
    
    def _get_random_message_pair(self) -> tuple:
        """Получение случайной пары сообщений (всегда строки)"""
        message1, message2 = random.choice(self.dialog_templates)
        return message1, message2
    
    def generate_dialogue(self, min_messages: int = 5, max_messages: int = 15) -> Dict:
        """Генерация одного диалога"""
        num_messages = random.randint(min_messages, max_messages)
        messages = []
        current_time = datetime.now() - timedelta(hours=random.randint(0, 48))
        
        for i in range(num_messages):
            # Выбираем случайных пользователей
            user1 = random.choice(self.users)
            user2 = random.choice([u for u in self.users if u != user1])
            message_text = random.choice(self.dialog_templates)[i % 2]  # Чередуем сообщения
            
            # Проверяем наличие SQL-слов
            has_sql = any(kw in message_text.upper() for kw in self.sql_keywords)
            sql_words_found = [kw for kw in self.sql_keywords if kw in message_text.upper()]
            
            messages.append({
                "sender": user1 if i % 2 == 0 else user2,
                "text": message_text,
                "timestamp": current_time.isoformat(),
                "has_sql_keywords": has_sql,
                "sql_words_present": sql_words_found
            })
            
            current_time += timedelta(seconds=random.randint(10, 300))
        
        return {
            "dialogue_id": random.randint(10000, 99999),
            "message_count": len(messages),
            "messages": messages,
            "contains_sql_keywords": any(m["has_sql_keywords"] for m in messages),
            "context": random.choice(self.contexts)
        }
    
    def generate_dataset(self, num_dialogues: int = 50000) -> List[Dict]:
        """Генерация датасета диалогов"""
        dataset = []
        for i in range(num_dialogues):
            dialogue = self.generate_dialogue()
            dataset.append(dialogue)
            
            if (i + 1) % 5000 == 0:
                print(f"  Сгенерировано {i+1:,} диалогов...")
        
        return dataset

class FlattenedDialogueDataset:
    """Преобразование диалогов в плоский формат для ML"""
    
    @staticmethod
    def flatten_dialogues(dialogues: List[Dict]) -> List[Dict]:
        """Преобразует диалоги в отдельные сообщения"""
        flattened = []
        msg_id = 0
        for dialogue in dialogues:
            for message in dialogue["messages"]:
                flattened.append({
                    "dialogue_id": dialogue["dialogue_id"],
                    "message_id": msg_id,
                    "sender": message["sender"],
                    "text": message["text"],
                    "timestamp": message["timestamp"],
                    "has_sql_keywords": message["has_sql_keywords"],
                    "sql_words": "|".join(message["sql_words_present"]) if message["sql_words_present"] else "",
                    "dialogue_context": dialogue["context"],
                    "is_malicious": 0  # Все сообщения безопасны
                })
                msg_id += 1
        return flattened
    
    @staticmethod
    def save_to_csv(data: List[Dict], filename: str):
        """Сохранение в CSV формат"""
        if not data:
            print("⚠️ Нет данных для сохранения")
            return
        
        fieldnames = list(data[0].keys())
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✅ Сохранено {len(data)} записей в {filename}")

def main():
    print("=" * 70)
    print("ГЕНЕРАТОР НОРМАЛЬНЫХ ДИАЛОГОВ С SQL-ЛЕКСИКОЙ (ИСПРАВЛЕННЫЙ)")
    print("=" * 70)
    
    # Параметры генерации
    NUM_DIALOGUES = 50000  # 50,000 диалогов
    
    print(f"\n🎯 Цель: сгенерировать {NUM_DIALOGUES:,} диалогов")
    print("⏳ Начинаем генерацию...\n")
    
    # Генерация диалогов
    generator = SQLDialogueGenerator()
    dialogues = generator.generate_dataset(num_dialogues=NUM_DIALOGUES)
    
    print(f"\n✅ Сгенерировано {len(dialogues):,} диалогов")
    
    # Подсчет общего количества сообщений
    total_messages = sum(len(d["messages"]) for d in dialogues)
    print(f"📊 Общее количество сообщений: {total_messages:,}")
    
    # Преобразование в плоский формат
    print("\n🔄 Преобразование в формат для ML...")
    flattener = FlattenedDialogueDataset()
    flat_data = flattener.flatten_dialogues(dialogues)
    
    # Сохранение в CSV
    print("💾 Сохранение датасета...")
    flattener.save_to_csv(flat_data, 'normal_sql_dialogues.csv')
    
    # Дополнительная статистика
    print("\n📊 СТАТИСТИКА ДАТАСЕТА:")
    print(f"  • Диалогов: {len(dialogues):,}")
    print(f"  • Сообщений: {len(flat_data):,}")
    print(f"  • Уникальных отправителей: {len(set(m['sender'] for m in flat_data))}")
    sql_dialogues = sum(1 for d in dialogues if d['contains_sql_keywords'])
    print(f"  • Диалогов с SQL-словами: {sql_dialogues}")
    
    # Показываем примеры
    print("\n📝 ПРИМЕРЫ СГЕНЕРИРОВАННЫХ ДИАЛОГОВ:")
    for i, dialogue in enumerate(dialogues[:3]):
        print(f"\n--- ДИАЛОГ #{dialogue['dialogue_id']} (контекст: {dialogue['context']}) ---")
        for msg in dialogue['messages'][:5]:
            print(f"  {msg['sender']}: {msg['text']}")
        if len(dialogue['messages']) > 5:
            print(f"  ... и еще {len(dialogue['messages']) - 5} сообщений")
    
    # Сохраняем также в JSON для разнообразия
    with open('normal_sql_dialogues_sample.json', 'w', encoding='utf-8') as f:
        json.dump(dialogues[:1000], f, ensure_ascii=False, indent=2)
    print("\n✅ Сохранен sample из 1000 диалогов в JSON формате")
    
    print("\n" + "=" * 70)
    print("🎉 ДАТАСЕТ ГОТОВ К ИСПОЛЬЗОВАНИЮ!")
    print("=" * 70)
    print(f"📁 CSV файл: normal_sql_dialogues.csv")
    print(f"📁 JSON sample: normal_sql_dialogues_sample.json")
    print(f"💾 Размер CSV: ~{len(str(flat_data)) / 1024 / 1024:.1f} MB")
    print("\n💡 Поля в датасете:")
    print("  • dialogue_id - ID диалога")
    print("  • message_id - ID сообщения")
    print("  • sender - отправитель")
    print("  • text - текст сообщения")
    print("  • has_sql_keywords - есть ли SQL-слова (True/False)")
    print("  • sql_words - конкретные найденные SQL-слова")
    print("  • is_malicious - всегда 0 (безопасно)")

if __name__ == "__main__":
    main()
