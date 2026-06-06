#!/usr/bin/env python3
# send_clean_requests.py

import csv
import requests
import time
import json
from typing import List, Dict

class CleanRequestSender:
    """Отправка чистых запросов (без SQL)"""
    
    def __init__(self):
        self.base_url = "https://tchk.site"
        self.session = requests.Session()
        
        self.headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/register",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "DNT": "1"
        }
    
    def send_register_request(self, message_text: str, index: int) -> Dict:
        """Отправка запроса на регистрацию"""
        url = f"{self.base_url}/api/Auth/send-verification"
        
        # Очищаем текст для username
        clean_text = message_text[:40].replace(' ', '_').replace('"', '').replace("'", '').replace('\n', '')
        
        payload = {
            "username": f"clean_{clean_text}_{index}"[:50],
            "email": f"clean_{index}@test.com",
            "password": "CleanPass123!",
            "device_info": "web"
        }
        
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=5)
            return {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "message_text": message_text,
                "index": index
            }
        except Exception as e:
            return {
                "status_code": 0,
                "success": False,
                "error": str(e),
                "message_text": message_text,
                "index": index
            }
    
    def load_messages(self, csv_file: str) -> List[Dict]:
        """Загрузка сообщений из датасета"""
        messages = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                messages.append({
                    "text": row['text'],
                    "sender": row.get('sender', 'unknown')
                })
        return messages
    
    def send_all(self, messages: List[Dict], delay: float = 0.05):
        """Отправка всех сообщений"""
        
        total = len(messages)
        
        print(f"\n🚀 Отправка {total} чистых сообщений (0% SQL)...")
        print("=" * 70)
        
        results = []
        success_count = 0
        
        for i, msg in enumerate(messages):
            result = self.send_register_request(msg['text'], i)
            results.append(result)
            
            if result['status_code'] == 200:
                success_count += 1
            
            # Прогресс каждые 50 сообщений
            if (i + 1) % 50 == 0 or i == total - 1:
                status = "✅" if result['status_code'] == 200 else "❌"
                percent = ((i + 1) / total) * 100
                print(f"{status} [{i+1:3}/{total}] {percent:5.1f}% | {msg['text'][:50]}... | HTTP {result['status_code']}")
            
            time.sleep(delay)
        
        # Статистика
        print("\n" + "=" * 70)
        print("📊 СТАТИСТИКА ОТПРАВКИ:")
        print(f"  Всего запросов: {total}")
        print(f"  Успешно (200): {success_count} ({(success_count/total)*100:.1f}%)")
        print(f"  Ошибок: {total - success_count}")
        
        return results

def main():
    print("=" * 70)
    print("ОТПРАВКА ЧИСТЫХ ЗАПРОСОВ (500 сообщений, 0% SQL)")
    print("=" * 70)
    
    sender = CleanRequestSender()
    
    # Загружаем датасет
    print("\n📥 Загрузка сообщений из english_clean_500.csv...")
    messages = sender.load_messages("english_clean_500.csv")
    
    if not messages:
        print("❌ Файл english_clean_500.csv не найден!")
        print("   Сначала запустите: python3 generate_english_clean.py")
        return
    
    print(f"✅ Загружено {len(messages)} чистых сообщений")
    print(f"  SQL-слов: 0 (100% безопасные)")
    
    # Подтверждение
    print(f"\n⚠️  Будет отправлено {len(messages)} запросов на сервер")
    confirm = input("Продолжить? (y/N): ")
    if confirm.lower() != 'y':
        print("Отменено")
        return
    
    # Отправка
    results = sender.send_all(messages, delay=0.05)
    
    # Сохраняем результаты
    with open('send_results_clean_500.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Результаты сохранены в send_results_clean_500.json")

if __name__ == "__main__":
    main()
