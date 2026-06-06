#!/usr/bin/env python3
# generate_logs_only.py

import requests
import csv
import random
import time
import json
from datetime import datetime
from typing import List, Dict

class LogGenerator:
    """Генератор запросов для сбора логов (без реальной регистрации)"""
    
    def __init__(self):
        self.base_url = "https://tchk.site"
        self.session = requests.Session()
        
        # Заголовки как у реального браузера
        self.headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/register",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "DNT": "1",
            "Connection": "keep-alive"
        }
    
    def send_register_request(self, username: str, email: str, password: str) -> Dict:
        """Отправка запроса на регистрацию (только для логов)"""
        url = f"{self.base_url}/api/Auth/send-verification"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "device_info": "web"
        }
        
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=5)
            return {
                "status_code": response.status_code,
                "success": True,
                "payload": payload
            }
        except Exception as e:
            return {
                "status_code": 0,
                "success": False,
                "error": str(e),
                "payload": payload
            }
    
    def load_messages_from_csv(self, csv_file: str, limit: int = None) -> List[Dict]:
        """Загрузка сообщений из датасета"""
        messages = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if limit and i >= limit:
                        break
                    messages.append({
                        "text": row.get('text', ''),
                        "has_sql": row.get('has_sql_keywords', 'False'),
                        "sender": row.get('sender', 'unknown')
                    })
            return messages
        except FileNotFoundError:
            print(f"❌ Файл {csv_file} не найден")
            return []
    
    def generate_requests_from_messages(self, messages: List[Dict], delay: float = 0.1):
        """Генерация запросов из сообщений датасета"""
        
        print(f"\n🚀 Генерация {len(messages)} запросов для логов...")
        print("=" * 70)
        
        results = []
        for i, msg in enumerate(messages):
            # Используем текст сообщения как username/email для разнообразия
            # Но обрезаем, чтобы не было слишком длинно
            short_text = msg['text'][:30].replace(' ', '_').replace('"', '').replace("'", "")
            
            username = f"user_{i}_{short_text}"[:50]
            email = f"{username}@test.com"[:50]
            password = "Test123456!"
            
            result = self.send_register_request(username, email, password)
            results.append(result)
            
            # Определяем тип запроса по наличию SQL-слов
            sql_type = "SQL_KEYWORDS" if msg['has_sql'] == 'True' else "NORMAL"
            
            status = "✅" if result['status_code'] == 200 else "❌"
            print(f"{status} [{i+1}/{len(messages)}] {sql_type:13} | {msg['text'][:50]}...")
            
            time.sleep(delay)
        
        # Статистика
        success_count = sum(1 for r in results if r['status_code'] == 200)
        print("\n" + "=" * 70)
        print("📊 СТАТИСТИКА ЗАПРОСОВ:")
        print(f"  Всего запросов: {len(results)}")
        print(f"  Успешно (200): {success_count} ({(success_count/len(results))*100:.1f}%)")
        print(f"  С SQL-словами: {sum(1 for m in messages if m['has_sql'] == 'True')}")
        print(f"  Без SQL: {sum(1 for m in messages if m['has_sql'] == 'False')}")
        
        print("\n💡 Логи записаны в Nginx:")
        print("  • Смотрите: docker logs nginx_to_mess_container")
        print("  • Или: cat /var/log/nginx/access.log")

def main():
    print("=" * 70)
    print("ГЕНЕРАТОР ЗАПРОСОВ ДЛЯ СБОРА ЛОГОВ")
    print("=" * 70)
    
    generator = LogGenerator()
    
    # Загружаем сообщения из датасета
    print("\n📥 Загрузка сообщений из датасета...")
    messages = generator.load_messages_from_csv("normal_sql_dialogues.csv", limit=100)
    
    if not messages:
        print("❌ Датасет не найден, используем тестовые сообщения")
        messages = [
            {"text": "SELECT id FROM users WHERE id = 1", "has_sql": "True", "sender": "user1"},
            {"text": "Привет! Как дела?", "has_sql": "False", "sender": "user2"},
            {"text": "INSERT INTO logs VALUES ('test', NOW())", "has_sql": "True", "sender": "user1"},
            {"text": "Что делаешь сегодня вечером?", "has_sql": "False", "sender": "user2"},
            {"text": "DELETE FROM temp WHERE created_at < NOW()", "has_sql": "True", "sender": "user1"},
        ] * 20  # Повторяем для объема
        print(f"  Используем {len(messages)} тестовых сообщений")
    else:
        print(f"  Загружено {len(messages)} сообщений")
    
    # Генерируем запросы
    generator.generate_requests_from_messages(messages, delay=0.1)
    
    print("\n" + "=" * 70)
    print("✅ ГОТОВО!")
    print("\n📋 Чтобы посмотреть логи:")
    print("  docker logs nginx_to_mess_container --tail 100")
    print("  # Или смотрите JSON логи:")
    print("  docker logs nginx_to_mess_container 2>&1 | grep 'api/Auth/send-verification'")

if __name__ == "__main__":
    main()
