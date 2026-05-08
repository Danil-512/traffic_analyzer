using System;
using System.Text.Json.Serialization;

public class Http
{
	public Http()
	{
	}

    [JsonPropertyName("ip")]
    public string Ip { get; set; }

    [JsonPropertyName("method")]
    public string Method { get; set; }

    [JsonPropertyName("uri")]
    public string Path { get; set; } // В Nginx это $request_uri

    [JsonPropertyName("status")]
    public int ResponseStatusCode { get; set; }

    [JsonPropertyName("user_agent")]
    public string UserAgent { get; set; }

    [JsonPropertyName("referer")]
    public string Referer { get; set; }

    // Эти поля пригодятся для анализа DoS/DDoS
    [JsonPropertyName("request_time")]
    public double RequestTime { get; set; }

    [JsonPropertyName("body_bytes_sent")]
    public int BodyBytesSent { get; set; }

    [JsonPropertyName("body")]
    public string Payload { get; set; }

    public void Met123121234()
    {
    }
}

