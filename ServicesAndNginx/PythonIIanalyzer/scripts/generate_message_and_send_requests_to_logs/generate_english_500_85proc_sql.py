#!/usr/bin/env python3
# generate_sql_injections.py

import random
import csv
from datetime import datetime
from typing import List, Dict

class SQLInjectionGenerator:
    """Генератор сообщений с SQL-инъекциями (85%)"""
    
    def __init__(self, injection_percent: float = 85.0):
        self.injection_percent = injection_percent
        
        # Реальные SQL-инъекции (вредоносные)
        self.sql_injections = [
            # Классические инъекции
            "' OR '1'='1",
            "' OR 1=1 --",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin' --",
            "' OR 'x'='x",
            "1' OR '1' = '1'",
            "' OR 1=1#",
            "1; DROP TABLE products",
            "' UNION SELECT username, password FROM users --",
            
            # Обход аутентификации
            "admin' OR '1'='1' --",
            "' OR 1=1 LIMIT 1 --",
            "'=' 'OR'",
            "' OR '1'='1'/*",
            "admin'--",
            "' OR 1=1 -- ",
            "') OR ('1'='1",
            "1' OR '1' = '1' LIMIT 1 --",
            
            # Union-based инъекции
            "' UNION SELECT null, username, password FROM users --",
            "' UNION ALL SELECT 1,2,3,4,5 --",
            "' UNION SELECT column_name FROM information_schema.columns --",
            "1' UNION SELECT @@version --",
            "' UNION SELECT database() --",
            
            # Time-based инъекции
            "1' AND SLEEP(5) --",
            "' OR (SELECT*FROM(SELECT(SLEEP(5)))a) --",
            "1' WAITFOR DELAY '00:00:05' --",
            
            # Error-based инъекции
            "1' AND extractvalue(1, concat(0x7e, database())) --",
            "' AND 1=CONVERT(int, @@version) --",
            "1' AND updatexml(1, concat(0x7e, version()), 1) --",
            
            # Boolean-based инъекции
            "1' AND '1'='1",
            "1' AND '1'='2",
            "' AND 1=1 --",
            "' AND 1=2 --",
            
            # Stacked queries
            "1'; INSERT INTO users VALUES ('hacker', 'pass') --",
            "1'; UPDATE users SET password = 'hacked' WHERE username = 'admin' --",
            "1'; DELETE FROM logs WHERE id = 1 --",
            
            # Более сложные инъекции
            "'; EXEC xp_cmdshell('dir') --",
            "1' OR EXISTS(SELECT * FROM users WHERE username='admin') --",
            "' OR ASCII(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)) > 100 --",
            "1' AND CASE WHEN (SELECT COUNT(*) FROM users) > 100 THEN SLEEP(5) ELSE 0 END --",
            
            # Обход фильтров
            "' Oorr 1=1 --",
            "' O/**/R 1=1 --",
            "'%20OR%201=1%20--",
            "'+OR+1=1+--",
            "' || '1' == '1",
            "1%27%20OR%20%271%27=%271",
            
            # Second-order инъекции
            "admin' --",
            "'; INSERT INTO logs (message) VALUES ('SQL injection') --",
            "'; CALL proc_inject() --",
            "1'; SELECT pg_sleep(5) --"
        ]
        
        # Нормальные английские фразы (15%)
        self.normal_phrases = [
            "Hello! How are you today?",
            "What are your plans for the weekend?",
            "The weather is really nice outside",
            "Can you send me the photos from yesterday?",
            "Thanks for your help, I really appreciate it",
            "Sorry, I'm busy right now, can't talk",
            "Let's meet for coffee tomorrow morning",
            "Did you watch the latest movie?",
            "I need to finish this project by Friday",
            "What's your favorite restaurant in town?",
            "Happy birthday! Hope you have a great day",
            "I'm going to the gym later, want to join?",
            "Have you seen the new update? It's amazing",
            "Can you give me a call when you're free?",
            "The traffic was terrible this morning",
            "I just bought a new laptop, it's awesome",
            "What time does the meeting start?",
            "Don't forget to bring your laptop tomorrow",
            "The food at that place is delicious",
            "I'm learning a new programming language"
        ]
        
        # Имена отправителей
        self.senders = ["Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Hannah"]
    
    def generate_message(self, msg_id: int) -> Dict:
        """Генерирует одно сообщение (85% SQL-инъекции)"""
        
        # Определяем тип сообщения
        is_injection = random.random() < (self.injection_percent / 100)
        
        if is_injection:
            text = random.choice(self.sql_injections)
            sql_words_found = ["SQL_INJECTION"]
            message_type = "injection"
        else:
            text = random.choice(self.normal_phrases)
            sql_words_found = []
            message_type = "normal"
        
        # Добавляем вариации для инъекций
        if is_injection and random.random() < 0.3:
            text = text.upper()
        
        sender = random.choice(self.senders)
        
        return {
            "id": msg_id,
            "text": text,
            "is_injection": is_injection,
            "message_type": message_type,
            "sql_words": "|".join(sql_words_found) if sql_words_found else "",
            "length": len(text),
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_dataset(self, num_messages: int = 500) -> List[Dict]:
        """Генерация датасета сообщений"""
        
        dataset = []
        print(f"🎯 Генерация {num_messages} сообщений (инъекции: {self.injection_percent}%)...")
        
        for i in range(num_messages):
            message = self.generate_message(i)
            dataset.append(message)
            
            if (i + 1) % 100 == 0:
                print(f"  Сгенерировано {i+1}/{num_messages} сообщений...")
        
        return dataset
    
    def save_to_csv(self, dataset: List[Dict], filename: str = "sql_injections_85percent.csv"):
        """Сохраняет датасет в CSV"""
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'text', 'is_injection', 'message_type', 'sql_words', 'length', 'timestamp', 'sender'])
            writer.writeheader()
            writer.writerows(dataset)
        
        total = len(dataset)
        injection_count = sum(1 for m in dataset if m['is_injection'])
        
        print(f"\n📊 СТАТИСТИКА ДАТАСЕТА:")
        print(f"  Всего сообщений: {total}")
        print(f"  SQL-инъекции: {injection_count} ({injection_count/total*100:.1f}%)")
        print(f"  Нормальные: {total - injection_count} ({(total-injection_count)/total*100:.1f}%)")
        print(f"  Сохранено в: {filename}")
        
        return {"total": total, "injection_count": injection_count}

