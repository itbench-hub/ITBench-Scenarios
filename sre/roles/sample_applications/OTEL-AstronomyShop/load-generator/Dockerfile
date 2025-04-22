FROM ghcr.io/open-telemetry/demo:2.0.1-load-generator

RUN apt-get update && apt-get install -y sed

# To avoid triggering any calls to the recommendation component
# Changing the task weight from 3 to 0 for '/'
RUN sed -i '/@task(1)/{N;s/@task(1)\n    def index/@task(0)\n    def index/}' locustfile.py

# Changing the task weight from 3 to 0 for get_recommendations
RUN sed -i '/@task(3)/{N;s/@task(3)\n    def get_recommendations/@task(0)\n    def get_recommendations/}' locustfile.py

# Update the wait time from between(1, 10) to between(1, 5)
RUN sed -i 's/wait_time = between(1, 10)/wait_time = between(1, 5)/' locustfile.py

# Keep the original entrypoint
ENTRYPOINT ["locust", "--skip-log-setup"]
