using Npgsql;
using StackExchange.Redis;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;

namespace BlockedIpSyncService
{
    public class Worker(ILogger<Worker> logger) : BackgroundService
    {
        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            try
            {
                DotNetEnv.Env.Load();
                logger.LogInformation("Файл .env успешно прочитан и загружен в окружение.");
            }
            catch (Exception ex)
            {
                logger.LogWarning(ex, "Не удалось загрузить файл .env. Используются системные переменные или дефолтные значения.");
            }

            logger.LogInformation("Сервис запущен и запускает стартовую синхронизацию...");
            await DoSyncAsync(stoppingToken);

            try
            {
                string rabbitHost = Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_HOST") ?? "178.159.31.162";
                int rabbitPort = int.Parse(Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_PORT") ?? "5673");
                string rabbitUser = Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_USER") ?? "user_for_analyzer";
                string rabbitPass = Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_PASS") ?? "fgdadj231ejwej4@";
                string rabbitVHost = Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_VHOST") ?? "rabbitmq_analyzer";

                if (rabbitHost == "rabbitmq")
                {
                    rabbitHost = "178.159.31.162";
                }

                var factory = new ConnectionFactory()
                {
                    HostName = rabbitHost,
                    Port = rabbitPort,
                    UserName = rabbitUser,
                    Password = rabbitPass,
                    VirtualHost = rabbitVHost
                };

                using var rabbitConnection = factory.CreateConnection();
                using var rabbitChannel = rabbitConnection.CreateModel();

                string queueName = "redis_sync_commands";

                rabbitChannel.QueueDeclare(
                    queue: queueName,
                    durable: true,
                    exclusive: false,
                    autoDelete: false,
                    arguments: null);

                logger.LogInformation("Успешно подключились к RabbitMQ. Ожидаем команды в очереди '{queue}'...", queueName);

                var consumer = new EventingBasicConsumer(rabbitChannel);
                consumer.Received += async (model, ea) =>
                {
                    var body = ea.Body.ToArray();
                    var message = Encoding.UTF8.GetString(body);

                    logger.LogInformation("Получена команда из RabbitMQ: {msg}", message);

                    if (message.ToLower() == "sync" || message.ToLower() == "redis_restart")
                    {
                        logger.LogInformation("Запуск повторной синхронизации по запросу из очереди...");
                        await DoSyncAsync(stoppingToken);
                    }

                    rabbitChannel.BasicAck(ea.DeliveryTag, false);
                };

                rabbitChannel.BasicConsume(queue: queueName, autoAck: false, consumer: consumer);

                while (!stoppingToken.IsCancellationRequested)
                {
                    await Task.Delay(1000, stoppingToken);
                }
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Критическая ошибка при работе с RabbitMQ. Прослушивание команд недоступно.");
            }
        }

        private async Task DoSyncAsync(CancellationToken stoppingToken)
        {
            try
            {
                string postgresHost = Environment.GetEnvironmentVariable("POSTGRESQL_HOST") ?? "178.159.31.162";
                string postgresPort = Environment.GetEnvironmentVariable("POSTGRESQL_PORT") ?? "34572";
                string postgresDatabase = Environment.GetEnvironmentVariable("POSTGRESQL_DATABASE") ?? "db_analyzer";
                string postgresUser = Environment.GetEnvironmentVariable("POSTGRESQL_USERNAME") ?? "db_analyzer_user";
                string postgresPassword = Environment.GetEnvironmentVariable("POSTGRESQL_PASSWORD") ?? "Hds232^2Sd";

                if (postgresHost == "postgres")
                {
                    postgresHost = "178.159.31.162";
                }

                string connectionString = $"Host={postgresHost};Port={postgresPort};Database={postgresDatabase};Username={postgresUser};Password={postgresPassword}";

                string redisHost = Environment.GetEnvironmentVariable("REDIS_HOST") ?? "178.159.31.162";
                string redisPort = Environment.GetEnvironmentVariable("REDIS_PORT") ?? "6379";
                string redisPassword = Environment.GetEnvironmentVariable("REDIS_PASSWORD") ?? "dafej1@*jW";

                if (redisHost == "redis")
                {
                    redisHost = "178.159.31.162";
                }

                string redisConnectionString = $"{redisHost}:{redisPort},password={redisPassword},allowAdmin=true";

                await using var connection = new NpgsqlConnection(connectionString);
                await connection.OpenAsync(stoppingToken);
                logger.LogInformation("Подключение к PostgreSQL успешно");

                using ConnectionMultiplexer redis = await ConnectionMultiplexer.ConnectAsync(redisConnectionString);
                IDatabase redisDb = redis.GetDatabase();
                logger.LogInformation("Подключение к Redis успешно");

                string sql = "SELECT DISTINCT source_ip::text FROM blocked_connections";

                await using var command = new NpgsqlCommand(sql, connection);
                await using var reader = await command.ExecuteReaderAsync(stoppingToken);

                int counter = 0;
                while (await reader.ReadAsync(stoppingToken))
                {
                    string ip = reader.GetString(0);

                    if (ip.Contains('/'))
                    {
                        ip = ip.Split('/')[0];
                    }

                    string redisKey = $"blocked_ip:{ip}";
                    await redisDb.StringSetAsync(redisKey, "1");
                    logger.LogInformation("IP записан в Redis: {ip}", ip);
                    counter++;
                }

                logger.LogInformation("Чтение PostgreSQL завершено. Всего перенесено IP: {count}", counter);

                //вывод строк из редиса
                logger.LogInformation("--------------------------------------------------");
                logger.LogInformation("ЗАПРОС ВСЕХ КЛЮЧЕЙ ИЗ REDIS ДЛЯ ПРОВЕРКИ ТЗ...");

                var endpoint = redis.GetEndPoints().First();
                var server = redis.GetServer(endpoint);

                var keys = server.Keys(pattern: "blocked_ip:*").ToList();

                logger.LogInformation("Найдено ключей в Redis: {keysCount}", keys.Count);
                foreach (var key in keys)
                {
                    string? val = await redisDb.StringGetAsync(key);
                    logger.LogInformation(" -> Ключ в Redis: [ {key} ], Значение (EXISTS результат): [ {val} ]", key, val);
                }
                logger.LogInformation("--------------------------------------------------");
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Ошибка во время выполнения синхронизации данных");
            }
        }
    }
}