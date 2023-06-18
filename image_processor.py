import os
from tkinter import filedialog, Tk, Label, Button, Scale, Radiobutton, IntVar
from PIL import Image
import sys

class ImageProcessor:
    def __init__(self):
        self.image_format = "png"
        self.create_main_window()

    def resize_and_crop_image(self, image, scale_factor, output_dir, img_index):
        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)
        resized_image = image.resize((new_width, new_height))
        crop_positions = [
            (0, 0, image.width, image.height),
            (new_width - image.width, 0, new_width, image.height),
            (0, new_height - image.height, image.width, new_height),
            (new_width - image.width, new_height - image.height, new_width, new_height),
            (new_width // 2 - image.width // 2, 0, new_width // 2 + image.width // 2, image.height),
            (0, new_height // 2 - image.height // 2, image.width, new_height // 2 + image.height // 2),
            (new_width - image.width, new_height // 2 - image.height // 2, new_width, new_height // 2 + image.height // 2),
            (new_width // 2 - image.width // 2, new_height - image.height, new_width // 2 + image.width // 2, new_height)
        ]
        pos = 1
        for index, position in enumerate(crop_positions):
            print(f"положение {pos}")
            cropped_image = resized_image.crop(position)
            cropped_image.save(os.path.join(output_dir, f"cropped_{img_index}_{index}.{self.image_format}"))
            pos+=1

    def process_images(self, directory, scale_factor):
        output_dir = os.path.join(directory, "output")
        os.makedirs(output_dir, exist_ok=True)
        img_index = 1
        # скрываю окно
        self.root.withdraw()
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image = Image.open(os.path.join(directory, filename))
                print(f"Обрабатываю изображение: {filename}")
                self.resize_and_crop_image(image, scale_factor, output_dir, img_index)
                img_index+=1
                print("\n")
        print("Готово!")
        self.root.deiconify() # Показать окно

    def choose_directory_and_process_images(self, scale_factor):
        directory = filedialog.askdirectory()
        if directory:
            self.process_images(directory, scale_factor)

    def set_image_format(self, value):
        if value == 1:
            self.image_format = "jpg"
        else:
            self.image_format = "png"

    def create_main_window(self):
        self.root = Tk()
        #пытаюсь установить иконку
        try:
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            self.root.wm_iconbitmap(os.path.join(base_path, "icon.ico"))
        except:
            pass
        self.root.title("Image Processor")
        var = IntVar()
        var.set(2)
        Label(self.root, text="Выберите масштаб:").pack(padx=10, pady=10)
        scale = Scale(self.root, from_=110, to=300, orient="horizontal")
        scale.set(120)
        scale.pack(padx=10, pady=10)

        Radiobutton(self.root, text="Сохранять в формате JPG", variable=var, value=1, command=lambda:self.set_image_format(var.get())).pack(padx=10, pady=10)
        Radiobutton(self.root, text="Сохранять в формате PNG", variable=var, value=2, command=lambda:self.set_image_format(var.get())).pack(padx=10, pady=10)

        Button(self.root, text="Выберите папку и обработайте изображения", bg="lightgreen", command=lambda: self.choose_directory_and_process_images(scale.get() / 100)).pack(padx=10, pady=10)

        self.root.mainloop()

if __name__ == "__main__":
    image_processor = ImageProcessor()