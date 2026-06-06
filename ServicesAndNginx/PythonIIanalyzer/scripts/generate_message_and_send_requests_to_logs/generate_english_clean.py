#!/usr/bin/env python3
# generate_english_clean.py

import random
import csv
from datetime import datetime
from typing import List, Dict

class CleanEnglishGenerator:
    """Генератор чистых английских диалогов (без SQL-слов)"""
    
    def __init__(self):
        # Полностью безопасные английские фразы (без SQL)
        self.safe_phrases = [
            # Приветствия и общие фразы
            "Hello! How are you doing today?",
            "Hey! Long time no see, how have you been?",
            "Good morning! Did you sleep well?",
            "Good evening! Hope you had a great day",
            "Hi there! Nice to see you again",
            
            # Вопросы о делах
            "What are your plans for the weekend?",
            "How was your day at work?",
            "Did you finish the project on time?",
            "What time are we meeting tomorrow?",
            "Are you coming to the party tonight?",
            
            # Обсуждение погоды
            "The weather is beautiful today, isn't it?",
            "I heard it's going to rain later",
            "It's so cold outside, don't forget your jacket",
            "Finally some sunshine after all that rain",
            "The temperature dropped significantly overnight",
            
            # Еда и рестораны
            "Have you tried the new Italian restaurant downtown?",
            "I'm craving pizza for dinner tonight",
            "What's your favorite coffee shop around here?",
            "The food at that place is absolutely amazing",
            "Let's grab lunch together someday this week",
            
            # Работа и учеба
            "I have a deadline coming up next Friday",
            "The meeting got moved to 3 PM instead",
            "Can you help me with this presentation?",
            "I need to finish this report by tomorrow",
            "My boss was really impressed with our work",
            
            # Хобби и развлечения
            "I started learning guitar last month",
            "Have you watched the latest Netflix series?",
            "What kind of music do you listen to?",
            "I love reading science fiction books",
            "Let's go hiking this weekend if the weather is nice",
            
            # Планы и приглашения
            "Would you like to go to the cinema tonight?",
            "I'm throwing a small party on Saturday",
            "Let's plan a trip somewhere next month",
            "We should hang out more often",
            "Do you want to grab a coffee after work?",
            
            # Личные вопросы
            "How is your family doing?",
            "Did you hear the latest news about the company?",
            "What do you think about the new policy?",
            "Are you feeling better today?",
            "I hope everything is going well for you",
            
            # Выражения эмоций
            "That's fantastic news! I'm so happy for you",
            "I'm really tired after such a long week",
            "This is so exciting, I can't wait",
            "I'm sorry to hear that, let me know if I can help",
            "What a wonderful surprise! Thank you so much",
            
            # Повседневные разговоры
            "I need to buy groceries after work",
            "My car broke down, so I'm taking the bus",
            "I finally cleaned my apartment today",
            "I'm thinking of adopting a pet soon",
            "This traffic is driving me crazy",
            
            # Дружеские советы
            "You should really take a break and relax",
            "Don't worry too much, everything will be fine",
            "Trust your instincts, you know what's best",
            "It's okay to make mistakes, that's how we learn",
            "Just be yourself and everything will work out",
            
            # Путешествия
            "I'm planning a trip to the beach next summer",
            "Have you ever been to Japan? I heard it's beautiful",
            "My favorite vacation was in the mountains",
            "I love exploring new cities and trying local food",
            "The flight was long but totally worth it",
            
            # Технологии (без SQL)
            "I just bought a new phone and it's amazing",
            "Can you recommend a good laptop for programming?",
            "I'm having trouble with my internet connection",
            "This app is really useful for organizing tasks",
            "The new software update fixed all the bugs",
            
            # Здоровье и фитнес
            "I've been going to the gym regularly lately",
            "Yoga helps me relax after a stressful day",
            "Drinking enough water is so important",
            "I'm trying to eat healthier this month",
            "Getting enough sleep makes a huge difference",
            
            # Новости и события
            "Did you see what happened in the news today?",
            "There's a new park opening downtown next week",
            "The concert was absolutely incredible last night",
            "I can't believe how fast this year is going by",
            "The museum has a new exhibition starting Friday"
        ]
        
        # Имена отправителей
        self.senders = [
            "Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", 
            "Hannah", "Ian", "Julia", "Kevin", "Laura", "Michael", "Nina", 
            "Oliver", "Patricia", "Quentin", "Rachel", "Steve", "Tina", 
            "Ursula", "Victor", "Wendy", "Xavier", "Yvonne", "Zack"
        ]
    
    def generate_message(self, msg_id: int) -> Dict:
        """Генерирует одно чистое сообщение"""
        
        text = random.choice(self.safe_phrases)
        sender = random.choice(self.senders)
        
        # Добавляем небольшие вариации для реалистичности
        if random.random() < 0.1:
            text = text.upper()
        elif random.random() < 0.05:
            text = f"{text}!!!"
        elif random.random() < 0.05:
            text = f"🤔 {text}"
        
        return {
            "id": msg_id,
            "text": text,
            "has_sql_keywords": False,
            "sql_words": "",
            "length": len(text),
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_dialogue(self, min_messages: int = 2, max_messages: int = 8) -> List[Dict]:
        """Генерирует диалог из нескольких сообщений"""
        
        num_messages = random.randint(min_messages, max_messages)
        dialogue = []
        
        for i in range(num_messages):
            message = self.generate_message(i)
            message["message_id"] = i
            dialogue.append(message)
        
        return dialogue
    
    def generate_dataset(self, num_messages: int = 500) -> List[Dict]:
        """Генерация датасета чистых сообщений"""
        
        dataset = []
        print(f"🎯 Генерация {num_messages} чистых сообщений (0% SQL)...")
        
        for i in range(num_messages):
            message = self.generate_message(i)
            dataset.append(message)
            
            if (i + 1) % 100 == 0:
                print(f"  Сгенерировано {i+1}/{num_messages} сообщений...")
        
        return dataset
    
    def save_to_csv(self, dataset: List[Dict], filename: str = "english_clean_500.csv"):
        """Сохраняет датасет в CSV"""
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'text', 'has_sql_keywords', 'sql_words', 'length', 'timestamp', 'sender'])
            writer.writeheader()
            writer.writerows(dataset)
        
        total = len(dataset)
        print(f"\n📊 СТАТИСТИКА:")
        print(f"  Всего сообщений: {total}")
        print(f"  С SQL-словами: 0 (0%)")
        print(f"  Полностью чистые: {total} (100%)")
        print(f"  Сохранено в: {filename}")
        
        return {"total": total, "sql_count": 0}

def main():
    print("=" * 70)
    print("ГЕНЕРАТОР ЧИСТЫХ АНГЛИЙСКИХ РАЗГОВОРОВ (0% SQL)")
    print("=" * 70)
    
    NUM_MESSAGES = 500
    
    print(f"\n📝 Параметры:")
    print(f"  Сообщений: {NUM_MESSAGES}")
    print(f"  SQL-слов: 0%")
    
    # Генерация
    generator = CleanEnglishGenerator()
    dataset = generator.generate_dataset(num_messages=NUM_MESSAGES)
    
    # Сохранение
    stats = generator.save_to_csv(dataset, "english_clean_500.csv")
    
    # Показываем примеры
    print("\n📝 ПРИМЕРЫ СГЕНЕРИРОВАННЫХ СООБЩЕНИЙ:")
    for i, example in enumerate(dataset[:10]):
        print(f"  {i+1}. {example['sender']}: {example['text'][:70]}...")
    
    print("\n✅ Готово! Файл: english_clean_500.csv")

if __name__ == "__main__":
    main()
