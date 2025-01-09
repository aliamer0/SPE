import time
import psutil
import logging
import cProfile
import pstats
import io
import matplotlib.pyplot as plt
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

# Profile a function using cProfile and generate stats
def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    # Save profiling stats to a file
    with open(f"{func.__name__}_profile.txt", "w") as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.sort_stats("cumulative")
        stats.print_stats()

    # Display stats using snakeviz
    stats.dump_stats(f"{func.__name__}_profile.prof")
    print(f"Profiling complete for {func.__name__}. Use snakeviz to visualize: snakeviz {func.__name__}_profile.prof")
    return result

# Plot resource usage trends
def plot_resource_usage(cpu_usage, memory_usage, timestamps, title):
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, cpu_usage, label="CPU Usage (%)", color="blue")
    plt.plot(timestamps, memory_usage, label="Memory Usage (MB)", color="green")
    plt.xlabel("Time (s)")
    plt.ylabel("Usage")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{title.replace(' ', '_')}_resource_usage.png")
    plt.show()

if __name__ == "__main__":
    # Sample inputs for testing
    video_path = "5105.mp4"  # Path to a sample video file
    plot_text = "A time traveling scientist goes back to prehistoric times and feeds dinosaurs a magic cereal that increases their intelligence - next they land in modern New York City for a series of comic adventures."  # Placeholder plot text
    output_path = "summary_video.mp4"
    output_path1 = "summary_video_with_captions.mp4"
    cap_path = "summary_video.srt"
    
    # Initialize process monitoring
    process = psutil.Process()
    cpu_usage = []
    memory_usage = []
    timestamps = []

    # Task: Find engaging scenes
    logging.info("Starting scene detection")
    start_time = time.time()

    scenes = profile_function(find_engaging_scenes, video_path, max_duration=20, plot_text=plot_text)

    elapsed_time = time.time() - start_time
    memory, cpu = monitor_resources(process)
    cpu_usage.append(cpu)
    memory_usage.append(memory)
    timestamps.append(elapsed_time)

    logging.info(f"Scene detection completed: {len(scenes)} scenes found")
    logging.info(f"Time taken: {elapsed_time:.2f} seconds")
    logging.info(f"Memory usage: {memory:.2f} MB")
    logging.info(f"CPU usage: {cpu:.2f}%")

    # Task: Extract and combine clips
    if scenes:
        logging.info("Starting video summarization")
        start_time = time.time()

        profile_function(extract_and_combine_clips, video_path, output_path, output_path1, cap_path, scenes)


        elapsed_time = time.time() - start_time
        memory, cpu = monitor_resources(process)
        cpu_usage.append(cpu)
        memory_usage.append(memory)
        timestamps.append(elapsed_time)

        logging.info(f"Video summarization completed")
        logging.info(f"Time taken: {elapsed_time:.2f} seconds")
        logging.info(f"Memory usage: {memory:.2f} MB")
        logging.info(f"CPU usage: {cpu:.2f}%")

        # Plot resource usage trends
        plot_resource_usage(cpu_usage, memory_usage, timestamps, "Video Summarizer Resource Usage")

    else:
        logging.warning("No scenes detected for summarization.")

    logging.info("Performance evaluation completed.")
