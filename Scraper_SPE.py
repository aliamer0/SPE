import time
import psutil
import logging
from Scraper import Scraper

# Setup logging
logging.basicConfig(filename='performance.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Performance monitoring function
def monitor_resources(process, duration=1):
    """Monitor CPU and memory usage of the process."""
    memory_usage = process.memory_info().rss / (1024 * 1024)  # in MB
    cpu_usage = process.cpu_percent(interval=duration)
    return memory_usage, cpu_usage

# Main performance evaluation
if __name__ == "__main__":
    # Initialize scraper
    scraper = Scraper(host='localhost', user='ali', password='456430', database='movies02',
                      user_agent= "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

    # Track performance of specific tasks
    tasks = [
        ("populate_database_movies", scraper.populate_database_movies),
    ]

    # Start monitoring
    process = psutil.Process()
    overall_start_time = time.time()

    for task_name, task_function in tasks:
        logging.info(f"Starting task: {task_name}")

        # Monitor time
        start_time = time.time()

        try:
            task_function()
        except Exception as e:
            logging.error(f"Error during {task_name}: {str(e)}")

        elapsed_time = time.time() - start_time
        memory_usage, cpu_usage = monitor_resources(process)

        # Log performance metrics
        logging.info(f"Task {task_name} completed.")
        logging.info(f"Time taken: {elapsed_time:.2f} seconds")
        logging.info(f"Memory usage: {memory_usage:.2f} MB")
        logging.info(f"CPU usage: {cpu_usage:.2f}%")

    # Overall performance summary
    overall_elapsed_time = time.time() - overall_start_time
    overall_memory_usage, overall_cpu_usage = monitor_resources(process)

    logging.info("--- Overall Performance Summary ---")
    logging.info(f"Total execution time: {overall_elapsed_time:.2f} seconds")
    logging.info(f"Total memory usage: {overall_memory_usage:.2f} MB")
    logging.info(f"Average CPU usage: {overall_cpu_usage:.2f}%")

    # Clean up
    scraper.quit()
