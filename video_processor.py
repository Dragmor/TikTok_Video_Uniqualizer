import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip, CompositeVideoClip, vfx
from moviepy.editor import ImageClip
import os
import itertools
from PIL import Image, ImageTk
import cv2


class VideoProcessor:
    def __init__(self, root, mode):
        self.root = root
        # режим работы программы
        self.mode = mode 
        self.file_path = ""
        self.img_dir_path = ""
        self.alpha = 1
        self.zoom_factor = 1.0
        self.image_zoom_factor = 1.0
        self.crop_x = 0
        self.crop_y = 0
        self.crop_width = 198
        self.crop_height = 198
        self.new_canvas_w = 298
        self.new_canvas_h = 298
        # имя видео, которое выбрано в данный момент
        self.current_video_name = ""
        # имя картинки
        self.current_image_name = ""

        self.create_ui()
        self.pre_start_configurate()
        if self.mode == "manual":
            self.manual_mode_config()

    def create_ui(self):
        self.root.title("Уникализатор видео")

        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, padx=5, pady=5)

        # Create widgets
        self.file_path_label = tk.Label(self.frame, text="Каталог с видео:")
        self.file_path_label.grid(row=0, column=0, padx=5, pady=5)

        self.file_path_entry = tk.Entry(self.frame, justify="center")
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5)
        self.file_path_entry.config(state="disabled")

        self.browse_file_button = tk.Button(self.frame, text="обзор", command=self.browse_file)
        self.browse_file_button.grid(row=0, column=2, padx=5, pady=5)

        self.img_dir_path_label = tk.Label(self.frame, text="Каталог с картинками:")
        self.img_dir_path_label.grid(row=1, column=0, padx=5, pady=5)

        self.img_dir_path_entry = tk.Entry(self.frame, justify="center")
        self.img_dir_path_entry.grid(row=1, column=1, padx=5, pady=5)
        self.img_dir_path_entry.config(state="disabled")

        self.browse_img_dir_button = tk.Button(self.frame, text="обзор", command=self.browse_img_dir)
        self.browse_img_dir_button.grid(row=1, column=2, padx=5, pady=5)
        self.browse_img_dir_button.config(state="disabled")

        self.alpha_label = tk.Label(self.frame, text="Прозрачность картинки:")
        self.alpha_label.grid(row=2, column=0, padx=5, pady=5)

        self.alpha_scale = tk.Scale(self.frame, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, command=self.set_alpha)
        self.alpha_scale.grid(row=2, column=1, padx=5, pady=5)

        self.zoom_label = tk.Label(self.frame, text="Растянуть видео %:")
        self.zoom_label.grid(row=3, column=0, padx=5, pady=5)

        self.zoom_scale = tk.Scale(self.frame, from_=100, to=200, resolution=1, orient=tk.HORIZONTAL, command=self.set_zoom)
        self.zoom_scale.grid(row=3, column=1, padx=5, pady=5)

        self.crop_label = tk.Label(self.root, text="Область обрезки:")
        self.crop_label.grid(row=1, column=1, padx=5, pady=5)

        self.crop_canvas = tk.Canvas(self.root, width=200, height=200, bg="black")
        self.crop_canvas.grid(row=0, column=1, padx=5, pady=5)

        self.frame_scale = tk.Scale(self.root, from_=1, to=100, resolution=1, orient=tk.HORIZONTAL, command=self.set_frame)
        self.frame_scale.grid(row=1, column=1, padx=5, pady=5)

        self.crop_rectangle = self.crop_canvas.create_rectangle(3, 3, self.crop_width+3, self.crop_height+3, outline="red")
        self.line1 = self.crop_canvas.create_line(3, 3, self.crop_width+3, self.crop_height+3, fill="red")
        self.line2 = self.crop_canvas.create_line(3, self.crop_width+3, self.crop_height+3, 3, fill="red")

        self.process_button = tk.Button(self.root, text="старт!", command=self.process_video)
        self.process_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
  

    def pre_start_configurate(self):
        # метод преднастроек элементов
        self.alpha_scale.config(state="disabled")
        self.zoom_scale.config(state="disabled")
        self.frame_scale.config(state="disabled")
        self.process_button.config(state="disabled")



    def manual_mode_config(self):
        # метод для настройки окна под ручной режим
        self.process_button.grid_forget()

    def set_frame(self, value):
        # метод для выбора кадра в Canvas
        cap = cv2.VideoCapture(os.path.join(self.file_path, self.current_video_name))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames//100*int(value))
        ret, frame = cap.read()
        frame = cv2.resize(frame, (self.new_canvas_w, self.new_canvas_h))
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(image)
        self.photo_image = ImageTk.PhotoImage(image)
        # создаем Canvas и добавляем изображение
        self.video_frame = self.crop_canvas.create_image(3, 3, anchor="nw", image=self.photo_image)
        self.crop_canvas.lower(self.video_frame)

        cap.release()
        cv2.destroyAllWindows()
        

    def update_crop_area(self, event):
        # вычисляем новые координаты квадрата
        new_x = event.x
        new_y = event.y
        new_width = self.crop_width
        new_height = self.crop_height

        # проверяем, чтобы квадрат не выходил за пределы Canvas
        if new_x < 1:
            new_x = 1
        if new_y < 1:
            new_y = 1
        if new_x + new_width > self.crop_canvas.winfo_width():
            new_x = self.crop_canvas.winfo_width() - new_width
        if new_y + new_height > self.crop_canvas.winfo_height():
            new_y = self.crop_canvas.winfo_height() - new_height

        # обновляем координаты квадрата
        self.crop_x = new_x
        self.crop_y = new_y

        # обновляем координаты и размеры прямоугольника на Canvas
        self.crop_canvas.coords(self.crop_rectangle, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line1, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line2, self.crop_x, self.crop_y + self.crop_height, self.crop_x + self.crop_width, self.crop_y)
    
    def set_alpha(self, value):
        # задаёт прозрачность для картинки
        if int(value) == 0:
            self.alpha = 1
        else:
            self.alpha = (100-float(value)) / 100
        # задаём прозрачность картинки
        self.image.putalpha(int((100-int(value))*2.56)) # Изменить прозрачность изображения
        self.photo = ImageTk.PhotoImage(self.image) # Обновить объект PhotoImage
        self.crop_canvas.itemconfig(self.photo_frame, image=self.photo)

    def set_zoom(self, value):
        # устанавливает зум
        self.zoom_factor = float(value) / 100
        # обновляем размеры квадрата
        self.crop_width = self.new_canvas_w+(100-int(value))
        self.crop_height = self.new_canvas_h+(100-int(value))
        # обновляем координаты и размеры прямоугольника на Canvas
        self.crop_canvas.coords(self.crop_rectangle, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line1, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line2, self.crop_x, self.crop_y + self.crop_height, self.crop_x + self.crop_width, self.crop_y)

    def change_image_field(self):
        # накладывает self.current_image_name на Canvas
        self.image = Image.open(os.path.join(self.img_dir_path, self.current_image_name))
        self.image = self.image.resize((self.new_canvas_w, self.new_canvas_h), Image.ANTIALIAS) # Растянуть изображение до размеров холста
        self.image.putalpha(256)
        self.photo = ImageTk.PhotoImage(self.image)
        self.photo_frame = self.crop_canvas.create_image(0, 0, anchor="nw", image=self.photo) # Вставить изображение с полупрозрачностью


    def change_video_field(self):
        # метод меняет кадр из видео в прямоугольнике, его размер
        cap = cv2.VideoCapture(os.path.join(self.file_path, self.current_video_name))
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # меняю разрешение Canvas
        video_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        video_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.new_canvas_w = int(video_w/2)
        self.new_canvas_h = int(video_h/2)
        #
        self.crop_canvas.config(width=self.new_canvas_w)
        self.crop_canvas.config(height=self.new_canvas_h)
        # меняю разрешение красного квадрата
        self.crop_width = self.new_canvas_w
        self.crop_height = self.new_canvas_h
        # обновляем координаты и размеры прямоугольника на Canvas
        self.crop_canvas.coords(self.crop_rectangle, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line1, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line2, self.crop_x, self.crop_y + self.crop_height, self.crop_x + self.crop_width, self.crop_y)

        ret, frame = cap.read()
        frame = cv2.resize(frame, (self.new_canvas_w, self.new_canvas_h))
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(image)
        self.photo_image = ImageTk.PhotoImage(image)

        # создаем Canvas и добавляем изображение
        self.video_frame = self.crop_canvas.create_image(3, 3, anchor="nw", image=self.photo_image)
        self.crop_canvas.lower(self.video_frame)

        cap.release()
        cv2.destroyAllWindows()

    def browse_file(self):
        self.file_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select directory")
        self.file_path_entry.config(state="normal")
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, os.path.basename(self.file_path))
        self.file_path_entry.config(state="disabled")
        if self.file_path == "":
            return
        else:
            video_files = list(filter(lambda path: path[-4:].lower() == ".mp4", os.listdir(self.file_path)))
            if len(video_files) < 1:
                return
            # добавляю кадр из видео на Canvas
            self.current_video_name = video_files[0]
            self.change_video_field()
            # делаю бинд мыши на холсте
            self.crop_canvas.bind("<B1-Motion>", self.update_crop_area)
            self.zoom_scale.config(state="normal")
            self.frame_scale.config(state="normal")
            self.browse_img_dir_button.config(state="normal")
            # блокирую кнопку выбора каталога видео
            self.browse_file_button.config(state="disabled")
            self.file_path_entry.config(state="disabled")
            

    def browse_img_dir(self):
        self.img_dir_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select directory")
        self.img_dir_path_entry.config(state="normal")
        self.img_dir_path_entry.delete(0, tk.END)
        self.img_dir_path_entry.insert(0, os.path.basename(self.img_dir_path))
        self.img_dir_path_entry.config(state="disabled")
        if self.img_dir_path == "":
            return
        else:
            img_files = list(filter(lambda path: path[-4:].lower() == ".png" or path[-4:].lower() == ".jpg", os.listdir(self.img_dir_path)))
            if len(img_files) < 1:
                return
            # добавляю кадр на Canvas
            self.current_image_name = img_files[0]
            self.change_image_field()
            self.process_button.config(state="normal")
            self.alpha_scale.config(state="normal")
            self.process_button.config(state="normal", bg="lightgreen", font=("system", 12))
            self.browse_img_dir_button.config(state="disabled")




    def process_video(self):
        # Check if video file and image directory are selected
        if self.file_path == "" or self.img_dir_path == "":
            messagebox.showwarning("Предупреждение", "Сначала выберите каталоги с видео и изображениями!")
            return
        # Check limits
        if self.crop_x < 1 or self.crop_x == 3:
            self.crop_x = 1
        if self.crop_y < 1 or self.crop_y == 3:
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

            video_clip_cropped = video_clip.crop(x1=self.crop_x*2, y1=self.crop_y*2, x2=self.crop_x*2+(self.crop_width*2), y2=self.crop_y*2+(self.crop_height*2))
            video_resized = video_clip_cropped.resize((width, height))

            # Overlay image on video
            img = img.set_duration(video_resized.duration)
            final_video = CompositeVideoClip([video_resized, img])

            # Set audio to the final video
            final_video = final_video.set_audio(audio_clip)

            # Export video
            if not os.path.isdir(os.path.normpath(os.path.join(self.file_path,"output"))):
                os.mkdir(os.path.normpath(os.path.join(self.file_path,"output")))
            output_file = os.path.normpath(os.path.join(self.file_path, f"output/{os.path.splitext(vid_file)[0]}.mp4"))
            final_video.write_videofile(output_file)

