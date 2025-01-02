import time
import psutil
import logging
from video_summarizer import find_engaging_scenes, extract_and_combine_clips

# Setup logging
logging.basicConfig(filename='video_summarizer_performance.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Monitor resources function
def monitor_resources(process, duration=1):
    """Monitor CPU and memory usage of the process."""
    memory_usage = process.memory_info().rss / (1024 * 1024)  # in MB
    cpu_usage = process.cpu_percent(interval=duration)
    return memory_usage, cpu_usage

if __name__ == "__main__":
    # Sample inputs for testing
    video_path = "sample_video.mp4"  # Path to a sample video file
    plot_text = "A thrilling adventure with mystery and heroics."  # Placeholder plot text
    output_path = "output/summary_video.mp4"
    output_path1 = "output/summary_video_with_captions.mp4"
    cap_path = "output/summary_video.srt"

    # Initialize process monitoring
    process = psutil.Process()

    # Task: Find engaging scenes
    logging.info("Starting scene detection")
    start_time = time.time()

    scenes = find_engaging_scenes(video_path, max_duration=20, plot_text=plot_text)

    elapsed_time = time.time() - start_time
    memory_usage, cpu_usage = monitor_resources(process)
    logging.info(f"Scene detection completed: {len(scenes)} scenes found")
    logging.info(f"Time taken: {elapsed_time:.2f} seconds")
    logging.info(f"Memory usage: {memory_usage:.2f} MB")
    logging.info(f"CPU usage: {cpu_usage:.2f}%")

    # Task: Extract and combine clips
    if scenes:
        logging.info("Starting video summarization")
        start_time = time.time()

        try:
            extract_and_combine_clips(video_path, output_path, output_path1, cap_path, scenes, None, plot_text)
        except Exception as e:
            logging.error(f"Error during video summarization: {str(e)}")

        elapsed_time = time.time() - start_time
        memory_usage, cpu_usage = monitor_resources(process)
        logging.info(f"Video summarization completed")
        logging.info(f"Time taken: {elapsed_time:.2f} seconds")
        logging.info(f"Memory usage: {memory_usage:.2f} MB")
        logging.info(f"CPU usage: {cpu_usage:.2f}%")

    else:
        logging.warning("No scenes detected for summarization.")

    logging.info("Performance evaluation completed.")
