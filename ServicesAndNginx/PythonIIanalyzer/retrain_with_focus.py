# retrain_with_focus.py
"""Дообучение модели с фокусом на классические SQL инъекции"""
import numpy as np
from model_train import SQLInjectionTrainer

# Создаем тренер с более чувствительными параметрами
trainer = SQLInjectionTrainer(
    n_estimators=200,      # Больше деревьев
    max_depth=20,          # Глубже деревья
    use_grid_search=True   # Автоподбор параметров
)

# Обучаем модель
trainer.train(
    dataset_dir="logs",
    file_patterns=["*.log"]
)

# Сохраняем
trainer.save_model()

print(" Модель переобучена с улучшенными параметрами")