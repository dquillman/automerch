from printful_client import get_store_metrics

def run():
    metrics = get_store_metrics()
    print(f"Metrics: {metrics}")
