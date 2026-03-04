import os
import time
import asyncio
import structlog
from observability import init_observability, db_query_duration, external_api_duration

# Import observability from backend
import sys
sys.path.append('../../backend')
from backend.app.observability import init_observability

logger = structlog.get_logger()

class Worker:
    def __init__(self):
        self.running = True

    async def process_job(self, job_data: dict):
        """Process a background job"""
        job_id = job_data.get('id')
        job_type = job_data.get('type', 'unknown')

        logger.info("Processing job", job_id=job_id, job_type=job_type)

        try:
            # Simulate DB query
            with db_query_duration.labels(operation="select").time():
                # In real app, fetch job details from DB
                await asyncio.sleep(0.1)

            # Simulate external API call
            with external_api_duration.labels(service="external_service", method="POST").time():
                # In real app, call external API
                await asyncio.sleep(0.2)

            # Simulate processing
            await asyncio.sleep(1.0)

            logger.info("Job completed successfully", job_id=job_id, duration=1.3)
            return {"status": "completed", "result": "success"}

        except Exception as e:
            logger.error("Job failed", job_id=job_id, error=str(e))
            raise

    async def run(self):
        """Main worker loop"""
        logger.info("Worker starting")

        while self.running:
            try:
                # Simulate job queue polling
                # In real app, poll Redis/RabbitMQ for jobs
                job_data = {"id": "job-123", "type": "process_document"}

                if job_data:
                    await self.process_job(job_data)
                else:
                    await asyncio.sleep(5)  # No jobs, wait

            except Exception as e:
                logger.error("Worker error", error=str(e))
                await asyncio.sleep(10)  # Backoff on error

        logger.info("Worker stopping")

    def stop(self):
        self.running = False

if __name__ == "__main__":
    # Initialize observability
    init_observability(None, "worker")  # No FastAPI app for worker

    worker = Worker()

    try:
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        worker.stop()
        logger.info("Worker shutdown gracefully")
