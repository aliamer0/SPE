import cProfile
import pstats
import io
from video_summarizer import find_engaging_scenes

# Function to profile
def profile_video_summarizer():
    video_path = "5105.mp4"  # Path to a sample video file
    plot_text = "A time traveling scientist goes back to prehistoric times and feeds dinosaurs a magic cereal that increases their intelligence - next they land in modern New York City for a series of comic adventures."  # Placeholder plot text

    # Call the function to profile
    scenes = find_engaging_scenes(video_path, max_duration=20, plot_text=plot_text)
    print(f"Detected scenes: {scenes}")

if __name__ == "__main__":
    # Set up the profiler
    profiler = cProfile.Profile()
    profiler.enable()

    # Run the function
    profile_video_summarizer()

    # Disable the profiler
    profiler.disable()

    # Output profiling results to a file
    with open("profile_video_summarizer.txt", "w") as f:
        ps = pstats.Stats(profiler, stream=f)
        ps.sort_stats("cumulative")
        ps.print_stats()

    print("Profiling complete. Results saved to 'profile_video_summarizer.txt'.")
