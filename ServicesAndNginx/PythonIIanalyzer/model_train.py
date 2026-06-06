import pickle
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_val_score, GridSearchCV
from feature_extractor import SQLInjectionFeatureExtractor
from preprocess import DataPreprocessor
import logging
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SQLInjectionTrainer:
    """Тренер модели для обнаружения SQL-инъекций"""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 15, 
                 use_grid_search: bool = False):
        self.model = None
        self.feature_extractor = SQLInjectionFeatureExtractor()
        self.preprocessor = DataPreprocessor()
        self.use_grid_search = use_grid_search
        self.training_history = {}
        
        # Параметры для Grid Search
        self.param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None]
        }
    
    def train(self, dataset_dir: str, file_patterns: list = None):
        """Обучение модели на датасетах"""
        logger.info("="*60)
        logger.info("НАЧАЛО ОБУЧЕНИЯ МОДЕЛИ")
        logger.info("="*60)
        
        # 1. Загрузка датасетов
        logger.info("Шаг 1: Загрузка датасетов...")
        logs, labels, metadata = self.preprocessor.load_dataset_from_files(
            dataset_dir, file_patterns
        )
        
        # Вывод статистики
        self.preprocessor.print_dataset_stats()
        
        # 2. Извлечение признаков
        logger.info("\nШаг 2: Извлечение признаков...")
        X = self.preprocessor.prepare_features(logs, self.feature_extractor)
        
        # 3. Разделение и масштабирование
        logger.info("\nШаг 3: Разделение и масштабирование данных...")
        data = self.preprocessor.split_and_scale(X, labels, test_size=0.2)
        
        # 4. Обучение модели
        logger.info("\nШаг 4: Обучение модели...")
        
        if self.use_grid_search:
            self.model = self._grid_search_train(data['X_train'], data['y_train'])
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced',
                n_jobs=-1
            )
            self.model.fit(data['X_train'], data['y_train'])
        
        # 5. Оценка модели
        self._evaluate_model(data)
        
        # 6. Сохранение истории обучения
        self.training_history = {
            'timestamp': datetime.now().isoformat(),
            'dataset_stats': self.preprocessor.dataset_stats,
            'model_params': self.model.get_params(),
            'feature_count': self.feature_extractor.get_feature_count(),
            'feature_names': self.feature_extractor.get_feature_names()
        }
        
        return self.model
    
    def _grid_search_train(self, X_train, y_train):
        """Обучение с подбором гиперпараметров"""
        logger.info("Выполняется Grid Search для поиска оптимальных параметров...")
        
        base_model = RandomForestClassifier(random_state=42, class_weight='balanced', n_jobs=-1)
        grid_search = GridSearchCV(
            base_model, self.param_grid, 
            cv=5, scoring='roc_auc', n_jobs=-1, verbose=1
        )
        grid_search.fit(X_train, y_train)
        
        logger.info(f"Лучшие параметры: {grid_search.best_params_}")
        logger.info(f"Лучший score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def _evaluate_model(self, data: dict):
        """Оценка качества модели"""
        logger.info("\n" + "="*50)
        logger.info("ОЦЕНКА КАЧЕСТВА МОДЕЛИ")
        logger.info("="*50)
        
        y_pred = self.model.predict(data['X_test'])
        y_pred_proba = self.model.predict_proba(data['X_test'])[:, 1]
        
        # Основные метрики
        accuracy = accuracy_score(data['y_test'], y_pred)
        precision = precision_score(data['y_test'], y_pred)
        recall = recall_score(data['y_test'], y_pred)
        f1 = f1_score(data['y_test'], y_pred)
        roc_auc = roc_auc_score(data['y_test'], y_pred_proba)
        
        logger.info(f"\n📊 Основные метрики:")
        logger.info(f"  Accuracy:  {accuracy:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall:    {recall:.4f}")
        logger.info(f"  F1-Score:  {f1:.4f}")
        logger.info(f"  ROC-AUC:   {roc_auc:.4f}")
        
        # Cross-validation
        logger.info(f"\n📈 Cross-validation (5-fold):")
        cv_scores = cross_val_score(self.model, data['X_train'], data['y_train'], cv=5, scoring='roc_auc')
        logger.info(f"  CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
        
        # Classification report
        logger.info(f"\n📋 Classification Report:")
        logger.info(f"\n{classification_report(data['y_test'], y_pred, target_names=['Normal', 'SQL Injection'])}")
        
        # Confusion matrix
        cm = confusion_matrix(data['y_test'], y_pred)
        logger.info(f"\n📊 Confusion Matrix:")
        logger.info(f"  TN={cm[0,0]}, FP={cm[0,1]}")
        logger.info(f"  FN={cm[1,0]}, TP={cm[1,1]}")
        
        # Feature importance
        feature_importance = self._analyze_feature_importance()
        
        # Сохраняем метрики
        self.training_history['metrics'] = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': roc_auc,
            'cv_scores_mean': cv_scores.mean(),
            'cv_scores_std': cv_scores.std(),
            'confusion_matrix': cm.tolist()
        }
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': roc_auc
        }
    
    def _analyze_feature_importance(self):
        """Анализ важности признаков"""
        feature_names = self.feature_extractor.get_feature_names()
        importance = self.model.feature_importances_
        
        # Сортировка по важности
        indices = np.argsort(importance)[::-1]
        
        logger.info(f"\n🎯 TOP-15 важных признаков:")
        logger.info("="*50)
        for i, idx in enumerate(indices[:15]):
            logger.info(f"{i+1:2d}. {feature_names[idx]:30s} : {importance[idx]:.4f}")
        
        # Сохраняем для истории
        feature_importance = {feature_names[idx]: float(importance[idx]) for idx in indices[:20]}
        self.training_history['feature_importance'] = feature_importance
        
        return feature_importance
    
    def save_model(self, model_path: str = 'model.pkl', 
                   scaler_path: str = 'scaler.pkl',
                   history_path: str = 'training_history.json'):
        """Сохранение модели, скейлера и истории обучения"""
        # Сохранение модели
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        logger.info(f"\n✅ Модель сохранена: {model_path}")
        
        # Сохранение скейлера
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.preprocessor.scaler, f)
        logger.info(f"✅ Скейлер сохранен: {scaler_path}")
        
        # Сохранение истории обучения
        with open(history_path, 'w') as f:
            json.dump(self.training_history, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ История обучения сохранена: {history_path}")
        
        # Сохранение feature extractor
        with open('feature_extractor.pkl', 'wb') as f:
            pickle.dump(self.feature_extractor, f)
        logger.info(f"✅ Feature extractor сохранен: feature_extractor.pkl")
    
    def plot_confusion_matrix(self, data: dict, save_path: str = 'confusion_matrix.png'):
        """Визуализация матрицы ошибок"""
        y_pred = self.model.predict(data['X_test'])
        cm = confusion_matrix(data['y_test'], y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Normal', 'SQL Injection'],
                    yticklabels=['Normal', 'SQL Injection'])
        plt.title('Confusion Matrix - SQL Injection Detection')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(save_path, dpi=100)
        logger.info(f"✅ Матрица ошибок сохранена: {save_path}")
        plt.close()
    
    def plot_feature_importance(self, save_path: str = 'feature_importance.png'):
        """Визуализация важности признаков"""
        feature_names = self.feature_extractor.get_feature_names()
        importance = self.model.feature_importances_
        
        indices = np.argsort(importance)[::-1][:20]
        
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(indices)), importance[indices], color='steelblue')
        plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
        plt.xlabel('Feature Importance')
        plt.title('Top-20 Feature Importance for SQL Injection Detection')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(save_path, dpi=100)
        logger.info(f"✅ График важности признаков сохранен: {save_path}")
        plt.close()


