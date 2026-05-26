namespace CollectorService
{
    public class Worker(ILogger<Worker> logger) : BackgroundService
    {
        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            logger.LogInformation("Collector Worker Service started");

            while (!stoppingToken.IsCancellationRequested)
            {
                // Здесь будет реальная логика (чтение из TCP/очереди)
                await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
            }

            /*
            while (!stoppingToken.IsCancellationRequested)
            {
                if (logger.IsEnabled(LogLevel.Information))
                {
                    logger.LogInformation("Worker running at: {time}", DateTimeOffset.Now);
                }
                await Task.Delay(1000, stoppingToken);
            }
            */
        }
    }
}
