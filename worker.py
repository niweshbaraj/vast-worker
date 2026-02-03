import base64
from vastai_sdk import Worker, WorkerConfig, HandlerConfig, LogActionConfig, BenchmarkConfig

# Model server runs on port 8000 inside the container
MODEL_SERVER_URL = "http://127.0.0.1"
MODEL_SERVER_PORT = 8000
MODEL_LOG_FILE = "/var/log/model.log"


def workload(payload):
    # cost ~ image size
    return len(payload["image"]) / 50000


def benchmark_generator() -> dict:
    """Generate benchmark payload - minimal base64 data"""
    return {"image": base64.b64encode(b"test").decode("utf-8")}

worker_config = WorkerConfig(
    model_server_url=MODEL_SERVER_URL,
    model_server_port=MODEL_SERVER_PORT,
    model_log_file=MODEL_LOG_FILE,

    handlers=[
        HandlerConfig(
            route="/process",
            allow_parallel_requests=False,
            max_queue_time=60.0,
            # workload_calculator=lambda p: 1.0,
            workload_calculator=workload,
            benchmark_config=BenchmarkConfig(
                generator=benchmark_generator,
                runs=4,
                concurrency=1,
            ),
        ),
    ],

    log_action_config=LogActionConfig(
        on_load=["Model Loaded Successfully"],
        on_error=["CRITICAL:", "Traceback (most recent call last):"],
        on_info=["Loading ONNX Model"],
    ),
)

if __name__ == "__main__":
    Worker(worker_config).run()