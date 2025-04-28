import tkinter as tk
# Select files, popup messages, and user input
from tkinter import filedialog, messagebox, simpledialog

# Image opening and resizing, in a way Tk can read
from PIL import Image, ImageTk

# Check if file is in library, set up a library, random selection
import os
import json
import random

# Allow webcam access
import cv2

# Categories for manual user selection
CATEGORIES = ["Tops", "Bottoms", "Shoes"]

class ClothingItem:
    """ Represents a clothing item with an image path and category."""
    def __init__(self, image_path, category, size):
        self.image_path = image_path
        self.category = category
        self.size = size


class OutfitGeneratorApp:
    """ Main application class for the Outfit Generator."""
    def __init__(self, root):
        """ Initializes the outfit generator app, sets up GUI, and loads stored data. """
        # Main window setup
        self.root = root
        self.root.title("Outfit Generator")
        self.root.geometry("600x700")
        self.root.configure(bg="#fce3e5")  # Set background color
        
        # Initialize storage
        self.library = {cat: [] for cat in CATEGORIES}
        self.image_refs = {}  # Prevent garbage of Tkinter images

        self.load_library()

        # GUI Widgets, labels, and buttons
        tk.Label(root, text="The Outfit Generator", font=("Times", 24, "bold"), bg="#fce3e5").pack(pady=10)

        # Frame to hold buttons in one row
        button_frame = tk.Frame(root, bg="#fce3e5")
        button_frame.pack(pady=10)

        # Buttons in horizontal row
        tk.Button(button_frame, text="Upload Image", command=self.upload_image, font=("Arial", 12), bg="#0C315C", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Capture Image", command=self.capture_image, font=("Arial", 12), bg="#0C315C", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Library", command=self.clear_library, font=("Arial", 12), bg="#0C315C", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Category", command=self.clear_category, font=("Arial", 12), bg="#0C315C", fg="white").pack(side=tk.LEFT, padx=5)

        self.camera_index = 0  # Default camera is 0
        
        button_frame = tk.Frame(root, bg="#fce3e5")
        button_frame.pack(pady=10)

        # Change Camera Button
        tk.Button(button_frame, text="Change Camera", command=self.change_camera, font=("Arial", 11), bg="#0C315C", fg="white").pack(side=tk.LEFT, padx=5)

        # Separate row for Generate Outfit
        tk.Button(root, text="Generate Outfit", command=self.generate_outfit, font=("Arial", 12), bg="#0C315C", fg="white").pack(pady=15)

        # Styling
        self.canvas = tk.Canvas(root, width=400, height=500, bg="white", highlightthickness=2, highlightbackground="#2F4858")
        self.canvas.pack(pady=20)

    def upload_image(self):
        """ Allows the user to upload an image and categorize it. """
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            category = simpledialog.askstring("Category", "Enter category (Tops, Bottoms, Shoes):").capitalize()
            if category not in CATEGORIES:
                messagebox.showerror("Error", f"Invalid category. Choose from {', '.join(CATEGORIES)}")
                return
            
            # Ask for AU size and validate input
            size_range = ("4-18" if category in ["Tops", "Bottoms"] else "5-13")
            size_prompt = f"Enter AU size ({size_range}):"
            while True:
                try:
                    size = int(simpledialog.askstring("Size Input", size_prompt))
                    if (category in ["Tops", "Bottoms"] and 4 <= size <= 18) or (category == "Shoes" and 5 <= size <= 13):
                        break
                    else:
                        messagebox.showerror("Error", f"Invalid size. Please enter a valid AU size ({size_range}).")
                except ValueError:
                    messagebox.showerror("Error", "Invalid input. Please enter a number.")

            # Save image to correct category and size.        
            self.library[category].append((file_path, size))
            self.save_library()
            messagebox.showinfo("Uploaded", f"Image added to {category} (Size AU {size})!") # Confirmation of doing so

    def capture_image (self):
        """ Allows user to take their own photo from webcam access. """
        cap = cv2.VideoCapture(self.camera_index) # (1)is front facing camera
        if not cap.isOpened():
            messagebox.showerror("Error","Could not open webcam")
            return
        
        messagebox.showinfo("Webcam", "Press 'SPACE' to capture and 'ESC' to exit.") # Instruction popup

        while True:
            ret, frame = cap.read()
            if not ret: 
                messagebox.showerror("Error", "Failed to capture image, make sure camera is not being used by another program")
                break

            cv2.imshow("Capture image", frame)

            key = cv2.waitKey(1)
            if key == 32: # Spacebar pressed to capture image
                i = 1
                while os.path.exists(F"capture{i}.png"): # Allowing users to capture more than one image.
                    i += 1
                file_path = f"capture{i}.png"  
                cv2.imwrite(file_path, frame)

                cap.release()
                cv2.destroyAllWindows()

                # Categorization 
                category = simpledialog.askstring("Category", "Enter category (Tops, Bottoms, Shoes):").capitalize()
                if category not in CATEGORIES:
                    messagebox.showerror("Error", f"Invalid category. Choose from {', '.join(CATEGORIES)}")
                    return
                
                # Size inputs for categorization
                size_range = ("4-18" if category in ["Tops", "Bottoms"] else "5-13")
                size_prompt = f"Enter AU size ({size_range}):"
                while True:
                    try:
                        size = int(simpledialog.askstring("Size Input", size_prompt))
                        if (category in ["Tops", "Bottoms"] and 4 <= size <= 18) or (category == "Shoes" and 5 <= size <= 13):
                            break
                        else:
                            messagebox.showerror("Error", f"Invalid size. Please enter a valid AU size ({size_range}).") # Error
                    except ValueError:
                        messagebox.showerror("Error", "Invalid input. Please enter a number.") # Error

                # Save to correct category and size
                self.library[category].append((file_path, size))
                self.save_library()
                messagebox.showinfo("Success", f"Image saved to {category}!") # Size
                break

            elif key == 27: # ESC key to escape
                cap.release()
                cv2.destroyAllWindows()
                break

    def change_camera(self):
        """ Allow user to choose camera index between 0 and 3. """
        try:
            index = int(simpledialog.askstring("Camera Selection", "Enter camera index (0-3):"))
            if 0 <= index <= 3:
                self.camera_index = index
                messagebox.showinfo("Camera Changed", f"Camera index set to {index}")
            else:
                messagebox.showerror("Invalid Index", "Please enter a number between 0 and 3.")
        except (ValueError, TypeError):
            messagebox.showerror("Invalid Input", "Please enter a valid number between 0 and 3.")
        

    def generate_outfit(self):
        """ Generates and displays a random outfit from the stored library."""
        self.canvas.delete("all")

        selected_items = {}
        for cat in CATEGORIES:
            if not self.library[cat]:
                messagebox.showwarning("Missing Items", f"No items in category: {cat}") # If one or more categories don't hold any images
                return
            selected_items[cat] = random.choice(self.library[cat])

        # Display images stacked on top of each other
        y_offset = 0
        for cat in CATEGORIES:
            image_path, size = selected_items[cat]
            img = Image.open(image_path)

            # Resize keeping aspect ratio
            max_width, max_height = 300, 120  # Limit inside canvas area

            if cat == "Shoes":
                max_width, max_height = 210, 85  # Smaller dimensions for shoes

            original_width, original_height = img.size
            ratio = min(max_width/original_width, max_height/original_height)
            new_size = (int(original_width * ratio), int(original_height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

            photo = ImageTk.PhotoImage(img)

            # Display the image
            self.canvas.create_image(200, y_offset + new_size[1]//2, image=photo)
            self.image_refs[cat] = photo  # Prevent garbage of image

            # Add AU size below
            self.canvas.create_text(200, y_offset + new_size[1] + 20, text=f"AU Size: {size}", font=("Arial", 10, "italic"), fill="#2F4858")

            y_offset += new_size[1] + 40  # move down for next image + text space

    def clear_library(self):
        """Clears all stored images and resets the library."""
        confirm = messagebox.askyesno("Clear Library", "Are you sure you want to remove all stored images?") # Confirmation
        if confirm:
            self.library = {cat: [] for cat in CATEGORIES}  # Resets library
            self.save_library()
            messagebox.showinfo("Library Cleared", "All stored images have been removed!") # Confirmation

    def clear_category(self):
        """ Clears only images from a selected category. """
        category = simpledialog.askstring("Clear Category", "Enter category to clear (Tops, Bottoms, Shoes):").capitalize() 
        if category not in CATEGORIES:
            messagebox.showerror("Error", f"Invalid category. Choose from {', '.join(CATEGORIES)}") # Error
            return
        if not self.library[category]:
            messagebox.showinfo("Already Empty", f"No images stored in {category}.") # Success
            return
        
        confirm = messagebox.askyesno("Clear Category", f"Are you sure you want to remove all images from {category}?")
        if confirm:
            self.library[category] = []  # Clearing selected category
            self.save_library()
            messagebox.showinfo("Category Cleared", f"All images from {category} have been removed!")

    def save_library(self):
        """ Saves the library to a JSON file."""
        with open("library.json", "w") as f:
            json.dump(self.library, f)

    def load_library(self):
        """ Loads the library from a JSON file if it exists. """
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
