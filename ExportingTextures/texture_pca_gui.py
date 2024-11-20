import os
import numpy as np
import cv2
from tkinter import Tk, Canvas, Scale, HORIZONTAL, Button, Frame, Scrollbar
from PIL import Image, ImageTk

# Paths
BASE_PATH = "D:/Projects/Pycharm Projects/PES-Face-Maker"
PCA_MODEL_PATH = os.path.join(BASE_PATH, "pca_texture_model.npy")
OUTPUT_PATH = os.path.join(BASE_PATH, "generated_textures")
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Load PCA model
pca = np.load(PCA_MODEL_PATH, allow_pickle=True).item()

# PCA attributes
mean_texture = pca.mean_
components = pca.components_
n_components = components.shape[0]


# GUI Setup
class TextureGeneratorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Texture Generator")
        self.component_values = np.zeros(n_components)

        # Frame for sliders with scrollbar
        self.slider_frame = Frame(master)
        self.slider_frame.pack(side="left", fill="y")

        self.slider_canvas = Canvas(self.slider_frame)
        self.slider_canvas.pack(side="left", fill="y", expand=True)

        self.slider_scrollbar = Scrollbar(self.slider_frame, orient="vertical", command=self.slider_canvas.yview)
        self.slider_scrollbar.pack(side="right", fill="y")

        self.slider_canvas.configure(yscrollcommand=self.slider_scrollbar.set)
        self.slider_canvas.bind('<Configure>', lambda e: self.slider_canvas.configure(scrollregion=self.slider_canvas.bbox("all")))

        self.sliders_container = Frame(self.slider_canvas)
        self.slider_canvas.create_window((0, 0), window=self.sliders_container, anchor="nw")

        # Create sliders for each PCA component
        self.sliders = []
        for i in range(n_components):
            slider = Scale(self.sliders_container, from_=-100, to=100, orient=HORIZONTAL, label=f"Component {i + 1}", command=self.update_texture)
            slider.pack()
            slider.set(0)  # Start with all components at zero
            self.sliders.append(slider)

        # Frame for buttons and canvas
        self.right_frame = Frame(master)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Generate Button
        self.generate_button = Button(self.right_frame, text="Generate Texture", command=self.update_texture)
        self.generate_button.pack()

        # Save Button
        self.save_button = Button(self.right_frame, text="Save Texture", command=self.save_texture)
        self.save_button.pack()

        # Canvas for displaying the texture
        self.canvas = Canvas(self.right_frame, width=256, height=256, bg="white")
        self.canvas.pack()

        # Initialize the image preview
        self.texture_preview = ImageTk.PhotoImage(image=Image.fromarray(np.zeros((256, 256, 3), dtype=np.uint8)))
        self.canvas.create_image(0, 0, anchor="nw", image=self.texture_preview)

    def update_texture(self, *_):
        # Update the texture based on slider values
        for i, slider in enumerate(self.sliders):
            self.component_values[i] = slider.get() * 10.0  # Scale values to smaller range

        # Reconstruct the texture using the PCA components
        new_texture = mean_texture + np.dot(self.component_values, components)
        new_texture = np.clip(new_texture, 0, 255).astype(np.uint8)  # Ensure valid pixel range
        new_texture = new_texture.reshape((256, 256, 3))  # Reshape back to image
        new_texture = cv2.cvtColor(new_texture, cv2.COLOR_BGR2RGB)  # Correct color ordering

        # Update the canvas with the new texture
        self.texture_preview = ImageTk.PhotoImage(image=Image.fromarray(new_texture))
        self.canvas.create_image(0, 0, anchor="nw", image=self.texture_preview)

    def save_texture(self):
        # Save the current texture
        for i, slider in enumerate(self.sliders):
            self.component_values[i] = slider.get() / 100.0  # Update values again

        new_texture = mean_texture + np.dot(self.component_values, components)
        new_texture = np.clip(new_texture, 0, 255).astype(np.uint8)
        new_texture = new_texture.reshape((256, 256, 3))
        new_texture_rgb = cv2.cvtColor(new_texture, cv2.COLOR_BGR2RGB)  # Correct for RGB

        # Save the texture as a PNG file
        save_path = os.path.join(OUTPUT_PATH, "generated_texture.png")
        cv2.imwrite(save_path, cv2.cvtColor(new_texture_rgb, cv2.COLOR_RGB2BGR))  # Convert back for OpenCV
        print(f"Texture saved to {save_path}")


# Main application loop
if __name__ == "__main__":
    root = Tk()
    gui = TextureGeneratorGUI(root)
    root.mainloop()
