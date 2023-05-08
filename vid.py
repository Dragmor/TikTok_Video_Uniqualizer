import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip, CompositeVideoClip, vfx
from moviepy.editor import ImageClip
import os

# import sys
# output = open("output.txt", "wt")
# sys.stdout = output
# sys.stderr = output

class VideoProcessor:
    def __init__(self, root):
        self.root = root
        self.file_path = ""
        self.img_dir_path = ""
        self.alpha = 0.5
        self.zoom_factor = 1.0
        self.image_zoom_factor = 1.0
        self.crop_x = 0
        self.crop_y = 0

        self.create_ui()

    def create_ui(self):
        self.root.title("Video Processor")

        # Create widgets
        self.file_path_label = tk.Label(self.root, text="Каталог с видео:")
        self.file_path_label.grid(row=0, column=0, padx=5, pady=5)

        self.file_path_entry = tk.Entry(self.root)
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5)

        self.browse_file_button = tk.Button(self.root, text="обзор", command=self.browse_file)
        self.browse_file_button.grid(row=0, column=2, padx=5, pady=5)

        self.img_dir_path_label = tk.Label(self.root, text="Каталог с картинками:")
        self.img_dir_path_label.grid(row=1, column=0, padx=5, pady=5)

        self.img_dir_path_entry = tk.Entry(self.root)
        self.img_dir_path_entry.grid(row=1, column=1, padx=5, pady=5)

        self.browse_img_dir_button = tk.Button(self.root, text="обзор", command=self.browse_img_dir)
        self.browse_img_dir_button.grid(row=1, column=2, padx=5, pady=5)

        self.alpha_label = tk.Label(self.root, text="Прозрачность картинки:")
        self.alpha_label.grid(row=2, column=0, padx=5, pady=5)

        self.alpha_scale = tk.Scale(self.root, from_=1, to=100, resolution=1, orient=tk.HORIZONTAL, command=self.set_alpha)
        self.alpha_scale.grid(row=2, column=1, padx=5, pady=5)

        self.zoom_label = tk.Label(self.root, text="Растянуть видео %:")
        self.zoom_label.grid(row=3, column=0, padx=5, pady=5)

        self.zoom_scale = tk.Scale(self.root, from_=100, to=200, resolution=1, orient=tk.HORIZONTAL, command=self.set_zoom)
        self.zoom_scale.grid(row=3, column=1, padx=5, pady=5)

        self.image_zoom_label = tk.Label(self.root, text="Растянуть картинку %:")
        self.image_zoom_label.grid(row=4, column=0, padx=5, pady=5)

        self.image_zoom_scale = tk.Scale(self.root, from_=100, to=200, resolution=1, orient=tk.HORIZONTAL, command=self.set_image_zoom)
        self.image_zoom_scale.grid(row=4, column=1, padx=5, pady=5)

        self.crop_label = tk.Label(self.root, text="Область обрезки:")
        self.crop_label.grid(row=5, column=0, padx=5, pady=5)

        self.crop_canvas = tk.Canvas(self.root, width=200, height=200, bg="white")
        self.crop_canvas.grid(row=5, column=1, padx=5, pady=5)
        self.crop_canvas.bind("<B1-Motion>", self.update_crop_area)

        self.crop_rectangle = self.crop_canvas.create_rectangle(0, 0, 100, 100, outline="black")

        self.process_button = tk.Button(self.root, text="Process", command=self.process_video)
        self.process_button.grid(row=6, column=1, padx=5, pady=5)

    def update_crop_area(self, event):
        self.crop_x = event.x
        self.crop_y = event.y
        self.crop_canvas.coords(self.crop_rectangle, self.crop_x, self.crop_y, self.crop_x + 100, self.crop_y + 100)

    def set_alpha(self, value):
        self.alpha = float(value) / 100

    def set_zoom(self, value):
        self.zoom_factor = float(value) / 100

    def set_image_zoom(self, value):
        self.image_zoom_factor = float(value) / 100

    def browse_file(self):
        self.file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file", filetypes=(("MP4 files", "*.mp4"), ("all files", "*.*")))
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, self.file_path)

    def browse_img_dir(self):
        self.img_dir_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select directory")
        self.img_dir_path_entry.delete(0, tk.END)
        self.img_dir_path_entry.insert(0, self.img_dir_path)

    def process_video(self):
        # Check if video file and image directory are selected
        if self.file_path == "" or self.img_dir_path == "":
            tk.messagebox.showwarning("Warning", "Please select video file and image directory.")
            return

        # Get video and audio clips
        video_clip = VideoFileClip(self.file_path)
        audio_clip = video_clip.audio

        # Get width and height of video clip
        width, height = video_clip.size

        # Get list of image files in directory
        img_files = os.listdir(self.img_dir_path)

        # Loop through each image file and process video
        for i, img_file in enumerate(img_files):
            # Get full path of image file
            img_path = os.path.join(self.img_dir_path, img_file)

            # Load image and resize
            img = ImageClip(img_path).resize((width * self.image_zoom_factor, height * self.image_zoom_factor))

            # Set alpha of image
            img = img.set_opacity(self.alpha)

            # Zoom video
            video_clip_zoomed = video_clip.fx(vfx.resize, self.zoom_factor)

            # Crop video back to its original resolution
            video_clip_cropped = video_clip_zoomed.crop(x1=self.crop_x, y1=self.crop_y, x2=self.crop_x + width, y2=self.crop_y + height)

            # Overlay image on video
            img = img.set_duration(video_clip_cropped.duration)
            final_video = CompositeVideoClip([video_clip_cropped, img])

            # Set audio to the final video
            final_video = final_video.set_audio(audio_clip)

            # Export video
            output_file = f"output_{i}.mp4"
            final_video.write_videofile(output_file)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoProcessor(root)
    root.mainloop()



'''
сделать выбор каталога с видео
цикл обработки всех видео со сменой картинок
idle_update() или как-то так
'''
