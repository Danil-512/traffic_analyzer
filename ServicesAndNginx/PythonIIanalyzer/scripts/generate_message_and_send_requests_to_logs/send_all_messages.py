#!/usr/bin/env python3
# send_all_messages.py

import csv
import requests
import time
import json
from typing import List, Dict

class RequestSender:
    """Отправка всех запросов из датасета"""
    
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
        """Отправка запроса на регистрацию с текстом сообщения"""
        url = f"{self.base_url}/api/Auth/send-verification"
        
        # Очищаем текст для использования в username
        clean_text = message_text[:40].replace(' ', '_').replace('"', '').replace("'", '').replace('\n', '')
        
        payload = {
            "username": f"{clean_text}_{index}"[:50],
            "email": f"user_{index}@test.com",
            "password": "Test123456!",
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
    
    def load_all_messages(self, csv_file: str) -> List[Dict]:
        """Загрузка ВСЕХ сообщений из датасета"""
        messages = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                messages.append({
                    "text": row['text'],
                    "has_sql": row['has_sql_keywords'] == 'True',
                    "sql_words": row.get('sql_words', '')
                })
        return messages
    
    def send_all_batch(self, messages: List[Dict], delay: float = 0.1, batch_size: int = 100):
        """Отправка всех сообщений с прогрессом по батчам"""
        
        total = len(messages)
        sql_count = sum(1 for m in messages if m['has_sql'])
        
        print(f"\n🚀 Отправка ВСЕХ {total} сообщений...")
        print(f"   Из них с SQL: {sql_count} ({sql_count/total*100:.1f}%)")
        print("=" * 70)
        
        results = []
        success_count = 0
        
        for i, msg in enumerate(messages):
            result = self.send_register_request(msg['text'], i)
            results.append(result)
            
            if result['status_code'] == 200:
                success_count += 1
            
            # Показываем прогресс каждые 50 сообщений
            if (i + 1) % 50 == 0 or i == total - 1:
                msg_type = "🔴SQL" if msg['has_sql'] else "🟢NOR"
                status = "✅" if result['status_code'] == 200 else "❌"
                percent = ((i + 1) / total) * 100
                print(f"{status} [{i+1:4}/{total}] {percent:5.1f}% | {msg_type} | {msg['text'][:50]}... | HTTP {result['status_code']}")
            
            # Задержка
            time.sleep(delay)
        
        # Финальная статистика
        print("\n" + "=" * 70)
        print("📊 ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(f"  Всего запросов: {total}")
        print(f"  Успешно (200): {success_count} ({(success_count/total)*100:.1f}%)")
        print(f"  Ошибок: {total - success_count}")
        print(f"  SQL-запросов отправлено: {sum(1 for r in results if r['success'] and messages[r['index']]['has_sql'])}")
        
        return results

def main():
    print("=" * 70)
    print("ОТПРАВКА ВСЕХ ЗАПРОСОВ ИЗ ДАТАСЕТА (1000 сообщений)")
    print("=" * 70)
    
    sender = RequestSender()
    
    # Загружаем ВСЕ сообщения
    print("\n📥 Загрузка сообщений из english_dialogues_5percent.csv...")
    messages = sender.load_all_messages("english_dialogues_5percent.csv")
    
    if not messages:
        print("❌ Файл не найден!")
        return
    
    print(f"✅ Загружено {len(messages)} сообщений")
    print(f"  С SQL-словами: {sum(1 for m in messages if m['has_sql'])}")
    print(f"  Без SQL: {sum(1 for m in messages if not m['has_sql'])}")
    
    # Подтверждение
    print("\n⚠️  Будет отправлено 1000 запросов на сервер")
    confirm = input("Продолжить? (y/N): ")
    if confirm.lower() != 'y':
        print("Отменено")
        return
    
    # Отправка всех сообщений
    results = sender.send_all_batch(messages, delay=0.05)  # 50ms задержка
    
    # Сохраняем результаты
    with open('send_results_1000.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Результаты сохранены в send_results_1000.json")
    
    # Команды для просмотра логов
    print("\n📋 Для просмотра логов на сервере:")
    print("  tail -f ~/Git/Messenger/logs/access.log")
    print("\n  # Или через Docker:")
    print("  docker logs nginx_to_mess_container --tail 100 | grep 'send-verification'")
    print("\n  # Подсчет SQL-запросов в логах:")
    print("  docker logs nginx_to_mess_container 2>&1 | grep 'send-verification' | grep -c 'SELECT\\|INSERT\\|UPDATE\\|DELETE'")

if __name__ == "__main__":
    main()
