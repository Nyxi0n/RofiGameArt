#!/usr/bin/env python3.12
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os
from steamgrid import SteamGridDB

# Replace with your SteamGridDB API key
API_KEY = "YOUR-API-Key"
sgdb = SteamGridDB(API_KEY)
DOWNLOAD_PATH = "~/downloads/"

class BoxArtDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SteamGridDB Box Art Downloader")
        self.geometry("600x500")
        
        # Create download path if it doesn't exist
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
        
        # Search bar and label
        self.search_label = tk.Label(self, text="Enter Game Name:")
        self.search_label.pack(pady=10)
        self.search_entry = tk.Entry(self, width=40)
        self.search_entry.pack(pady=5)
        
        # Search button
        self.search_button = tk.Button(self, text="Search", command=self.search_box_art)
        self.search_button.pack(pady=10)
        
        # Results frame
        self.results_frame = tk.Frame(self)
        self.results_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
    def search_box_art(self):
        game_name = self.search_entry.get()
        if game_name:
            try:
                # Search for games on SteamGridDB by name
                games = sgdb.search_game(game_name)
                if games:
                    # Automatically retrieve and display grid images for the first matching game
                    self.show_results(games[0].id, game_name)  # Pass the ID and name of the first match
                else:
                    messagebox.showinfo("No Results", "No games found with that name.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to search: {e}")

    def show_results(self, game_id, game_name):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get all grid images associated with the game ID
            grids = sgdb.get_grids_by_gameid([game_id])
            
            # Display the first 5 images
            for img in grids[:5]:  # Adjust the slice as needed
                self.display_image(img, game_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load images: {e}")
    
    def display_image(self, img, game_name):
        image_url = img.url
        image_response = requests.get(image_url)
        image_data = Image.open(BytesIO(image_response.content))
        image_data.thumbnail((100, 100))  # Thumbnail for display
        
        # Create Image in Tkinter-compatible format
        photo = ImageTk.PhotoImage(image_data)
        
        # Display Image and Download Button
        frame = tk.Frame(self.results_frame)
        frame.pack(side=tk.LEFT, padx=10)
        image_label = tk.Label(frame, image=photo)
        image_label.image = photo  # Keep reference to avoid garbage collection
        image_label.pack()
        
        download_button = tk.Button(frame, text="Download", command=lambda url=image_url: self.download_image(url, game_name))
        download_button.pack()

    def download_image(self, url, game_name):
        response = requests.get(url)
        if response.ok:
            # Extract file extension from URL
            file_extension = url.split(".")[-1]
            # Clean up the game name to create a safe file name
            safe_game_name = "".join(char for char in game_name if char.isalnum() or char in "._- ")
            filename = os.path.join(DOWNLOAD_PATH, f"{safe_game_name}.{file_extension}")
            with open(filename, "wb") as f:
                f.write(response.content)
            messagebox.showinfo("Downloaded", f"Image saved as {filename}")
        else:
            messagebox.showerror("Download Failed", "Failed to download the image.")

if __name__ == "__main__":
    app = BoxArtDownloader()
    app.mainloop()
