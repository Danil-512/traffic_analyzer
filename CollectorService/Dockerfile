# Первый этап - сборка
FROM mcr.microsoft.com/dotnet/sdk:10.0-alpine AS build

WORKDIR /src

# Копируем файл проекта (теперь он в корне контекста сборки)
COPY CollectorService.csproj .

# Восстанавливаем зависимости
RUN dotnet restore "CollectorService.csproj"

# Копируем все остальные файлы
COPY . .

# Публикуем приложение
RUN dotnet publish "CollectorService.csproj" \
    -c Release \
    -o /app/publish \
    --self-contained false

# Второй этап - запуск
FROM mcr.microsoft.com/dotnet/aspnet:10.0-alpine AS final

# Аргументы для портов
ARG SERVICE_PORT=5011
ARG COLLECTOR_TCP_PORT=6000

# Установка необходимых пакетов
RUN apk add --no-cache tzdata icu-libs curl wget

# Настройки окружения
ENV TZ=Asia/Yekaterinburg
ENV DOTNET_RUNNING_IN_CONTAINER=true
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false
ENV ASPNETCORE_URLS=http://0.0.0.0:${SERVICE_PORT}

# Создаем пользователя
RUN addgroup -g 1000 -S appgroup && \
    adduser -u 1000 -S appuser -G appgroup

WORKDIR /app

# Копируем собранное приложение
COPY --from=build /app/publish .

# Меняем владельца
RUN chown -R appuser:appgroup /app

# Переключаемся на непривилегированного пользователя
USER appuser

# Экспортируем порты
EXPOSE ${SERVICE_PORT}
EXPOSE ${COLLECTOR_TCP_PORT}

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${SERVICE_PORT}/health || exit 1

# Запуск
ENTRYPOINT ["dotnet", "CollectorService.dll"]
