import os
import numpy as np
import cv2
from tkinter import Tk, Canvas, Scale, HORIZONTAL, Button, Frame, Scrollbar, filedialog
from PIL import Image, ImageTk

from ExportingTextures.create_texture_pca import EXPORTING_TEXTURES_FOLDER_PATH

# Paths
BASE_PATH = "D:/Projects/Pycharm Projects/PES-Face-Maker"
PCA_MODEL_PATH = os.path.join(EXPORTING_TEXTURES_FOLDER_PATH, "pca_texture_model.npy")
GMM_MODEL_PATH = os.path.join(EXPORTING_TEXTURES_FOLDER_PATH, "gmm_texture_model.npy")
OUTPUT_PATH = os.path.join(BASE_PATH, "generated_textures")
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Load PCA model
pca = np.load(PCA_MODEL_PATH, allow_pickle=True).item()
coeff_min, coeff_max = np.load(os.path.join(BASE_PATH, "ExportingTextures/pca_texture_coeffs.npy"))
TEXTURE_SIZE = np.sqrt(pca.mean_.shape[0] // 3).astype(int)

# Load GMM model
gmm = np.load(GMM_MODEL_PATH, allow_pickle=True).item()

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
        self.debounce_id = None  # For debouncing `update_texture` calls

        # Calculate slider ranges
        self.slider_ranges = [3 * np.sqrt(var) for var in pca.explained_variance_]

        # Frame for sliders with scrollbar
        self.slider_frame = Frame(master)
        self.slider_frame.pack(side="left", fill="y")

        self.slider_canvas = Canvas(self.slider_frame, width=1000)
        self.slider_canvas.pack(side="left", fill="y", expand=True)

        self.slider_scrollbar = Scrollbar(self.slider_frame, orient="vertical", command=self.slider_canvas.yview)
        self.slider_scrollbar.pack(side="right", fill="y")

        self.slider_canvas.configure(yscrollcommand=self.slider_scrollbar.set)
        self.slider_canvas.bind('<Configure>',
                                lambda e: self.slider_canvas.configure(scrollregion=self.slider_canvas.bbox("all")))

        self.sliders_container = Frame(self.slider_canvas)
        self.slider_canvas.create_window((0, 0), window=self.sliders_container, anchor="nw")

        # Create sliders for each PCA component
        self.sliders = []
        for i in range(n_components):
            range_limit = self.slider_ranges[i]
            slider = Scale(self.sliders_container, orient=HORIZONTAL, label=f"Component {i + 1}",
                           command=self.debounced_update_texture, from_=-range_limit, to=range_limit, resolution=10,
                           length=900)
            slider.pack(pady=2)
            slider.set(0)  # Start with all components at zero
            self.sliders.append(slider)

        # Frame for buttons and canvas
        self.right_frame = Frame(master)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Import Button
        self.import_button = Button(self.right_frame, text="Import Texture", command=self.import_texture)
        self.import_button.pack()

        # Generate Button
        self.update_button = Button(self.right_frame, text="Update Texture", command=self.update_texture)
        self.update_button.pack()

        self.randomize_button = Button(self.right_frame, text="Randomize Texture", command=self.randomize_texture)
        self.randomize_button.pack()

        self.random_natural_button = Button(self.right_frame, text="Randomize Natural Texture", command=self.randomize_natural_texture)
        self.random_natural_button.pack()

        self.project_button = Button(self.right_frame, text="Project to Nearest", command=self.project_to_nearest)
        self.project_button.pack()

        self.reverse_button = Button(self.right_frame, text="Reverse", command=self.reverse_texture)
        self.reverse_button.pack()

        # Save Button
        self.save_button = Button(self.right_frame, text="Save Texture", command=self.save_texture)
        self.save_button.pack()

        # Canvas for displaying the texture
        self.canvas = Canvas(self.right_frame, width=TEXTURE_SIZE, height=TEXTURE_SIZE, bg="white")
        self.canvas.pack()

        # Initialize the image preview
        self.texture_preview = ImageTk.PhotoImage(
            image=Image.fromarray(np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)))
        self.canvas.create_image(0, 0, anchor="nw", image=self.texture_preview)

    def debounced_update_texture(self, *_):
        # Cancel the previous scheduled update if it exists
        if self.debounce_id:
            self.master.after_cancel(self.debounce_id)

        # Schedule a new update after a short delay (e.g., 200ms)
        self.debounce_id = self.master.after(200, self.update_texture)

    def update_texture(self, *_):
        # Update the texture based on slider values
        for i, slider in enumerate(self.sliders):
            self.component_values[i] = np.clip(slider.get(), -self.slider_ranges[i], self.slider_ranges[i])

        # Reconstruct the texture using the PCA components
        new_texture = mean_texture + np.dot(self.component_values, components)
        new_texture = np.clip(new_texture, 0, 255).astype(np.uint8)  # Ensure valid pixel range
        new_texture = new_texture.reshape((TEXTURE_SIZE, TEXTURE_SIZE, 3))  # Reshape back to image
        new_texture = cv2.cvtColor(new_texture, cv2.COLOR_BGR2RGB)  # Correct color ordering

        # Update the canvas with the new texture
        self.texture_preview = ImageTk.PhotoImage(image=Image.fromarray(new_texture))
        self.canvas.create_image(0, 0, anchor="nw", image=self.texture_preview)

    def randomize_texture(self):
        # Sample PCA coefficients from the multivariate Gaussian
        sampled_coefficients = np.random.normal(0, np.sqrt(pca.explained_variance_), size=n_components)
        self.component_values = sampled_coefficients

        # Update sliders and texture
        for i, value in enumerate(self.component_values):
            self.sliders[i].set(value)
        self.update_texture()

    def project_to_nearest(self):
        for i in range(len(self.component_values)):
            self.component_values[i] = np.clip(self.component_values[i], coeff_min[i], coeff_max[i])
            self.sliders[i].set(self.component_values[i])

    def randomize_natural_texture(self):
        # Sample random PCA coefficients from GMM model
        sampled_coefficients = gmm.sample(1)[0][0]
        self.component_values = sampled_coefficients

        # Update sliders and texture
        for i, value in enumerate(self.component_values):
            self.sliders[i].set(value)

        self.update_texture()

    def reverse_texture(self):
        for i in range(len(self.component_values)):
            self.component_values[i] = -self.component_values[i]
            self.sliders[i].set(self.component_values[i])
        self.update_texture()

    def save_texture(self):
        # Save the current texture
        new_texture = mean_texture + np.dot(self.component_values, components)
        new_texture = np.clip(new_texture, 0, 255).astype(np.uint8)
        new_texture = new_texture.reshape((TEXTURE_SIZE, TEXTURE_SIZE, 3))
        new_texture_rgb = cv2.cvtColor(new_texture, cv2.COLOR_BGR2RGB)  # Correct for RGB

        # Save the texture as a PNG file
        save_path = os.path.join(OUTPUT_PATH, "generated_texture.png")
        cv2.imwrite(save_path, cv2.cvtColor(new_texture_rgb, cv2.COLOR_RGB2BGR))  # Convert back for OpenCV
        print(f"Texture saved to {save_path}")

    def import_texture(self):
        # Open file dialog to import a texture
        texture_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not texture_path:
            return

        # Load and preprocess the texture
        imported_texture = cv2.imread(texture_path)
        imported_texture = cv2.resize(imported_texture, (TEXTURE_SIZE, TEXTURE_SIZE))
        imported_texture = imported_texture.reshape(-1).astype(np.float32)

        # Transform the imported texture to PCA space
        self.component_values = pca.transform([imported_texture])[0]

        # Update sliders based on the imported texture
        for i, value in enumerate(self.component_values):
            self.sliders[i].set(value)

        # Update texture preview
        self.update_texture()


# Main application loop
if __name__ == "__main__":
    root = Tk()
    gui = TextureGeneratorGUI(root)
    root.mainloop()
