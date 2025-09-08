# Speedtest Exporter

Yet another [Speedtest.net](https://www.speedtest.net/) exporter for Prometheus.

This project is heavily inspired by: [MiguelNdeCarvalho's](https://github.com/MiguelNdeCarvalho/speedtest-exporter) and [danopstech](https://github.com/danopstech/speedtest_exporter) exporter. I combined both project metrics and labels and added other metrics not exported by the original exporters.

## Usage

The recommended way to use this exporter is by using Docker. You can find the images in [Docker Hub](https://hub.docker.com/r/fahminlb33/speedtest-exporter).

```bash
docker run -p 9898:9898 fahminlb33/speedtest-exporter:1.0.2
```

### Prometheus Configuration

Every time you visit the `/metrics` endpoint, it will perform a speedtest. Therefore, it is not recommended to scrape it too rapidly. I recommend scraping every 1 hour. Also note that this exporter does not implement caching!

```yaml
scrape_configs
    - job_name: speedtest
      scrape_interval: 1h
      scrape_timeout:  15m
      static_configs:
        - targets: ['localhost:9989']
```

## Exported Metrics

```plain
# HELP speedtest_up Speedtest status whether the scrape worked
# TYPE speedtest_up gauge
speedtest_up 1.0
# HELP speedtest_packet_loss Packet loss during Speedtest
# TYPE speedtest_packet_loss gauge
speedtest_packet_loss{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 0.0
# HELP speedtest_ping_latency_milliseconds Ping in ms
# TYPE speedtest_ping_latency_milliseconds gauge
speedtest_ping_latency_milliseconds{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 3.168
# HELP speedtest_ping_jitter_milliseconds Jitter in ms
# TYPE speedtest_ping_jitter_milliseconds gauge
speedtest_ping_jitter_milliseconds{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 1.088
# HELP speedtest_upload_bandwidth_bytes_per_second Upload bandwidth in bytes/s
# TYPE speedtest_upload_bandwidth_bytes_per_second gauge
speedtest_upload_bandwidth_bytes_per_second{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 3.5562616e+07
# HELP speedtest_upload_milliseconds Upload duration in milliseconds
# TYPE speedtest_upload_milliseconds gauge
speedtest_upload_milliseconds{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 3601.0
# HELP speedtest_upload_size_bytes Uploaded data size in bytes
# TYPE speedtest_upload_size_bytes gauge
speedtest_upload_size_bytes{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 1.60076e+07
# HELP speedtest_upload_latency_milliseconds Upload latency in milliseconds
# TYPE speedtest_upload_latency_milliseconds gauge
speedtest_upload_latency_milliseconds{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 159.897
# HELP speedtest_upload_jitter_milliseconds Upload latency jitter in milliseconds
# TYPE speedtest_upload_jitter_milliseconds gauge
speedtest_upload_jitter_milliseconds{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 47.691
# HELP speedtest_download_bandwidth_bytes_per_second Download bandwidth in bytes/s
# TYPE speedtest_download_bandwidth_bytes_per_second gauge
speedtest_download_bandwidth_bytes_per_second{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 1.03809752e+08
# HELP speedtest_download_milliseconds Download duration in milliseconds
# TYPE speedtest_download_milliseconds gauge
speedtest_download_milliseconds{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 7810.0
# HELP speedtest_download_size_bytes Download data size in bytes
# TYPE speedtest_download_size_bytes gauge
speedtest_download_size_bytes{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 1.020208e+08
# HELP speedtest_download_latency_milliseconds Download latency in milliseconds
# TYPE speedtest_download_latency_milliseconds gauge
speedtest_download_latency_milliseconds{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 105.859
# HELP speedtest_download_jitter_milliseconds Download latency jitter in milliseconds
# TYPE speedtest_download_jitter_milliseconds gauge
speedtest_download_jitter_milliseconds{country="Indonesia",isp="PT. Telekomunikasi Indonesia",location="Jakarta",server_id="56632"} 31.592
```

## Grafana Dashboard

Coming soon!

## License

MIT License.
