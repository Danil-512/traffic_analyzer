using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Text.Json;
using DotNetEnv;
using Microsoft.Extensions.Logging;

namespace CollectorService
{
    public class HttpEndpoints : IDisposable
    {
        private readonly HttpListener _httpListener;
        private readonly ILogger<HttpEndpoints> _logger;
        private readonly int _port;

        public HttpEndpoints(IConfiguration configuration, ILogger<HttpEndpoints> logger)
        {
            _logger = logger;
            _port = configuration.GetValue<int>("SERVICE_PORT", 5001);
            _httpListener = new HttpListener();
        }

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            // В Docker используем *, локально — localhost
            var isDocker = Environment.GetEnvironmentVariable("DOTNET_RUNNING_IN_CONTAINER") == "true";
            var host = isDocker ? "*" : "localhost";
            _httpListener.Prefixes.Add($"http://{host}:{_port}/");

            try
            {
                _httpListener.Start();
                _logger.LogInformation("Health endpoint listening on port {Port}", _port);

                while (!cancellationToken.IsCancellationRequested)
                {
                    var context = await _httpListener.GetContextAsync()
                        .WaitAsync(cancellationToken);

                    await HandleRequestAsync(context);
                }
            }
            catch (OperationCanceledException)
            {
                _logger.LogInformation("Health endpoint shutting down");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Health endpoint error");
            }
            finally
            {
                _httpListener.Close();
            }
        }

        private async Task HandleRequestAsync(HttpListenerContext context)
        {
            var path = context.Request.Url?.AbsolutePath;

            if (path == "/health")
            {
                var response = new
                {
                    status = "Healthy",
                    timestamp = DateTime.UtcNow
                };

                var json = JsonSerializer.Serialize(response);
                var buffer = System.Text.Encoding.UTF8.GetBytes(json);

                context.Response.StatusCode = 200;
                context.Response.ContentType = "application/json";
                context.Response.ContentLength64 = buffer.Length;
                await context.Response.OutputStream.WriteAsync(buffer);
            }
            else
            {
                context.Response.StatusCode = 404;
            }

            context.Response.Close();
        }

        public void Dispose()
        {
            _httpListener?.Close();
            (_httpListener as IDisposable)?.Dispose();
        }
    }
}
