import tkinter as tk
#select files, popup messages and user input
from tkinter import filedialog, messagebox, simpledialog

# image  opening and resizing, in a way Tk can read
from PIL import Image, ImageTk

# Check if file is in library, set up a library, random selection
import os
import json
import random

# Categories for manual user selection
CATEGORIES = ["Tops", "Bottoms", "Shoes"]

class ClothingItem:
    def __init__(self, image_path, category):
        self.image_path = image_path
        self.category = category

class OutfitGeneratorApp:
    def __init__(self, root):
        #main window and size
        self.root = root
        self.root.title("Outfit Generator")
        self.root.geometry("600x700")
        self.root.configure(bg="#fce3e5")  # Set background color
        
        # Initialize storage
        self.library = {cat: [] for cat in CATEGORIES}
        self.image_refs = {}  # Needed to prevent garbage collection of Tkinter images

        self.load_library()

        # GUI Widgets, labels and buttons
        tk.Label(root, text="Upload Clothing Items", font=("Arial", 14, "bold"), bg="#fce3e5").pack(pady=10)
        tk.Button(root, text="Upload Image", command=self.upload_image, font=("Arial", 12), bg="#000080", fg="white").pack()
        tk.Button(root, text="Generate Outfit", command=self.generate_outfit, font=("Arial", 12), bg="#000080", fg="white").pack(pady=10)
        
        # Buttons to clear library
        tk.Button(root, text="Clear Library", command=self.clear_library, font=("Arial", 12), bg="#000080", fg="white").pack(pady=10)
        tk.Button(root, text="Clear Category", command=self.clear_category, font=("Arial", 12), bg="#000080", fg="white").pack(pady=5)

        #styling
        self.canvas = tk.Canvas(root, width=400, height=500, bg="white", highlightthickness=2, highlightbackground="#2F4858")
        self.canvas.pack(pady=20)

    # Allowing users to upload file
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            category = simpledialog.askstring("Category", "Enter category (Tops, Bottoms, Shoes):").capitalize()
            if category not in CATEGORIES:
                messagebox.showerror("Error", f"Invalid category. Choose from {', '.join(CATEGORIES)}")
                return
            self.library[category].append(file_path)
            self.save_library()
            messagebox.showinfo("Uploaded", f"Image added to {category}!")

    # Generate a random outfit
    def generate_outfit(self):
        self.canvas.delete("all")

        selected_items = {}
        for cat in CATEGORIES:
            if not self.library[cat]:
                messagebox.showwarning("Missing Items", f"No items in category: {cat}")
                return
            selected_items[cat] = random.choice(self.library[cat])

        # Display images stacked on top of each other
        y_offset = 0
        for cat in CATEGORIES:
            image_path = selected_items[cat]
            img = Image.open(image_path).resize((300, 150))
            photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(200, y_offset + 75, image=photo)  # 200 = center
            self.image_refs[cat] = photo  # Prevent garbage collection
            y_offset += 160

    def clear_library(self):
        # Clears all stored images and resets the library.
        confirm = messagebox.askyesno("Clear Library", "Are you sure you want to remove all stored images?")
        if confirm:
            self.library = {cat: [] for cat in CATEGORIES}  # Reset library
            self.save_library()
            messagebox.showinfo("Library Cleared", "All stored images have been removed!")

    def clear_category(self):
        # Clears only images from a selected category.
        category = simpledialog.askstring("Clear Category", "Enter category to clear (Tops, Bottoms, Shoes):").capitalize()
        if category not in CATEGORIES:
            messagebox.showerror("Error", f"Invalid category. Choose from {', '.join(CATEGORIES)}")
            return
        if not self.library[category]:
            messagebox.showinfo("Already Empty", f"No images stored in {category}.")
            return
        
        confirm = messagebox.askyesno("Clear Category", f"Are you sure you want to remove all images from {category}?")
        if confirm:
            self.library[category] = []  # Clear selected category
            self.save_library()
            messagebox.showinfo("Category Cleared", f"All images from {category} have been removed!")

    def save_library(self):
        with open("library.json", "w") as f:
            json.dump(self.library, f)

    def load_library(self):
        if os.path.exists("library.json"):
            with open("library.json", "r") as f:
                try:
                    self.library = json.load(f)
                except json.JSONDecodeError:
                    pass

if __name__ == "__main__":
    root = tk.Tk()
    app = OutfitGeneratorApp(root)
    root.mainloop()
