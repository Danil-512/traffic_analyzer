# Dockerfile nginx
FROM openresty/openresty:1.25.3.1-alpine
# Образ nginx с LuaJIT для выполнения логики, работы с бд и тп
# OpenResty - это полноценная веб-платформа, полученная путем встраивания интерпритатора LuaJIT в ядро nginx
# Позвояет писать логику прямо в конфиге nginx.conf на языке Lua
#
# Установка curl - используется в Healthcheck
# Установка пакетного менеджера для OpenResty
# Плюс установка пакета для работы с Redis
RUN apk add --no-cache curl openresty-opm && \
    opm get openresty/lua-resty-redis
#
# Установить рабочую директорию, относительно которой будут выполняться команды 
# по типу run, copy, cmd
WORKDIR /etc/nginx
#
# Скопировать файлы nginx.conf и security_headers.conf в контейнер
# Сразу изменить владельца файлов на nginx - стандартно существующего 
# пользователя, от лица которого будут производиться все действия (chown - change 
# owner, то есть сменить владельца. Первый аргумент - новый владелец, второй 
# аргумент - новая группа. Имя пользователя и имя группы одно, тк для сервисных 
# аккаунтов их обычно создают одноименными).
# nginx.conf.template - шаблон для формирования nginx.conf в entrypoint.sh
# nginx_healthcheck.sh - запуск хилтчека
#
COPY --chown=nginx:nginx nginx.conf.template ./nginx.conf.template
COPY --chown=nginx:nginx nginx_healthcheck.sh ./nginx_healthcheck.sh
COPY --chown=nginx:nginx security_headers.conf ./
#
# Аналогичное копирование файлов конфигурации сервисов
COPY --chown=nginx:nginx conf.d/*.conf ./conf.d/
#
# Создание директории для Lua скриптов
RUN mkdir -p /etc/nginx/lua && \
    chown -R nginx:nginx /etc/nginx/lua
#
# Копирование Lua скриптов в контейнер
COPY --chown=nginx:nginx lua/*.lua ./lua/
#
# Блок создания необходимых директорий внутри контейнера - кэш, информация о 
# процессах nginx (пид), логи (логи смонтирую вне контейнера в файле компоуза)
# RUN выполняет команды во время сборки контейнера
# Сначала создать директорию для кэша. Тег -p позволяет создать все дерево 
# директорий целиком, а не создавать отдельно каждый раз по папке.
RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
    # Для всех созданных директорий изменить владельцев и группы
    # Флаг -R означает рекурсивный режим, то есть применить к папке и всему 
    # возможному содержимому на любой глубине вложенности
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/run && \
    chown -R nginx:nginx /var/log/nginx && \
    # Создать файл, куда nginx будет записывать пид (идентификатор своего процесса)
    # Нужен, чтобы его можно было по нему останавливать, перезапускать и проверять 
    # статус 
    touch /var/run/nginx.pid && \
    chown nginx:nginx /var/run/nginx.pid
#
# Скопировать entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
# Сделать его исполняемым
RUN chmod +x /entrypoint.sh
# Сделать исполняемым nginx_healthcheck.sh
RUN chmod +x /etc/nginx/nginx_healthcheck.sh
#
# Сменить пользователя перед хилтчеком
USER nginx
#
# Базовый Healthcheck. Будет каждые 30 секунд проверять, жив ли контейнер.
# Если контейнер вернёт ошибку 3 раза подряд, ему присвоиться статус unhealthy и 
# уже какие-то средства вне контейнера будут его перезапускать
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD /etc/nginx/nginx_healthcheck.sh
#
# Команды CMD будут выполняться при запуске контейнера
# deamon off - указание nginx работать не в фоне. Процессы в линуксе работаю в фоне # или на переднем плане (захватывают терминал). Nginx как и некоторые процессы по 
# типу ssh стандартно работают в фоне. Но если nginx будет работать в фоне, то докер 
# подумает что контейнер завершился и остановит его. Поэтому, nginx должен 
# работать не в фоне
#CMD ["nginx", "-g", "daemon off;"]
# Запуск через скрипт с определением параметров и формированием конфигурации
ENTRYPOINT ["/entrypoint.sh"]
# Т.к. запуск через скрипт, то CMD пустой
CMD []
