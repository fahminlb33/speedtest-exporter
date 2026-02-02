import os
import copy
import json
import shutil
import logging
import subprocess
from typing import Optional

from flask import Flask, Response


# custom prometheus gauge implementation
class Gauge:
    def __init__(self, metric_name: str, description: str, labels=None):
        self.metric_name = metric_name
        self.description = description
        self.current_value = None
        self.current_labels = (
            {k: None for k in labels} if labels is not None else dict()
        )

    def labels(self, **labels):
        self.current_labels = labels
        return self

    def set(self, value: float):
        self.current_value = value
        return self

    def render(self):
        render_str = (
            f"# HELP {self.metric_name} {self.description}\n"
            + f"# TYPE {self.metric_name} gauge"
        )
        if self.current_value is None:
            return render_str

        if len(self.current_labels) == 0:
            return f"{render_str}\n{self.metric_name} {self.current_value}"

        labels_str = ",".join(f'{k}="{v}"' for k, v in self.current_labels.items())
        return f"{render_str}\n{self.metric_name}{{{labels_str}}} {self.current_value}"


format_string = "level=%(levelname)s datetime=%(asctime)s %(message)s"
logging.basicConfig(encoding="utf-8", level=logging.DEBUG, format=format_string)

app = Flask("Speedtest-Exporter")

counter_labels = ["test_uuid", "server_id", "isp", "location", "country"]
counters = {
    "up": Gauge("speedtest_up", "Speedtest status whether the scrape worked"),
    # "packet_loss": Gauge(
    #     "speedtest_packet_loss", "Packet loss during Speedtest", counter_labels
    # ),
    "ping_latency": Gauge(
        "speedtest_ping_latency_milliseconds",
        "Ping in ms",
        counter_labels,
    ),
    "ping_jitter": Gauge(
        "speedtest_ping_jitter_milliseconds",
        "Jitter in ms",
        counter_labels,
    ),
    "upload_bandwidth": Gauge(
        "speedtest_upload_bandwidth_bits_per_second",
        "Upload bandwidth in bits/s",
        counter_labels,
    ),
    "upload_duration": Gauge(
        "speedtest_upload_milliseconds",
        "Upload duration in milliseconds",
        counter_labels,
    ),
    "upload_size": Gauge(
        "speedtest_upload_size_bytes",
        "Uploaded data size in bytes",
        counter_labels,
    ),
    "upload_latency": Gauge(
        "speedtest_upload_latency_milliseconds",
        "Upload latency in milliseconds",
        counter_labels,
    ),
    "upload_jitter": Gauge(
        "speedtest_upload_jitter_milliseconds",
        "Upload latency jitter in milliseconds",
        counter_labels,
    ),
    "download_bandwidth": Gauge(
        "speedtest_download_bandwidth_bits_per_second",
        "Download bandwidth in bits/s",
        counter_labels,
    ),
    "download_duration": Gauge(
        "speedtest_download_milliseconds",
        "Download duration in milliseconds",
        counter_labels,
    ),
    "download_size": Gauge(
        "speedtest_download_size_bytes",
        "Download data size in bytes",
        counter_labels,
    ),
    "download_latency": Gauge(
        "speedtest_download_latency_milliseconds",
        "Download latency in milliseconds",
        counter_labels,
    ),
    "download_jitter": Gauge(
        "speedtest_download_jitter_milliseconds",
        "Download latency jitter in milliseconds",
        counter_labels,
    ),
}


def render_metrics() -> str:
    metrics_str = ""
    if counters["up"].current_value == 0:
        metrics_str = counters["up"].render()
    else:
        metrics_str = "\n".join(gauge.render() for gauge in counters.values())

    return Response(metrics_str, mimetype="text/plain; charset=utf-8")


def run_test() -> Optional[str]:
    server_id = os.environ.get("SPEEDTEST_SERVER_ID")
    timeout = int(os.environ.get("SPEEDTEST_TIMEOUT", "300"))

    cmd = [
        "speedtest",
        "--format=json",
        "--progress=no",
        "--accept-license",
        "--accept-gdpr",
    ]
    if server_id:
        cmd.append(f"--server-id={server_id}")

    try:
        output = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        logging.debug(output.stdout)

        for line in output.stdout.split("\n"):
            if '{"type":"result"' in line:
                return line
    except subprocess.CalledProcessError as e:
        logging.error("Speedtest CLI Error occurred that was not in JSON format")
    except subprocess.TimeoutExpired:
        logging.error("Speedtest CLI process took too long to complete and was killed.")

    return None


@app.route("/metrics")
def metrics():
    output_json = run_test()
    if output_json is None:
        counters["up"].set(0)
        return render_metrics()

    result = json.loads(output_json)

    server_labels = {
        "isp": result["isp"],
        "test_uuid": result["result"]["id"],
        "server_id": result["server"]["id"],
        "server": result["server"]["name"],
        "location": result["server"]["location"],
        "country": result["server"]["country"],
        "host": result["server"]["host"],
        "ip": result["server"]["ip"],
    }

    counters["up"].set(1)
    # counters["packet_loss"].labels(**server_labels).set(result["packetLoss"])

    counters["ping_latency"].labels(**server_labels).set(result["ping"]["latency"])
    counters["ping_jitter"].labels(**server_labels).set(result["ping"]["jitter"])

    counters["upload_bandwidth"].labels(**server_labels).set(
        result["upload"]["bandwidth"] * 8  # conversion to bytes/sec
    )
    counters["upload_duration"].labels(**server_labels).set(result["upload"]["elapsed"])
    counters["upload_size"].labels(**server_labels).set(result["upload"]["bytes"])
    counters["upload_latency"].labels(**server_labels).set(
        result["upload"]["latency"]["iqm"]
    )
    counters["upload_jitter"].labels(**server_labels).set(
        result["upload"]["latency"]["jitter"]
    )

    counters["download_bandwidth"].labels(**server_labels).set(
        result["download"]["bandwidth"] * 8  # conversion to bytes/sec
    )
    counters["download_duration"].labels(**server_labels).set(
        result["download"]["elapsed"]
    )
    counters["download_size"].labels(**server_labels).set(result["download"]["bytes"])
    counters["download_latency"].labels(**server_labels).set(
        result["download"]["latency"]["iqm"]
    )
    counters["download_jitter"].labels(**server_labels).set(
        result["download"]["latency"]["jitter"]
    )

    return render_metrics()


@app.route("/health")
def health():
    message = ""

    if shutil.which("speedtest") is None:
        message = "Speedtest CLI binary not found in PATH"
        logging.error(message)
        return message, 500

    version_stdout = subprocess.run(
        ["speedtest", "--version"], capture_output=True, text=True
    )
    if "Speedtest by Ookla" not in version_stdout.stdout:
        message = "Speedtest CLI that is installed is not the official version."
        logging.error(message)
        return message, 500

    return "OK", 200


@app.route("/")
def home():
    return """
            <h1>Welcome to Speedtest Exporter!</h1>
            Navigate to <a href="/metrics">/metrics</a> to perform speedtest and return the metrics.<br/>
            Navigate to <a href="/health">/health</a> to check the exporter health.
            """
