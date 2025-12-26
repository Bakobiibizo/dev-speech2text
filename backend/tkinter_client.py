import tkinter as tk
from tkinter import filedialog, messagebox
from clients.client import TranscriptionManager


class TranscriptionApp:
    def __init__(self, app_root):
        self.root = app_root
        self.root.title("Transcription Manager")
        self.root.geometry("300x300")

        # Create and place input widgets
        tk.Label(self.root, text="Input Folder Path:").pack()
        self.input_folder_entry = tk.Entry(self.root)
        self.input_folder_entry.pack()

        # Button to browse for input folder
        self.browse_button = tk.Button(
            self.root, text="Browse", command=self.browse_folder
        )
        self.browse_button.pack()

        # Button to execute TranscriptionManager.make_request()
        self.transcribe_button = tk.Button(
            self.root, text="Make Request", command=self.make_request
        )
        self.transcribe_button.pack()

        # Transcription Manager instance
        self.transcription_manager = TranscriptionManager()

    def browse_folder(self):
        folder_path = filedialog.askopenfilename()
        self.input_folder_entry.delete(0, tk.END)
        self.input_folder_entry.insert(0, folder_path)

    def make_request(self):
        input_path = self.input_folder_entry.get()
        try:
            # Assuming make_request() takes input and output paths
            self.transcription_manager.make_request(input_path)
            messagebox.showinfo("Success", "Request made successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptionApp(root)
    root.mainloop()