if __name__ == "__main__":
    # Путь к директории с датасетами
    DATASET_DIR = "logs"  # Папка с вашими логами
    
    # Создаем тренер и обучаем модель
    trainer = SQLInjectionTrainer(
        n_estimators=100,
        max_depth=15,
        use_grid_search=False  # Для быстрого обучения, при необходимости включите True
    )
    
    # Обучение на всех файлах
    model = trainer.train(
        dataset_dir=DATASET_DIR,
        file_patterns=["*.log"]  # Загружаем все log файлы
    )
    
    # Визуализация результатов
    # Для визуализации нужно сначала получить data из trainer.preprocessor
    # data = trainer.preprocessor.split_and_scale(...) - но у нас уже есть данные внутри trainer
    
    # Сохраняем модель
    trainer.save_model()
    
    # Создаем визуализации (если есть matplotlib и seaborn)
    try:
        # Повторно создаем data для визуализации
        logs, labels, _ = trainer.preprocessor.load_dataset_from_files(DATASET_DIR, ["*.log"])
        X = trainer.preprocessor.prepare_features(logs, trainer.feature_extractor)
        data = trainer.preprocessor.split_and_scale(X, labels, test_size=0.2)
        
        trainer.plot_confusion_matrix(data)
        trainer.plot_feature_importance()
    except Exception as e:
        logger.warning(f"Не удалось создать визуализации: {e}")