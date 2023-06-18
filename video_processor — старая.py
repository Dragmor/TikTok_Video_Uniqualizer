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
        self.crop_x = 0
        self.crop_y = 0
        self.crop_width = 198
        self.crop_height = 198
        self.new_canvas_w = 298
        self.new_canvas_h = 298
        self.width_deform = 100
        # имя видео, которое выбрано в данный момент
        self.current_video_name = ""
        # имя картинки
        self.current_image_name = ""
        # дефолтный битрейт
        self.default_bitrate = 4000
        # битрейт выходного видео
        self.bitrate = self.default_bitrate
        # качество кодирования видео
        self.preset = "medium"
        # индекс для ручной работы с видео
        self.video_index = 0
        # список имён видео-файлов
        self.video_files = []
        # список имён картинок
        self.image_files = []
        # список параметров для ручной обработки
        self.vid_params = []
        #
        self.video_frame = None

        self.create_ui()
        self.pre_start_configurate()

    def create_ui(self):
        self.root.title("Video processor")
        # создаём фреймы для красивого расположения элементов
        self.general_frame = tk.Frame(self.root)
        self.general_frame.grid(row=0, column=0, padx=5, pady=5, sticky="n")
        self.frame_left = tk.Frame(self.general_frame)
        self.frame_left.grid(row=0, column=0, padx=5, pady=5, sticky="n")
        self.frame_right = tk.Frame(self.general_frame)
        self.frame_right.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        # Create widgets
        self.file_path_label = tk.Label(self.frame_left, text="Каталог с видео:")
        self.file_path_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.file_path_entry = tk.Entry(self.frame_left, justify="center")
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.file_path_entry.config(state="disabled")

        self.browse_file_button = tk.Button(self.frame_left, text="обзор", command=self.browse_file)
        self.browse_file_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.img_dir_path_label = tk.Label(self.frame_left, text="Каталог с картинками:")
        self.img_dir_path_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.img_dir_path_entry = tk.Entry(self.frame_left, justify="center")
        self.img_dir_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.img_dir_path_entry.config(state="disabled")

        self.browse_img_dir_button = tk.Button(self.frame_left, text="обзор", command=self.browse_img_dir)
        self.browse_img_dir_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.browse_img_dir_button.config(state="disabled")

        self.alpha_label = tk.Label(self.frame_left, text="Прозрачность картинки:")
        self.alpha_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.alpha_scale = tk.Scale(self.frame_left, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, command=self.set_alpha)
        self.alpha_scale.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.zoom_label = tk.Label(self.frame_left, text="Обрезка видео:")
        self.zoom_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.zoom_scale = tk.Scale(self.frame_left, from_=100, to=200, resolution=1, orient=tk.HORIZONTAL, command=self.set_zoom)
        self.zoom_scale.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.width_deform_label = tk.Label(self.frame_left, text="Растягивание по ширине:")
        self.width_deform_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.width_deform_scale = tk.Scale(self.frame_left, from_=50, to=200, resolution=1, orient=tk.HORIZONTAL, command=self.set_width_deform)
        self.width_deform_scale.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.width_deform_scale.set(100)

        self.codec_choice = tk.StringVar()
        self.codec_choice.set("auto")

        self.codec_auto_radio = tk.Radiobutton(self.frame_left, text="Автоматический выбор кодека", state="disabled", variable=self.codec_choice, value="auto")
        self.codec_auto_radio.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        self.codec_mpeg4_radio = tk.Radiobutton(self.frame_left, text="Кодек MPEG4", state="disabled", variable=self.codec_choice, value="mpeg4")
        self.codec_mpeg4_radio.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        self.auto_bitrate = tk.BooleanVar()
        self.auto_bitrate.set(True)
        self.auto_bitrate_checkbutton = tk.Checkbutton(self.frame_left, text="Автоматический выбор битрейта", variable=self.auto_bitrate, state="disabled", command=self.toggle_bitrate_scale)
        self.auto_bitrate_checkbutton.grid(row=8, column=0, padx=5, pady=5, sticky="w")

        self.bitrate_label = tk.Label(self.frame_left, text="Битрейт видео (кбит/с):")
        self.bitrate_scale = tk.Scale(self.frame_left, from_=1000, to=10000, resolution=100, orient=tk.HORIZONTAL, command=self.set_bitrate)
        self.bitrate_scale.set(self.bitrate)

        self.preset_label = tk.Label(self.frame_left, text="Качество кодирования видео:")
        self.preset_label.grid(row=7, column=0, padx=5, pady=5, sticky="w")

        self.preset_scale = tk.Scale(self.frame_left, from_=1, to=9, resolution=1, orient=tk.HORIZONTAL, command=self.set_preset)
        self.preset_scale.grid(row=7, column=1, padx=5, pady=5, sticky="w")
        self.preset_scale.set(6)
        self.preset_scale.config(state="disabled")

        #---------------------------------------------------------------------------------------------------------------------------------#
        self.crop_canvas = tk.Canvas(self.frame_right, width=200, height=200, bg="black")
        self.crop_canvas.grid(row=0, column=0, padx=5, pady=5)

        self.crop_label = tk.Label(self.frame_right, text="раскадровка видео")
        self.crop_label.grid(row=1, column=0, padx=5, sticky="we")

        self.frame_scale = tk.Scale(self.frame_right, from_=1, to=100, resolution=1, orient=tk.HORIZONTAL, command=self.set_frame)
        self.frame_scale.grid(row=2, column=0, padx=5, sticky="we")
        if self.mode == "manual":
            # кнопка вперёд
            self.button_next = tk.Button(self.frame_right, width=10, text="следующее видео", state="disabled", command=self.next_video)
            self.button_next.grid(row=4, column=0, sticky="we")
            # счётчик для видео
            self.label_counter = tk.Label(self.frame_right, font="calibri", text="[0/0]")
            self.label_counter.grid(row=5, column=0, sticky="n")
        #
        self.crop_rectangle = self.crop_canvas.create_rectangle(3, 3, self.crop_width+3, self.crop_height+3, outline="red")
        self.line1 = self.crop_canvas.create_line(3, 3, self.crop_width+3, self.crop_height+3, fill="red")
        self.line2 = self.crop_canvas.create_line(3, self.crop_width+3, self.crop_height+3, 3, fill="red")

        self.process_button = tk.Button(self.root, text="старт!", command=self.process_video)
        if self.mode != "manual":
            self.process_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    def set_preset(self, value):
        # выбор качества кодирования
        value = int(value)-1
        preset_values = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"]
        preset = preset_values[value]
        self.preset = preset  

    def set_width_deform(self, value):
        # изменение ширины видео
        if self.video_frame == None:
            return

        self.width_deform = int(value)
        new_width = self.width_deform/100

        image = cv2.cvtColor(cv2.resize(self.frame, (int(self.new_canvas_w*new_width), self.new_canvas_h)), cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)

        
        self.photo_image = ImageTk.PhotoImage(image)
        # создаем Canvas и добавляем изображение
        self.video_frame = self.crop_canvas.create_image(int(3+(self.new_canvas_w/2)-(self.new_canvas_w*new_width/2)), 3, anchor="nw", image=self.photo_image)
        self.crop_canvas.lower(self.video_frame)


    def pre_start_configurate(self):
        # метод преднастроек элементов
        self.alpha_scale.config(state="disabled")
        self.zoom_scale.config(state="disabled")
        self.width_deform_scale.config(state="disabled")
        self.frame_scale.config(state="disabled")
        self.process_button.config(state="disabled")

    def toggle_bitrate_scale(self):
        if self.auto_bitrate.get():
            self.bitrate_label.grid_forget()
            self.bitrate_scale.grid_forget()
        else:
            self.bitrate_label.grid(row=9, column=0, padx=5, pady=5, sticky="w")
            self.bitrate_scale.grid(row=9, column=1, padx=5, pady=5, sticky="w")


    def set_bitrate(self, value):
        # задаём битрейт для видео
        self.bitrate = int(value)


    def next_video(self):
        # проверка, были-ли изменены параметры для видео по сравнению с предыдущим
        if len(self.vid_params)>0:
            if self.vid_params[-1][1:] == [self.alpha, self.crop_x*2, self.crop_y*2, self.crop_x*2+(self.crop_width*2), self.crop_y*2+(self.crop_height*2), self.width_deform]:
                result = messagebox.askyesno("Предупреждение", "Параметры видео такие-же, как у предыдущего! Продолжить?")
                if not result:
                    return

        if not len(self.video_files) <= self.video_index:
            self.label_counter.config(text=f"[{self.video_index+2}/{len(self.video_files)}]")
            self.current_video_name = self.video_files[self.video_index]



            '''

            имя self.current_video_name
            прозрачность self.alpha
            x1 self.crop_x*2
            y1 self.crop_y*2
            x2 self.crop_x*2+(self.crop_width*2)
            y2 self.crop_y*2+(self.crop_height*2)
            растягивание по ширине self.width_deform

            '''

            self.vid_params.append([self.current_video_name, self.alpha, self.crop_x*2, self.crop_y*2, self.crop_x*2+(self.crop_width*2), self.crop_y*2+(self.crop_height*2), self.width_deform])
            self.video_index+=1
            self.current_video_name = self.video_files[self.video_index]
            self.change_video_field()
            if self.current_image_name != "":
                self.change_image_field()

            print(self.vid_params[-1])

        if len(self.video_files) <= self.video_index+1:
            self.button_next.grid_forget()
            self.process_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")


    def set_frame(self, value):
        # метод для выбора кадра в Canvas
        cap = cv2.VideoCapture(os.path.join(self.file_path, self.current_video_name))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames//100*int(value))
        ret, self.frame = cap.read()

        new_width = self.width_deform/100
        image = cv2.cvtColor(cv2.resize(self.frame, (int(self.new_canvas_w*new_width), self.new_canvas_h)), cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        self.photo_image = ImageTk.PhotoImage(image)
        # создаем Canvas и добавляем изображение
        self.video_frame = self.crop_canvas.create_image(int(3+(self.new_canvas_w/2)-(self.new_canvas_w*new_width/2)), 3, anchor="nw", image=self.photo_image)
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
        # обновляем размеры квадрата
        w_aspect = self.crop_canvas.winfo_height()/self.crop_canvas.winfo_width()
        self.crop_width = self.new_canvas_w+(100-int(value))
        self.crop_height = self.new_canvas_h+((100-int(value))*w_aspect)



        # обновляем координаты и размеры прямоугольника на Canvas
        self.crop_canvas.coords(self.crop_rectangle, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line1, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
        self.crop_canvas.coords(self.line2, self.crop_x, self.crop_y + self.crop_height, self.crop_x + self.crop_width, self.crop_y)

    def change_image_field(self):
        # накладывает self.current_image_name на Canvas
        self.image = Image.open(os.path.join(self.img_dir_path, self.current_image_name))
        self.image = self.image.resize((self.new_canvas_w, self.new_canvas_h), Image.ANTIALIAS) # Растянуть изображение до размеров холста
        self.image.putalpha(int((100-int(self.alpha_scale.get()))*2.56))
        self.photo = ImageTk.PhotoImage(self.image)
        self.photo_frame = self.crop_canvas.create_image(0, 0, anchor="nw", image=self.photo) # Вставить изображение с полупрозрачностью

        if self.image_files.index(self.current_image_name)+1 < len(self.image_files):
            self.current_image_name = self.image_files[self.image_files.index(self.current_image_name)+1]
        else:
            self.current_image_name = self.image_files[0]

    def change_video_field(self):
        switcher = False
        # метод меняет кадр из видео в прямоугольнике, его размер
        cap = cv2.VideoCapture(os.path.join(self.file_path, self.current_video_name))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames//100*self.frame_scale.get())

        # меняю разрешение Canvas
        video_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        video_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # если разрешение видео не совпадает с прошлым разрешением
        if int(video_w/2) != self.new_canvas_w or int(video_h/2) != self.new_canvas_h:
            switcher = True

        self.new_canvas_w = int(video_w/2)
        self.new_canvas_h = int(video_h/2)
        #
        self.crop_canvas.config(width=self.new_canvas_w)
        self.crop_canvas.config(height=self.new_canvas_h)

        # меняю рамку, только если это первое видео, или у видео другое разрешение
        if self.vid_params == [] or switcher == True:
            # меняю разрешение красного квадрата
            self.crop_width = self.new_canvas_w
            self.crop_height = self.new_canvas_h
            #
            self.crop_x = 0
            self.crop_y = 0
            # обновляем координаты и размеры прямоугольника на Canvas
            self.crop_canvas.coords(self.crop_rectangle, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
            self.crop_canvas.coords(self.line1, self.crop_x, self.crop_y, self.crop_x + self.crop_width, self.crop_y + self.crop_height)
            self.crop_canvas.coords(self.line2, self.crop_x, self.crop_y + self.crop_height, self.crop_x + self.crop_width, self.crop_y)
            # сбрасываю значение ползунка зума
            self.zoom_scale.set(100)



        ret, self.frame = cap.read()

        new_width = self.width_deform/100
        image = cv2.cvtColor(cv2.resize(self.frame, (int(self.new_canvas_w*new_width), self.new_canvas_h)), cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        self.photo_image = ImageTk.PhotoImage(image)
        # создаем Canvas и добавляем изображение
        self.video_frame = self.crop_canvas.create_image(int(3+(self.new_canvas_w/2)-(self.new_canvas_w*new_width/2)), 3, anchor="nw", image=self.photo_image)
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
            self.video_files = list(filter(lambda path: path[-4:].lower() == ".mp4", os.listdir(self.file_path)))
            if len(self.video_files) < 1:
                return
            # добавляю кадр из видео на Canvas
            self.current_video_name = self.video_files[0]
            self.change_video_field()
            # делаю бинд мыши на холсте
            self.crop_canvas.bind("<B1-Motion>", self.update_crop_area)
            self.zoom_scale.config(state="normal")
            self.width_deform_scale.config(state="normal")
            self.frame_scale.config(state="normal")
            self.browse_img_dir_button.config(state="normal")
            self.auto_bitrate_checkbutton.config(state="normal")
            self.codec_auto_radio.config(state="normal")
            self.codec_mpeg4_radio.config(state="normal")
            self.preset_scale.config(state="normal")
            self.process_button.config(state="normal", bg="lightgreen")
            # блокирую кнопку выбора каталога видео
            self.browse_file_button.config(state="disabled")
            self.file_path_entry.config(state="disabled")
        if self.mode == "manual":
            self.label_counter.config(text=f"[1/{len(self.video_files)}]")
            self.button_next.config(state="normal")
            

    def browse_img_dir(self):
        self.img_dir_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select directory")
        self.img_dir_path_entry.config(state="normal")
        self.img_dir_path_entry.delete(0, tk.END)
        self.img_dir_path_entry.insert(0, os.path.basename(self.img_dir_path))
        self.img_dir_path_entry.config(state="disabled")
        if self.img_dir_path == "":
            return
        else:
            self.image_files = list(filter(lambda path: path[-4:].lower() == ".png" or path[-4:].lower() == ".jpg" or path[-5:].lower() == ".jpeg", os.listdir(self.img_dir_path)))
            if len(self.image_files) < 1:
                return
            # добавляю кадр на Canvas
            self.current_image_name = self.image_files[0]
            self.change_image_field()
            self.alpha_scale.config(state="normal")
            self.browse_img_dir_button.config(state="disabled")


    def process_video(self):
        # Check if video file and image directory are selected
        if self.file_path == "":
            messagebox.showwarning("Предупреждение", "Сначала выберите каталог с видео!")
            return

        # Check limits
        if self.crop_x < 1 or self.crop_x == 3:
            self.crop_x = 1
        if self.crop_y < 1 or self.crop_y == 3:
            self.crop_y = 1

        if self.mode == "manual":
            # добавляем в список последнее видео
            self.current_video_name = self.video_files[-1]
            self.vid_params.append([self.current_video_name, self.alpha, self.crop_x*2, self.crop_y*2, self.crop_x*2+(self.crop_width*2), self.crop_y*2+(self.crop_height*2), self.width_deform])

        # если указано изображение
        if self.img_dir_path != "":
            # Get list of image files in directory
            cycled_list = itertools.cycle(self.image_files)
        root.withdraw()
        # Loop through each image file and process video
        for i, vid_file in enumerate(self.video_files):
            try:
                # Get video and audio clips
                if self.mode == "manual":
                    video_clip = VideoFileClip(os.path.join(self.file_path, self.vid_params[i][0]))
                else:
                    video_clip = VideoFileClip(os.path.join(self.file_path,vid_file))
                audio_clip = video_clip.audio

                # Get width and height of video clip
                width, height = video_clip.size

                # если не указано изображение
                if self.img_dir_path != "":
                    # Get full path of image file
                    img_name = next(cycled_list)
                    img_path = os.path.join(self.img_dir_path, img_name)
                    # Load image and resize
                    img = ImageClip(img_path).resize((width, height))

                    # Set alpha of image
                    if self.mode == "manual":
                        img = img.set_opacity(self.vid_params[i][1])
                    else:
                        img = img.set_opacity(self.alpha)
                if self.mode == "manual":
                    video_clip_cropped = video_clip.crop(x1=self.vid_params[i][2], y1=self.vid_params[i][3], x2=self.vid_params[i][4], y2=self.vid_params[i][5])
                else:
                    video_clip_cropped = video_clip.crop(x1=self.crop_x*2, y1=self.crop_y*2, x2=self.crop_x*2+(self.crop_width*2), y2=self.crop_y*2+(self.crop_height*2))
                video_resized = video_clip_cropped.resize((width, height))
                # если не указано изображение
                if self.img_dir_path != "":
                    # Overlay image on video
                    img = img.set_duration(video_resized.duration)
                    final_video = CompositeVideoClip([video_resized, img])
                else:
                    final_video = video_resized

                # Set audio to the final video
                final_video = final_video.set_audio(audio_clip)

                # Export video
                if not os.path.isdir(os.path.normpath(os.path.join(self.file_path,"output"))):
                    os.mkdir(os.path.normpath(os.path.join(self.file_path,"output")))
                if self.mode == "manual":
                    output_file = os.path.normpath(os.path.join(self.file_path, f"output/{os.path.splitext(self.vid_params[i][0])[0]}.mp4"))
                else:
                    output_file = os.path.normpath(os.path.join(self.file_path, f"output/{os.path.splitext(vid_file)[0]}.mp4"))
                # определяем, какой кодек использовать
                codec = None
                if self.codec_choice.get() == "mpeg4":
                    codec = "mpeg4"
                bitrate = self.bitrate
                if self.auto_bitrate.get():
                    bitrate = self.default_bitrate
                final_video.write_videofile(output_file, codec=codec, preset=self.preset, bitrate=f"{bitrate}k")
            except:
                print("Произошла ошибка при обработке видео!")
        #
        root.deiconify() # Показать окно

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
 добавить иконку для гл. окна в if name == main!

 По поводу параметров, нужно чтобы я не смог к следующему видео перейти пока не изменю хоть какой нибудь параметр, 
 а то я могу по инерции прощелкать, а как мы знаем, одно видео может убить весь канал!
'''