if __name__ == "__main__":

    root = tk.Tk()
    # скрываю окно
    root.withdraw()
    message = "Хотите запустить программу для работы в автоматическом режиме? Нажмите [нет] чтобы запустить в режиме ручной работы"
    result = messagebox.askyesno("Выбор режима", message)
    if result:
        mode = 'auto'
    else:
        mode = 'manual'
    root.deiconify() # Показать окно
    app = VideoProcessor(root, mode)
    root.mainloop()
'''
 (кнопка, при нажатии которой в рабочей области кадр из видео сменяется другим кадром из этого же видео)

manual_mode_config(self): метод для первичной настройки окна под ручной режим


 счетчик всех видео и какое конкретно отображается в рабочей области(пример 16/1998/15, где 16- это видео 
 по порядку в папке, 1998 общее число видео, а 15 это на скольких видео установлены индивидуальные параметры) 
 и кнопка сохранить для сохранения параметра конкретно для этого видео

 Если на какое то я не нажал сохранить, то при нажатии на старт прога не запускалась, а писала, что не для всех 
 видео установлены индивидуальные параметры и перекидывалась в рабочую область видео без установленных параметров


 Можно сделать раскадровку максимальную и ползунов который я просто передвигаю, а картинки быстро меняются, 
 так и смогу понять как ведет себя видео

 добавить иконку для гл. окна в if name == main!
'''