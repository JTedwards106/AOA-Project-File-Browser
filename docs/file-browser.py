import os
import mimetypes
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

# Azure Cognitive Services summarization
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Azure credentials
endpoint = "https://<your-azure-endpoint>"
key = "<your-azure-key>"

# Initialize the Text Analytics client
credential = AzureKeyCredential(key)
client = TextAnalyticsClient(endpoint=endpoint, credential=credential)

def summarize_file_with_azure(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()

        # Call Azure Text Analytics for text summarization or key phrase extraction
        response = client.extract_key_phrases([content])[0]
        if response.is_error:
            return "Error summarizing the file."

        key_phrases = ", ".join(response.key_phrases)
        return f"Key phrases extracted: {key_phrases}"

    except Exception as e:
        return f"Azure summarization failed: {str(e)}"

class FileBrowserApp:
    def __init__(self, master):
        self.master = master
        master.title("File Explorer")

        # Header Section
        self.header_frame = tk.Frame(master)
        self.header_frame.pack(pady=10)

        self.icon_label = tk.Label(self.header_frame, text="🖥️", font=("Arial", 40))
        self.icon_label.pack(side=tk.LEFT)

        self.resource_var = tk.StringVar(master)
        self.resource_var.set("Select Resource")

        self.resource_options = [
            "Select Resource",
            "Folder",
            "File",
            "Hard Drive",
        ]

        self.resource_menu = tk.OptionMenu(self.header_frame, self.resource_var, *self.resource_options, command=self.resource_selected)
        self.resource_menu.pack(side=tk.LEFT, padx=10)

        self.search_entry = tk.Entry(self.header_frame, width=50)
        self.search_entry.insert(0, "Specify or select a resource")
        self.search_entry.pack(side=tk.LEFT, padx=10)

        self.search_info = tk.Label(self.header_frame, text="Select a resource to explore")
        self.search_info.pack(side=tk.LEFT)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.select_button = tk.Button(self.button_frame, text="Select", command=self.select_resource)
        self.select_button.pack(side=tk.LEFT, padx=5)

        # Table Section
        self.table_frame = tk.Frame(master)
        self.table_frame.pack(pady=10)

        self.table = tk.Frame(self.table_frame)
        self.table.pack()

        self.headers = ["Name", "Size", "Last Modified", "Type", "Summary"]
        for header in self.headers:
            label = tk.Label(self.table, text=header, font=("Arial", 12, "bold"), borderwidth=1, relief="solid", padx=10, pady=5)
            label.grid(row=0, column=self.headers.index(header))

    def resource_selected(self, selection):
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, selection)

    def select_resource(self):
        resource_type = self.resource_var.get()
        if resource_type == "Folder":
            self.select_folder()
        elif resource_type == "File":
            self.select_file()
        elif resource_type == "Hard Drive":
            self.select_drive()
        else:
            messagebox.showwarning("Warning", "Please select a valid resource type.")

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select a Folder")
        if folder_path:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, folder_path)
            self.populate_table(folder_path)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select a File")
        if file_path:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, file_path)
            self.populate_table(os.path.dirname(file_path))  # Show the directory of the selected file

    def select_drive(self):
        # For simplicity, list the C: drive. You could expand to list all available drives.
        drive = "C:\\"
        if os.path.exists(drive):
            self.populate_table(drive)

    def populate_table(self, folder_path):
        # Clear previous entries in the table
        for widget in self.table.grid_slaves():
            if int(widget.grid_info()['row']) > 0:
                widget.destroy()

        try:
            for index, entry in enumerate(os.listdir(folder_path)):
                full_path = os.path.join(folder_path, entry)
                if os.path.isfile(full_path):
                    file_name = os.path.basename(full_path)
                    file_size = os.path.getsize(full_path)
                    last_modified = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
                    file_type = mimetypes.guess_type(full_path)[0] or "Unknown"
                    summary = summarize_file_with_azure(full_path)

                    # Insert file information into the table
                    tk.Label(self.table, text=file_name, borderwidth=1, relief="solid", padx=10, pady=5).grid(row=index + 1, column=0)
                    tk.Label(self.table, text=f"{file_size} bytes", borderwidth=1, relief="solid", padx=10, pady=5).grid(row=index + 1, column=1)
                    tk.Label(self.table, text=last_modified, borderwidth=1, relief="solid", padx=10, pady=5).grid(row=index + 1, column=2)
                    tk.Label(self.table, text=file_type, borderwidth=1, relief="solid", padx=10, pady=5).grid(row=index + 1, column=3)
                    tk.Label(self.table, text=summary, borderwidth=1, relief="solid", padx=10, pady=5).grid(row=index + 1, column=4)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileBrowserApp(root)
    root.mainloop()
