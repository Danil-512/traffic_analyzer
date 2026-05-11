using CollectorService;
using DotNetEnv;
using Microsoft.AspNetCore.Builder;

// Для запуска через докер нужно передавать переменные окружения через докеркомпоуз
// Передам три возможных варианта, подставится нужный
var envPaths = new[]
{
    "../../.env",           // Локальная разработка (из bin/Debug/net10.0/)
    ".env",              // Docker (файл скопирован в контейнер)
    "/app/.env"          // Docker (явный путь)
};
//
// Поиск подходящего пути к файлу с переменными окружения
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
//
if (!envLoaded)
{
    Console.WriteLine("ERROR! No .env file found, using environment variables from Docker/system");
}

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHostedService<Worker>();

//
// Добавление http сервера
//builder.Services.AddSingleton<HttpEndpoints>();

var host = builder.Build();

host.MapGet("/health", () => Results.Ok(new { status = "Healthy", timestamp = DateTime.UtcNow }));
/*
var httpEndpoints = host.Services.GetRequiredService<HttpEndpoints>();
var lifetime = host.Services.GetRequiredService<IHostApplicationLifetime>();
var healthTask = httpEndpoints.StartAsync(lifetime.ApplicationStopping);
*/

await host.RunAsync();
//await healthTask;
