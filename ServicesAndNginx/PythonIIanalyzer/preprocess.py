import json
import re
from typing import List, Tuple, Dict, Any
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Предобработка данных для обучения с учетом метаданных из имен файлов"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.dataset_stats = {}
    
    def parse_filename_metadata(self, filename: str) -> Dict[str, Any]:
        """
        Парсинг метаданных из имени файла.
        Пример: access_backup_20260603_205232_1000_5proc_sql_noI.log
        """
        metadata = {
            'original_name': filename,
            'has_sql_context': False,
            'has_sql_injection': False,
            'percentage': None,
            'count': None,
            'type': 'unknown'
        }
        
        # Определение наличия SQL контекста
        if 'sql' in filename.lower():
            metadata['has_sql_context'] = True
            
        # Определение SQL инъекций
        if 'sqli' in filename.lower():
            metadata['has_sql_injection'] = True
            metadata['type'] = 'sql_injection'
        elif 'sql_noi' in filename.lower():
            metadata['has_sql_injection'] = False
            metadata['type'] = 'sql_context_no_injection'
        elif 'no_sql' in filename.lower():
            metadata['has_sql_context'] = False
            metadata['type'] = 'normal'
        
        # Извлечение процента из имени файла (например, 5proc, 85proc)
        percent_match = re.search(r'(\d+)proc', filename)
        if percent_match:
            metadata['percentage'] = int(percent_match.group(1))
        
        # Извлечение количества записей из имени файла
        count_match = re.search(r'_(\d+)_', filename)
        if count_match:
            metadata['count'] = int(count_match.group(1))
        
        # Определение специфичных типов
        if 'normal_use_no_sql' in filename:
            metadata['type'] = 'normal_traffic'
        elif 'raznoe_atack_no_sqlI' in filename:
            metadata['type'] = 'various_attacks_no_injection'
        elif 'sqlmap' in filename:
            metadata['type'] = 'sqlmap_automated'
            
        return metadata
    
    def load_dataset_from_files(self, directory: str, file_patterns: List[str] = None) -> Tuple[List[Dict], np.ndarray, List[Dict]]:
        """
        Загрузка датасетов из нескольких файлов с автоматической разметкой
        """
        all_logs = []
        all_labels = []
        all_metadata = []
        
        directory_path = Path(directory)
        
        # Если не указаны паттерны, загружаем все .log файлы
        if file_patterns is None:
            log_files = list(directory_path.glob('*.log'))
        else:
            log_files = []
            for pattern in file_patterns:
                log_files.extend(directory_path.glob(pattern))
        
        logger.info(f"Найдено {len(log_files)} файлов для загрузки")
        
        for log_file in log_files:
            metadata = self.parse_filename_metadata(log_file.name)
            logger.info(f"Загрузка файла: {log_file.name}")
            logger.info(f"  Метаданные: {metadata}")
            
            logs, labels = self._load_single_file(log_file, metadata)
            
            all_logs.extend(logs)
            all_labels.extend(labels)
            all_metadata.extend([metadata] * len(logs))
            
            # Сохраняем статистику по датасету
            self.dataset_stats[log_file.name] = {
                'metadata': metadata,
                'total_entries': len(logs),
                'sql_injection_count': sum(labels),
                'normal_count': len(labels) - sum(labels)
            }
            
            logger.info(f"  Загружено {len(logs)} записей, из них SQL инъекций: {sum(labels)}")
        
        all_labels = np.array(all_labels)
        logger.info(f"\nВсего загружено: {len(all_logs)} записей")
        logger.info(f"Баланс классов: 0 (normal)={len(all_labels)-sum(all_labels)}, 1 (sql_injection)={sum(all_labels)}")
        
        return all_logs, all_labels, all_metadata
    
    def _load_single_file(self, file_path: Path, metadata: Dict) -> Tuple[List[Dict], List[int]]:
        """
        Загрузка одного файла с автоматической разметкой на основе метаданных
        """
        logs = []
        labels = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f):
                if line.strip():
                    try:
                        # Парсим JSON строку
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                        
                        # Автоматическая разметка на основе метаданных файла
                        if metadata['type'] == 'normal_traffic':
                            # Нормальный трафик без SQL
                            label = 0
                        elif metadata['type'] == 'sql_injection':
                            # Файл с SQL инъекциями
                            label = 1
                        elif metadata['type'] == 'sql_context_no_injection':
                            # Есть SQL контекст, но нет инъекций
                            label = 0
                        elif metadata['type'] == 'normal':
                            label = 0
                        elif metadata['type'] == 'sqlmap_automated':
                            # SQLMap генерирует SQL инъекции
                            label = 1
                        elif metadata['type'] == 'various_attacks_no_injection':
                            # Разные атаки без SQL инъекций
                            label = 0
                        else:
                            # Если тип не определен, используем процент
                            if metadata.get('percentage') is not None:
                                # Для файлов с указанием процента (например, 85proc)
                                # Используем порог > 30% для определения как инъекции
                                label = 1 if metadata['percentage'] > 30 else 0
                            else:
                                label = 1 if metadata.get('has_sql_injection', False) else 0
                        
                        labels.append(label)
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Ошибка парсинга JSON в {file_path.name}:{line_num+1}: {e}")
                        continue
        
        return logs, labels
    
    def prepare_features(self, logs: List[dict], feature_extractor) -> np.ndarray:
        """Подготовка признаков"""
        features = []
        for i, log in enumerate(logs):
            if i % 1000 == 0:
                logger.info(f"Обработка признаков: {i}/{len(logs)}")
            features.append(feature_extractor.extract_from_log(log))
        
        X = np.array(features)
        logger.info(f"Матрица признаков создана: {X.shape}")
        return X
    
    def split_and_scale(self, X: np.ndarray, y: np.ndarray, 
                       test_size: float = 0.2, 
                       random_state: int = 42,
                       use_stratify: bool = True) -> dict:
        """Разделение данных и масштабирование"""
        
        stratify = y if use_stratify else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, 
            stratify=stratify, shuffle=True
        )
        
        logger.info(f"Разделение данных: train={len(X_train)}, test={len(X_test)}")
        logger.info(f"Train баланс: {np.bincount(y_train)}")
        logger.info(f"Test баланс: {np.bincount(y_test)}")
        
        # Масштабирование признаков
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.is_fitted = True
        
        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train,
            'y_test': y_test
        }
    
    def scale_features(self, features: np.ndarray) -> np.ndarray:
        """Масштабирование новых данных"""
        if not self.is_fitted:
            raise ValueError("Scaler не обучен. Сначала вызовите split_and_scale.")
        
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        return self.scaler.transform(features)
    
    def print_dataset_stats(self):
        """Вывод статистики по датасетам"""
        print("\n" + "="*60)
        print("СТАТИСТИКА ЗАГРУЖЕННЫХ ДАТАСЕТОВ")
        print("="*60)
        
        for filename, stats in self.dataset_stats.items():
            print(f"\n {filename}")
            print(f"   Тип: {stats['metadata']['type']}")
            print(f"   Всего записей: {stats['total_entries']}")
            print(f"   SQL инъекции: {stats['sql_injection_count']} ({stats['sql_injection_count']/stats['total_entries']*100:.1f}%)")
            print(f"   Нормальный трафик: {stats['normal_count']} ({stats['normal_count']/stats['total_entries']*100:.1f}%)")
            if stats['metadata'].get('percentage'):
                print(f"   Указанный процент: {stats['metadata']['percentage']}%")