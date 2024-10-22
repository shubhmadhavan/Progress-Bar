import tkinter as tk
from tkinter import colorchooser, ttk, filedialog
import json
import os
from dark_title_bar import dark_title_bar 
import sv_ttk

class ProgressApp(tk.Tk):
    def __init__(self):
        super().__init__()

        dark_title_bar(self)
        sv_ttk.set_theme("dark")
        self.title("Progress Bar App")
        self.geometry("1115x760")




        self.last_file_tracker = "last_file.json"
        self.last_file = self.load_last_file_path()

        self.settings = self.load_settings(self.last_file) if self.last_file else {}

        self.configure(bg=self.settings.get("app_bg", "#f0f0f0"))

        self.create_widgets()

        # Bind keyboard shortcuts
        self.bind_all("<Control-s>", lambda event: self.save_progress())
        self.bind_all("<Control-S>", lambda event: self.save_as())  # Ctrl + Shift + S
        self.bind_all("<Control-l>", lambda event: self.load_data())
        self.bind_all("<Control-r>", lambda event: self.undo_list())  # Ctrl + R to undo the list

        self.load_progress()

    # Add a new method to undo the displayed list
    def undo_list(self):
        self.clear_rows()  # Clear all rows
        self.load_progress()  # Reload from settings

    def create_widgets(self):
        self.menu_bar = tk.Menu(self, bg="white", fg="black")  # Set the menu bar color to black
        self.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=1)
        #self.menu_bar.add_cascade(label="▼", menu=file_menu)  # Change the label from "File" to "▼" 
        #### uncomment above line to show File Menu Bar
        
        file_menu.add_command(label="Save", command=self.save_progress)
        file_menu.add_command(label="Save As", command=self.save_as)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Continue with other widget creation
        ttk.Label(self, text="Name").grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ttk.Label(self, text="Progress").grid(row=0, column=1, padx=12, pady=10, sticky="ew")
        ttk.Label(self, text="Total").grid(row=0, column=2, padx=10, pady=12, sticky="ew")
        ttk.Label(self, text="Progress Bar").grid(row=0, column=3, padx=12, pady=10, sticky="ew")

        self.add_row_button = ttk.Button(self, text="+", command=self.add_row)
        self.add_row_button.place(relx=1.0, rely=0.0, anchor="ne", x=-4.4, y=10)

        self.rows = []

        self.status_label = ttk.Label(self, text="", font=("Arial", 16), foreground="green")
        self.status_label.place(relx=1.0, rely=0.0, anchor="ne", x=-56, y=15) 

        self.grid_columnconfigure(0, minsize=150)
        self.grid_columnconfigure(1, minsize=100)
        self.grid_columnconfigure(2, minsize=100)
        self.grid_columnconfigure(3, minsize=500)
        self.grid_columnconfigure(4, minsize=100)


    def add_row(self, name="", progress=0, total=100, bar_color="#474747"):
        row_index = len(self.rows) + 2

        # Directly set name in the Entry widget instead of using StringVar
        name_entry = ttk.Entry(self, width=15)
        name_entry.insert(0, name)  # Set the name directly in the Entry widget
        name_entry.grid(row=row_index, column=0, padx=10, pady=5, sticky="ew")

        progress_var = tk.IntVar(value=progress)
        total_var = tk.IntVar(value=total)
        bar_color_var = tk.StringVar(value=bar_color)

        # Progress Entry
        progress_entry = ttk.Entry(self, textvariable=progress_var, width=10)
        progress_entry.grid(row=row_index, column=1, padx=10, pady=5, sticky="ew")
        
        # Total Entry
        total_entry = ttk.Entry(self, textvariable=total_var, width=10)
        total_entry.grid(row=row_index, column=2, padx=10, pady=5, sticky="ew")
        
        # Progress bar using Canvas
        canvas = tk.Canvas(self, width=500, height=30, bg=self['bg'], highlightthickness=0)
        canvas.grid(row=row_index, column=3, padx=10, pady=5)

        # Create a border rectangle
        border = canvas.create_rectangle(0, 0, 500, 30, outline="grey", width=2)

        # Create the progress bar rectangle
        bar = canvas.create_rectangle(2, 2, 2, 28, fill=bar_color_var.get(), outline="")

        # Percentage label
        percent_label = ttk.Label(self, text="0%", width=5)
        percent_label.grid(row=row_index, column=4, padx=5)

        # Choose color button
        color_button = ttk.Button(self, text="🖌", command=lambda: self.choose_bar_color(bar_color_var, bar, canvas))
        color_button.grid(row=row_index, column=5, padx=5)

        # Delete row button
        delete_button = ttk.Button(self, text="x", command=lambda: self.delete_row(row_index))
        delete_button.grid(row=row_index, column=6, padx=5)

        def update_progress(*args):
            try:
                progress = float(progress_var.get())
                total = float(total_var.get())
                
                if total > 0 and progress >= 0:
                    percentage = min((progress / total) * 100, 100)
                    canvas.coords(bar, 2, 2, percentage * 5 + 2, 28)  # Scale the bar width
                    percent_label.config(text=f"{int(percentage)}%")
            except ValueError:
                canvas.coords(bar, 2, 2, 2, 28)  # Reset bar
                percent_label.config(text="0%")

        progress_var.trace_add("write", update_progress)
        total_var.trace_add("write", update_progress)
        
        self.rows.append((name_entry, progress_entry, total_entry, canvas, bar, percent_label, bar_color_var, color_button, delete_button))
        
        update_progress()
        
        self.update_idletasks()

        
    def delete_row(self, row_index):
        # First, handle the last row's buttons (🖌 and x) before any deletion happens
        if self.rows:
            last_row = self.rows[-1]
            last_row[7].grid_remove()  # Hide the color button (🖌) on the last row
            last_row[8].grid_remove()  # Hide the delete button (x) on the last row

        adjusted_index = row_index - 2  # Adjust for header row
        if 0 <= adjusted_index < len(self.rows):
            # Get the row to delete
            row_to_delete = self.rows.pop(adjusted_index)

            # Destroy all the actual widgets in the row (0 to 6 are widgets)
            for widget in row_to_delete[:6]:  # Only destroy the first 6 widgets (the actual UI elements)
                if isinstance(widget, tk.Widget):  # Check if it is a Tkinter Widget before destroying
                    widget.destroy()

            # Refresh the rows after deletion
            self.update_rows()

    def update_rows(self):
        """Update the layout of rows after a row is deleted."""
        for i, row in enumerate(self.rows):
            name_entry, progress_entry, total_entry, canvas, bar, percent_label, bar_color_var, color_button, delete_button = row

            # Reassign grid positions for all widgets in the updated row
            name_entry.grid(row=i + 2, column=0, padx=10, pady=5, sticky="ew")
            progress_entry.grid(row=i + 2, column=1, padx=10, pady=5, sticky="ew")
            total_entry.grid(row=i + 2, column=2, padx=10, pady=5, sticky="ew")
            canvas.grid(row=i + 2, column=3, padx=10, pady=5)
            percent_label.grid(row=i + 2, column=4, padx=5)
            color_button.grid(row=i + 2, column=5, padx=5)
            delete_button.grid(row=i + 2, column=6, padx=5)

        # Adjust the last row's color button and delete button (if there are any rows left)
        if self.rows:
            last_row = self.rows[-1]
            last_row[7].grid(row=len(self.rows) + 1, column=5)
            last_row[8].grid(row=len(self.rows) + 1, column=6)



    

    def update_progress_bars(self):
        for index, row in enumerate(self.rows):
            name_var, progress_var, total_var, canvas, bar, percent_label, bar_color_var, color_button, delete_button = row
            try:
                progress = float(progress_var.get())
                total = float(total_var.get())
                if total > 0:
                    percentage = min((progress / total) * 100, 100)
                    canvas.coords(bar, 2, 2, percentage * 5 + 2, 28)
                    percent_label.config(text=f"{int(percentage)}%")
                else:
                    canvas.coords(bar, 2, 2, 2, 28)
                    percent_label.config(text="0%")
            except ValueError:
                canvas.coords(bar, 2, 2, 2, 28)
                percent_label.config(text="0%")

    def choose_bar_color(self, color_var, bar, canvas):
        color = colorchooser.askcolor(title="Choose Progress Bar Color")[1]
        if color:
            color_var.set(color)
            canvas.itemconfig(bar, fill=color)

    def load_progress(self):
        """Load the progress data from settings."""
        self.clear_rows()  # Clear any existing rows first
        for entry in self.settings.get("progress_data", []):
            name = entry.get("name", "")
            progress = entry.get("progress", 0)
            total = entry.get("total", 100)
            bar_color = entry.get("bar_color", "#78f5f3")
            
            # Call add_row with the correct parameters
            self.add_row(name=name, progress=progress, total=total, bar_color=bar_color)




    def load_settings(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
        return {}

    def save_progress(self):

        data = [
            {
                "name": row[0].get(),           # row[0] is the Entry widget for the name
                "progress": row[1].get(),       # row[1] is the progress_var
                "total": row[2].get(),          # row[2] is the total_var
                "bar_color": row[6].get()       # row[6] is the color_var
            } for row in self.rows
        ]
        self.settings["progress_data"] = data
        self.save_settings(self.last_file)
        self.show_status_checkmark()


    def save_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            self.save_settings(file_path)
            self.last_file = file_path
            with open(self.last_file_tracker, "w") as file:
                json.dump({"last_file": self.last_file}, file)
            self.show_status_checkmark()

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.settings = self.load_settings(file_path)
            self.clear_rows()
            self.load_progress()
            self.last_file = file_path
            with open(self.last_file_tracker, "w") as file:
                json.dump({"last_file": self.last_file}, file)

    def save_settings(self, file_path):
        with open(file_path, "w") as file:
            json.dump(self.settings, file)

    def load_last_file_path(self):
        if os.path.exists(self.last_file_tracker):
            with open(self.last_file_tracker, "r") as file:
                try:
                    last_used_file = json.load(file).get("last_file", "")
                    if os.path.exists(last_used_file):
                        return last_used_file
                except json.JSONDecodeError:
                    pass
        return "settings.json"

    def clear_rows(self):
        for row in self.rows:
            for widget in row:
                if isinstance(widget, tk.Widget):  # Ensure it's a widget before destroying
                    widget.destroy()
        self.rows.clear()  # Cl

    def show_status_checkmark(self):
        lighter_grey = "#464646"  # A lighter gray gives a faded appearance.
        self.status_label.config(text="💾", foreground=lighter_grey)
        self.after(1000, lambda: self.status_label.config(text=""))

    def on_closing(self):
        self.save_progress()
        self.destroy()

if __name__ == "__main__":
    app = ProgressApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
