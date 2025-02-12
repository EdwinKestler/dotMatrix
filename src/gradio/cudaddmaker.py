import cv2
import numpy as np
import gradio as gr

from moviepy.editor import VideoFileClip
import tempfile
import os
import cupy as cp  # GPU-accelerated library, if using the GPU version

def dot_matrix_effect(frame, dot_size):
    """
    Converts a given BGR frame into a dot matrix style image.
    
    Parameters:
      - frame: Input image in BGR format.
      - dot_size: Radius of the dot to draw.
      
    Returns:
      - output_bgr: Processed image in BGR format.
    """
    # Convert frame to grayscale using the standard formula:
    # G(x,y) = 0.299*R + 0.587*G + 0.114*B
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Adjust cell size: using a factor of 3 instead of 4 for tighter spacing.
    cell_size = int(dot_size * 2)
    height, width = gray.shape
    # Create a white canvas.
    output = np.ones((height, width), dtype=np.uint8) * 255

    # Process the frame in blocks.
    for y in range(0, height, cell_size):
        for x in range(0, width, cell_size):
            cell = gray[y:min(y + cell_size, height), x:min(x + cell_size, width)]
            avg_intensity = np.mean(cell)
            # If the cell is relatively dark, draw a dot.
            if avg_intensity < 128:
                center = (x + cell.shape[1] // 2, y + cell.shape[0] // 2)
                cv2.circle(output, center, int(dot_size), (0,), -1)
    
    # Convert processed image back to BGR.
    output_bgr = cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)
    return output_bgr

def process_video(input_video, dot_size):
    """
    Applies the dot matrix effect to each frame of a video.
    
    Parameters:
      - input_video: Uploaded video file.
      - dot_size: Dot size selected by the user.
    
    Returns:
      - output_video_path: Path to the processed video file.
    """
    # Create a temporary directory to save the processed video.
    tmp_dir = tempfile.mkdtemp()
    output_video_path = os.path.join(tmp_dir, "output.mp4")
    
    # Load video using MoviePy.
    clip = VideoFileClip(input_video.name)

    def process_frame(frame):
        # MoviePy uses RGB format; convert to BGR.
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        processed_bgr = dot_matrix_effect(frame_bgr, dot_size)
        # Convert back to RGB for MoviePy.
        processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)
        return processed_rgb

    # Apply the dot matrix effect to each frame.
    processed_clip = clip.fl_image(process_frame)
    processed_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac', logger=None)
    
    return output_video_path

def test_frame(input_video, dot_size):
    """
    Processes only the first frame of the uploaded video so you can test the dot size.
    
    Parameters:
      - input_video: Uploaded video file.
      - dot_size: Dot size chosen from the slider.
    
    Returns:
      - processed_rgb: The processed first frame in RGB format.
    """
    # Load video using MoviePy.
    clip = VideoFileClip(input_video.name)
    # Extract the first frame (time=0 seconds).
    frame = clip.get_frame(0)  # frame in RGB format
    # Convert the frame from RGB to BGR for processing.
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    processed_bgr = dot_matrix_effect(frame_bgr, dot_size)
    # Convert the processed frame back to RGB for display.
    processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)
    return processed_rgb

def convert_media(input_media, dot_size):
    """
    Process the uploaded media file. In this app, only video files are supported.
    
    Parameters:
      - input_media: Video file uploaded by the user.
      - dot_size: Dot size chosen from the slider.
    
    Returns:
      - A tuple (video_path, video_path) where the first output is shown to the user
        and the second is stored in the hidden state for replay.
    """
    filename = input_media.name.lower()
    if any(filename.endswith(ext) for ext in [".mp4", ".avi", ".mov", ".mkv"]):
        video_path = process_video(input_media, dot_size)
        return video_path, video_path
    else:
        raise ValueError("Unsupported file format. Please upload a video file.")

def replay_video(video_path):
    """
    Replay function for the processed video.
    
    Parameters:
      - video_path: The stored processed video path.
      
    Returns:
      - video_path: The same video file path, causing the video component to replay.
    """
    return video_path

# Build the Gradio interface using a Blocks layout.
with gr.Blocks() as demo:
    gr.Markdown("# ChatGPT Ad Maker")
    gr.Markdown(
        "This app converts a video into a black and white dotted image effect. "
        "Adjust the dot size using the slider below, then process the video. "
        "Use the **Test Frame** button to render just one frame for testing, "
        "and the **Replay Video** button to replay the full processed video."
    )
    
    with gr.Row():
        input_video = gr.File(label="Upload Video", file_types=[".mp4", ".avi", ".mov", ".mkv"])
        dot_slider = gr.Slider(minimum=1, maximum=5, step=1, value=1, label="Dot Size (radius in pixels)")
    
    process_button = gr.Button("Process Video")
    test_button = gr.Button("Test Frame")
    replay_button = gr.Button("Replay Video")
    
    # A hidden state to store the processed video path.
    video_state = gr.State()
    output_video = gr.Video(label="Processed Video", format="mp4")
    # An image output for testing a single frame.
    test_output = gr.Image(label="Test Processed Frame")
    
    # Process the video when the process button is clicked.
    process_button.click(
        fn=convert_media,
        inputs=[input_video, dot_slider],
        outputs=[output_video, video_state]
    )
    
    # The test button processes only the first frame and returns an image.
    test_button.click(
        fn=test_frame,
        inputs=[input_video, dot_slider],
        outputs=test_output
    )
    
    # The replay button uses the stored state to re-output the video.
    replay_button.click(
        fn=replay_video,
        inputs=[video_state],
        outputs=output_video
    )

if __name__ == "__main__":
    demo.launch()