def main():
    print("=" * 70)
    print("ГЕНЕРАТОР СООБЩЕНИЙ С SQL-ИНЪЕКЦИЯМИ (85%)")
    print("=" * 70)
    
    NUM_MESSAGES = 500
    INJECTION_PERCENT = 85.0
    
    print(f"\n📝 Параметры:")
    print(f"  Сообщений: {NUM_MESSAGES}")
    print(f"  SQL-инъекции: {INJECTION_PERCENT}%")
    print(f"  Нормальные: {100 - INJECTION_PERCENT}%")
    
    # Генерация
    generator = SQLInjectionGenerator(injection_percent=INJECTION_PERCENT)
    dataset = generator.generate_dataset(num_messages=NUM_MESSAGES)
    
    # Сохранение
    stats = generator.save_to_csv(dataset, "sql_injections_85percent.csv")
    
    # Показываем примеры
    print("\n📝 ПРИМЕРЫ СООБЩЕНИЙ:")
    print("  --- НОРМАЛЬНЫЕ (15%) ---")
    normal_examples = [m for m in dataset if not m['is_injection']][:5]
    for ex in normal_examples:
        print(f"    • {ex['text'][:70]}")
    
    print("\n  --- SQL-ИНЪЕКЦИИ (85%) ---")
    injection_examples = [m for m in dataset if m['is_injection']][:10]
    for ex in injection_examples:
        print(f"    • {ex['text'][:70]}")
    
    print("\n✅ Готово! Файл: sql_injections_85percent.csv")

if __name__ == "__main__":
    main()
