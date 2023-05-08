import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip, CompositeVideoClip, vfx
from moviepy.editor import ImageClip
import os
import itertools

from PIL import Image, ImageTk
import cv2


class VideoProcessor:
    def __init__(self, root):
        self.root = root
        self.file_path = ""
        self.img_dir_path = ""
        self.alpha = 0.01
        self.zoom_factor = 1.0
        self.image_zoom_factor = 1.0
        self.crop_x = 0
        self.crop_y = 0
        self.crop_width = 198
        self.crop_height = 198

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

        self.crop_label = tk.Label(self.root, text="Область обрезки:")
        self.crop_label.grid(row=5, column=0, padx=5, pady=5)

        self.crop_canvas = tk.Canvas(self.root, width=200, height=200, bg="black")
        self.crop_canvas.grid(row=5, column=1, padx=5, pady=5)
        self.crop_canvas.bind("<B1-Motion>", self.update_crop_area)

        self.crop_rectangle = self.crop_canvas.create_rectangle(3, 3, self.crop_width+3, self.crop_height+3, outline="red")
        self.line1 = self.crop_canvas.create_line(3, 3, self.crop_width, self.crop_height, fill="red")
        self.line2 = self.crop_canvas.create_line(3, self.crop_width, self.crop_height, 3, fill="red")

        self.process_button = tk.Button(self.root, text="Process", command=self.process_video)
        self.process_button.grid(row=6, column=1, padx=5, pady=5)

    def update_crop_area(self, event):
        # вычисляем новые координаты квадрата
        new_x = event.x
        new_y = event.y
        new_width = self.crop_width
        new_height = self.crop_height

        # проверяем, чтобы квадрат не выходил за пределы Canvas
        if new_x < 3:
            new_x = 3
        if new_y < 3:
            new_y = 3
        if new_x + new_width > self.crop_canvas.winfo_width() -3:
            new_x = self.crop_canvas.winfo_width() - new_width -3
        if new_y + new_height > self.crop_canvas.winfo_height() -3:
            new_y = self.crop_canvas.winfo_height() - new_height -3

        # обновляем координаты квадрата
        self.crop_x = new_x
        self.crop_y = new_y

        # обновляем координаты и размеры прямоугольника на Canvas
        self.crop_canvas.coords(self.crop_rectangle, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line1, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line2, self.crop_x, self.crop_y + self.crop_height, self.crop_x + self.crop_width, self.crop_y)
    
    def set_alpha(self, value):
        self.alpha = float(value) / 100

    def set_zoom(self, value):
        self.zoom_factor = float(value) / 100
        # обновляем размеры квадрата
        self.crop_width = 298-int(value)
        self.crop_height = 298-int(value)
        # обновляем координаты и размеры прямоугольника на Canvas
        self.crop_canvas.coords(self.crop_rectangle, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line1, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line2, self.crop_x, self.crop_y + self.crop_height, self.crop_x + self.crop_width, self.crop_y)

    def browse_file(self):
        self.file_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select directory")
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, self.file_path)
        if self.file_path == "":
            return
        else:
            video_files = list(filter(lambda path: path[-4:].lower() == ".mp4", os.listdir(self.file_path)))

            cap = cv2.VideoCapture(os.path.join(self.file_path, video_files[0]))
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            ret, frame = cap.read()
            frame = cv2.resize(frame, (199, 199))
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = Image.fromarray(image)
            self.photo_image = ImageTk.PhotoImage(image)

            # создаем Canvas и добавляем изображение
            self.video_frame = self.crop_canvas.create_image(3, 3, anchor="nw", image=self.photo_image)
            self.crop_canvas.lower(self.video_frame)

            cap.release()
            cv2.destroyAllWindows()

    def browse_img_dir(self):
        self.img_dir_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select directory")
        self.img_dir_path_entry.delete(0, tk.END)
        self.img_dir_path_entry.insert(0, self.img_dir_path)


    def process_video(self):
        # Check if video file and image directory are selected
        if self.file_path == "" or self.img_dir_path == "":
            tk.messagebox.showwarning("Warning", "Please select video file and image directory.")
            return
        # Check limits
        if self.crop_x < 1:
            self.crop_x = 1
        if self.crop_y < 1:
            self.crop_y = 1

        # Get list of image files in directory
        img_files = list(filter(lambda path: path[-4:].lower() == ".jpg" or path[-4:].lower() == ".png" or path[-5:].lower() == ".jpeg", os.listdir(self.img_dir_path)))
        cycled_list = itertools.cycle(img_files)

        # Get list of videos files in directory
        # video_files = os.listdir(self.file_path)
        video_files = list(filter(lambda path: path[-4:].lower() == ".mp4", os.listdir(self.file_path)))




        # Loop through each image file and process video
        for i, vid_file in enumerate(video_files):
            # Get video and audio clips
            video_clip = VideoFileClip(os.path.join(self.file_path,vid_file))
            audio_clip = video_clip.audio

            # Get width and height of video clip
            width, height = video_clip.size

            # Get full path of image file
            img_name = next(cycled_list)
            img_path = os.path.join(self.img_dir_path, img_name)
            # Load image and resize
            img = ImageClip(img_path).resize((width, height))

            # Set alpha of image
            img = img.set_opacity(self.alpha)

            # Zoom video
            video_clip_zoomed = video_clip.fx(vfx.resize, self.zoom_factor)
            zoomed_width, zoomed_height = video_clip_zoomed.size

            # Crop video back to its original resolution
            crop_x = self.crop_width/(self.crop_x-3)
            crop_y = self.crop_width/(self.crop_y-3)
            video_clip_cropped = video_clip_zoomed.crop(x1=zoomed_width//crop_x, y1=zoomed_height//crop_y, x2=zoomed_width//crop_x + width, y2=zoomed_height//crop_y + height)
            print(f"Crop_x = {crop_x}\nCrop_y = {crop_y}")
            print(f"Original resolution = {width}x{height}")
            print(f"Zoomed resolution = {zoomed_width}x{zoomed_height}")
            print(f"Cropped coords:\nx1={zoomed_width//crop_x}\ny1={zoomed_height//crop_y}\nx2={zoomed_width//crop_x + width}\ny2={zoomed_height//crop_y + height}")
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
