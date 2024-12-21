import os
import tkinter as tk
from tkinter import filedialog, messagebox
import markdown
import shutil  # For copying files

# Default output directory
default_output_dir = r"D:/OneDrive - bbw.ch/+GIT/answers/output"

# Function to select the image file
def select_image_file():
    filetypes = (
        ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
        ("All files", "*.*")
    )
    filepath = filedialog.askopenfilename(title="Select Image File", initialdir=os.getcwd(), filetypes=filetypes)
    if filepath:
        image_path_var.set(filepath)

# Function to select the output directory
def select_output_dir():
    folder = filedialog.askdirectory(initialdir=default_output_dir, title="Select Output Directory")
    if folder:
        output_dir_var.set(folder)

# Function to generate the HTML and embed the image
def generate_html():
    title = title_entry.get().strip()
    markdown_text = markdown_textbox.get("1.0", tk.END).strip()
    output_dir = output_dir_var.get().strip()
    image_path = image_path_var.get().strip()  # Get the image path

    if not title:
        messagebox.showerror("Input Error", "Please provide a title for the HTML page.")
        return
    if not markdown_text:
        messagebox.showerror("Input Error", "Please provide the Markdown content.")
        return

    # Use the default output directory if none is specified
    if not output_dir:
        output_dir = default_output_dir
    else:
        # Expand user tilde (~) and environment variables
        output_dir = os.path.expandvars(os.path.expanduser(output_dir))

    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "template.html")

    # Check if template exists
    if not os.path.isfile(template_path):
        messagebox.showerror("Template Error", f"Template file not found at {template_path}")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read the HTML template
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            template = file.read()
    except Exception as e:
        messagebox.showerror("Template Error", f"Error reading template file: {e}")
        return

    # Convert Markdown to HTML with line breaks
    html_content = markdown.markdown(markdown_text, extensions=['nl2br'])

    # Embed the HTML content and image into the template
    html_output = template.replace("{{title}}", title).replace("{{content}}", html_content)
    if image_path:
        image_filename = os.path.basename(image_path)
        html_output = html_output.replace("{{image}}", image_filename)

        # Copy the image to the output directory
        try:
            shutil.copy(image_path, os.path.join(output_dir, image_filename))
        except Exception as e:
            messagebox.showerror("File Copy Error", f"Error copying image file: {e}")
            return
    else:
        html_output = html_output.replace("{{image}}", "")

    # Save the generated HTML file
    output_file_path = os.path.join(output_dir, f"{title}.html")
    try:
        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write(html_output)
        messagebox.showinfo("Success", f"HTML file successfully created at {output_file_path}")
    except Exception as e:
        messagebox.showerror("File Save Error", f"Error saving HTML file: {e}")

# Create the main application window
root = tk.Tk()
root.title("HTML Generator with Image Support")

# Variables
image_path_var = tk.StringVar()
output_dir_var = tk.StringVar(value=default_output_dir)

# GUI Elements
tk.Label(root, text="Title:").pack()
title_entry = tk.Entry(root, width=50)
title_entry.pack()

tk.Label(root, text="Markdown Content:").pack()
markdown_textbox = tk.Text(root, width=60, height=15)
markdown_textbox.pack()

tk.Button(root, text="Select Image File", command=select_image_file).pack()
tk.Label(root, textvariable=image_path_var, wraplength=500).pack()

tk.Button(root, text="Change Output Directory", command=select_output_dir).pack()
tk.Label(root, textvariable=output_dir_var, wraplength=500).pack()

tk.Button(root, text="Generate HTML", command=generate_html).pack()

# Start the main loop
root.mainloop()
