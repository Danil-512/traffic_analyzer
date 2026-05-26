using CollectorService;
using DotNetEnv;
using CollectorService.RabbitMq;

// Загрузка .env файла
var envPaths = new[]
{
    "../../.env",           // Локальная разработка (из bin/Debug/net8.0/)
    ".env",                 // Docker (файл скопирован в контейнер)
    "/app/.env"             // Docker (явный путь)
};

bool envLoaded = false;
foreach (var path in envPaths)
{
    if (File.Exists(path))
    {
        Env.Load(path);
        Console.WriteLine($"Loaded .env from: {path}");
        envLoaded = true;
        break;
    }
}

if (!envLoaded)
{
    Console.WriteLine("INFO: No .env file found, using environment variables from Docker/system");
}

var builder = WebApplication.CreateBuilder(args);

// Регистрация отправителя сервиса для работы с брокером
builder.Services.AddScoped<IRabbitMqService, RabbitMqService>();

// Добавляем Worker как BackgroundService
builder.Services.AddHostedService<Worker>();

// Получаем порт из переменных окружения
var servicePort = Environment.GetEnvironmentVariable("SERVICE_PORT") ??
                  Environment.GetEnvironmentVariable("COLLECTOR_SERVICE_PORT") ??
                  "5011";

// Настройка Kestrel для HTTP healthcheck
builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(int.Parse(servicePort));
});

var app = builder.Build();

// Health check endpoint
app.MapGet("/health", () => Results.Ok(new
{
    status = "Healthy",
    timestamp = DateTime.UtcNow,
    port = servicePort
}));

// Запуск приложения
app.Run();