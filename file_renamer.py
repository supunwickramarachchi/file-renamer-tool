import os
import time
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from customtkinter import CTkProgressBar

rename_log = [] # This will store renamed files to allow undo

def show_preview(folder_path, prefix, filetype):
    preview_box.delete("1.0", tk.END)
    date = datetime.now().strftime("%Y-%b-%d")
    rename_count = sum(1 for file in os.listdir(folder_path) if file.startswith(prefix)) + 1
    
    all_files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]        
    if filetype != "all":
        all_files = [file for file in all_files if os.path.splitext(file)[1].lower() == filetype.lower()]
        
    for filename in all_files:
        if filename.startswith(prefix):
            continue
        
        file_ext = os.path.splitext(filename)[1]
        new_name = f"{prefix}_{date}_{rename_count}{file_ext}"
        preview_box.insert(tk.END, f"{filename} --> {new_name}\n")
        rename_count += 1  

def show_confirmation_popup(callback_yes):
    popup = ctk.CTkToplevel(app)
    popup.title("Confirm Rename")
    popup.resizable(False, False)
    popup.grab_set()
    
    popup_width = 300
    popup_height = 150

    # Get app position
    app.update_idletasks()
    x = app.winfo_x()
    y = app.winfo_y()
    app_width = app.winfo_width()
    app_height = app.winfo_height()

    # Load popup on right side of the app
    right_x = x + app_width + 10  # 10px space to the right
    center_y = y + (app_height // 2) - (popup_height // 2)

    popup.geometry(f"{popup_width}x{popup_height}+{right_x}+{center_y}")
    
    label = ctk.CTkLabel(popup, text="Do you want to rename these files?")
    label.pack(pady=20)
    
    button_frame = ctk.CTkFrame(popup)
    button_frame.pack(pady=10)
    
    def confirm_yes():
        popup.destroy()
        callback_yes()
        
    def confirm_no():
        popup.destroy()
        preview_box.delete("1.0", tk.END)
        
    yes_btn = ctk.CTkButton(button_frame, text="Yes", command=confirm_yes)
    yes_btn.pack(side='left', padx=10)
    
    no_btn = ctk.CTkButton(button_frame, text="No", command=confirm_no)
    no_btn.pack(side='right', padx=10)
    
def file_renamer(folder_path, prefix, filetype):
    global rename_log
    date = datetime.now().strftime("%Y-%b-%d")
    found = False
    existing_count = sum(1 for file in os.listdir(folder_path) if file.startswith(prefix))
    rename_count = existing_count + 1
    actual_renamed = 0
    
    all_files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
    
    if filetype != 'all':
        all_files = [file for file in all_files if os.path.splitext(file)[1] == filetype]
    
    total_files = len(all_files)
    
    if total_files == 0:
        messagebox.showinfo("Info", "No file found to rename.")
        return
    
    progress_bar.set(0)
    app.update_idletasks()
    
    rename_log.clear()
    
    for count, filename in enumerate(all_files):
        if filename.startswith(prefix):
            continue
        
        file_path = os.path.join(folder_path, filename)
        file_ext = os.path.splitext(filename)[1]
        new_name = f"{prefix}_{date}_{rename_count}{file_ext}"
        new_path = os.path.join(folder_path, new_name)
        
        os.rename(file_path, new_path)
        print(f"Renamed: {filename} --> {new_name}")
        rename_count += 1
        actual_renamed += 1
        
        rename_log.append((new_path, file_path)) # Save new and original paths
        
        # Update progess bar
        progress = (count + 1) / total_files
        progress_bar.set(progress)
        app.update_idletasks()
        time.sleep(0.10)
                        
    if actual_renamed == 0:
        messagebox.showinfo("Info", "No file found to rename.")
    else:
        messagebox.showinfo("Success: ", f"{actual_renamed} files renamed!")
        preview_box.delete("1.0", tk.END)
        progress_bar.set(0)

def undo_rename():
    if not rename_log:
        messagebox.showinfo("Undo", "No rename actions to undo.")
        return
        
    for new_path, old_path in reversed(rename_log):
        if os.path.exists(new_path):
            os.rename(new_path, old_path)
            
    messagebox.showinfo("Undo", "Rename actions undone.")
    preview_box.delete("1.0", tk.END)
    rename_log.clear()
        

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        prefix = prefix_entry.get()
        filetype = filetype_option.get()
        if not prefix:
            messagebox.showerror("Error: ", "Please enter a prefix!")
            return
        
        show_preview(folder, prefix, filetype)
        
        def after_confirm():
            file_renamer(folder, prefix, filetype)
            prefix_entry.delete(0, tk.END)
            
        
        show_confirmation_popup(after_confirm)
        
def center_window(app, width=400, height=300):
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (width / 2))
    app.geometry(f"{width}x{height}+{x}+{y}")

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("File Renamer Tool")
center_window(app, 500, 400)
app.resizable(False, False)

# Add progress bar
progress_bar = CTkProgressBar(app, width=300)
progress_bar.set(0)
progress_bar.pack(pady=(10, 10))
progress_bar.configure(mode="determinate") 

# Prefix input
prefix_label = ctk.CTkLabel(app, text="Enter prefix:")
prefix_label.pack(pady=(5, 5))

prefix_entry = ctk.CTkEntry(app, width=250, placeholder_text="eg: Renamed_")
prefix_entry.pack(pady=(0, 10))

# File type drop down
filetype_option = ctk.CTkOptionMenu(app, values=["all", ".jpg", ".jpeg", ".png", ".txt", ".pdf"])
filetype_option.set("all")
filetype_option.pack(pady=5)

# Choose folder button 
select_button = ctk.CTkButton(app, text="Choose folder and rename", command=choose_folder)
select_button.pack(pady=20)


# Add Undo button
undo_btn = ctk.CTkButton(app, text="Undo Rename", command=undo_rename)
undo_btn.pack(pady=5)

# preview Box
preview_label = ctk.CTkLabel(app, text="Preview of Renamed Files:")
preview_label.pack(pady=(10, 2))

preview_box = ctk.CTkTextbox(app, height=120, width=400)
preview_box.pack(pady=(0, 10))

app.protocol("WM_DELETE_WINDOW", app.quit)
app.mainloop()


# More functionalies should be added