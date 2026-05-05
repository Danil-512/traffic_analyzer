# entrypoint.sh
#!/bin/sh
#----------------------------------------------------------------------------------------------------------------
# Скрипт для запуска Nginx с выполнением дополнительных действий
#
# Действия перед запуском, изменения в файле:
# Дата добавления  Автор      Функция
# 17.03.2026             Данил     Определение количества используемых ядер
#----------------------------------------------------------------------------------------------------------------

# Прерывание выполнения скрипта при любой ошибке
set -e
#
## ОПРЕДЕЛЕНИЕ МАКСИМАЛЬНО ДОПУСТИМОГО КОЛИЧЕСТВА ПРОЦЕССОВ
# Получение переменной из контейнера. Если не найдет, то 4
MAX_WORKERS="${NGINX_MAX_CPU:-4}"
#
echo "Максимальное количество процессов из .env: $MAX_WORKERS"
#
# ОПРЕДЕЛЕНИЕ ОГРАНИЧЕНИЙ CPU КОНТЕЙНЕРА
## Написано не мной. Надо будет тестировать и описывать
if [ -f /sys/fs/cgroup/cpu/cpu.cfs_quota_us ]; then
    echo "Обнаружена cgroup v1"
    #
    QUOTA=$(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us 2>/dev/null)
    PERIOD=$(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us 2>/dev/null)
    #
    # Проверяем, что лимиты установлены (QUOTA не равна -1, что означает "без ограничений")
    if [ -n "$QUOTA" ] && [ -n "$PERIOD" ] && [ "$QUOTA" -gt 0 ] && [ "$PERIOD" -gt 0 ]; then
        CPU_LIMIT=$((QUOTA / PERIOD))
        echo "CPU лимит из cgroup: $CPU_LIMIT ядер"
    else
        CPU_LIMIT=$(nproc)
        echo "Нет жёсткого лимита CPU, используем nproc: $CPU_LIMIT ядер"
    fi
#
# Проверяем наличие cgroup v2
elif [ -f /sys/fs/cgroup/cpu.max ]; then
    echo "Обнаружена cgroup v2"
    #
    CPU_MAX=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null | head -n1)
    QUOTA=$(echo $CPU_MAX | awk '{print $1}')
    PERIOD=$(echo $CPU_MAX | awk '{print $2}')
    #
    # Проверяем, что QUOTA не равна "max" (без ограничений)
    if [ "$QUOTA" != "max" ] && [ "$QUOTA" -gt 0 ] && [ "$PERIOD" -gt 0 ]; then
        CPU_LIMIT=$((QUOTA / PERIOD))
        echo "CPU лимит из cgroup v2: $CPU_LIMIT ядер"
    else
        CPU_LIMIT=$(nproc)
        echo "Нет жёсткого лимита CPU, используем nproc: $CPU_LIMIT ядер"
    fi
#
# Если cgroup не найдены
else
    echo "cgroup не обнаружены, используем nproc"
    CPU_LIMIT=$(nproc)
fi
#
# ПРИМЕНЕНИЕ МАКСИМАЛЬНОГО ОГРАНИЧЕНИЯ
# Сравнение максимального количества для контейнера с количеством из переменной
#   окружения
# Если количество из переменной окружения больше, возьму максимум контейнера
#   -gt - больше
if [ "$MAX_WORKERS" -gt "$CPU_LIMIT" ]; then
  WORKERS=$CPU_LIMIT
  #
  echo "Максимум для контейнера меньше, берем его $WORKERS"
else
  WORKERS=$MAX_WORKERS
  #
  echo "Максимум из переменной окружения меньше, берем его $WORKERS"
fi
#
# На случай если значение не будет положительным. -lt - меньше
if [ "$WORKERS" -lt 1 ]; then
  WORKERS=1
  #
  echo "Было определено не положительное, берем 1 WORKERS"
fi
#
# ГЕНЕРАЦИЯ КОНФИГУРАЦИИ И ЗАПУСК NGINX
echo "Начало генерации конфигурации nginx"
#
# Проверка наличия файла шаблона
if [ ! -f /etc/nginx/nginx.conf.template ]; then
  echo "Не найден файл nginx.conf.template!"
  #
  exit 1
fi
#
# СОЗДАНИЕ ФАЙЛА КОНФИГУРАЦИИ NGINX.CONF из NGINX.CONF.TEMPLATE
# Берем файл шаблон nginx.conf.template и заменяем в нем метку
#  WORKER_PROCESSES на полученное количество процессов. В будущем можно
#  будет добавить другие параметры. sed - потоковый редактор.
# “s|ШАБЛОН|ЗАМЕНА|g” - замена шаблона на передаваемый параметр
# \${} - экранирование. Без \ баш подумал бы что это переменная
# /etc/nginx/nginx.conf.template - входной файл
# /etc/nginx/nginx.conf - выходной генерируемый файл
sed "s|\${WORKER_PROCESSES}|$WORKERS|g" /etc/nginx/nginx.conf.template > /tmp/nginx.conf
#
# Подставить порт и хост из переменной окружения
sed -i "s|\${NGINX_PORT}|${NGINX_PORT:-5173}|g" /tmp/nginx.conf
sed -i "s|\${NGINX_HOST}|${NGINX_HOST:-localhost}|g" /tmp/nginx.conf
#
# Проверка, был ли создан nginx.conf
if [ ! -f /tmp/nginx.conf ]; then
  echo "Не создан файл nginx.conf!"
  #
  exit 1
fi
#
# Проверка корректности конфигурации
echo "Проверка конфигурации nginx"
nginx -t -c /tmp/nginx.conf
#
# Присвоение ответа переменной. $? - ответ последней команды
NGINX_CHECK=$?
# -ne - не равно
if [ $NGINX_CHECK -ne 0 ]; then
  echo "Ошибка в конфигурации nginx. Код ошибки: $NGINX_CHECK"
  # Завершаем с вовзратом кода ошибки
  exit $NGINX_CHECK
fi
#
echo "Конфигурация nginx корректна"
#
#
# ЗАПУСК NGINX
#   exec - замена текущего процесса новым (команда баш).
#   nginx - что будет запущено
#   -g - глобальная директива. Означает что следующие аргументы будут применены
#      поверх основного конфига
#   daemon off - команда nginx не уходить в фоновый режим, чтобы контейнер не
#      завершился
exec nginx -c /tmp/nginx.conf -g "daemon off;"