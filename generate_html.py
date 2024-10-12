import os
import tkinter as tk
from tkinter import filedialog, messagebox
import markdown

# Function to generate HTML from Markdown
def generate_html():
    title = title_entry.get().strip()
    markdown_text = markdown_textbox.get("1.0", tk.END).strip()
    output_dir = output_dir_var.get().strip()

    if not title:
        messagebox.showerror("Input Error", "Please enter a title for the HTML page.")
        return
    if not markdown_text:
        messagebox.showerror("Input Error", "Please enter Markdown content.")
        return

    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "template.html")
    
    # Set default output directory if not specified
    if not output_dir:
        output_dir = os.path.join(script_dir, "output")
    else:
        # Expand user tilde (~) and environment variables
        output_dir = os.path.expandvars(os.path.expanduser(output_dir))
    
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
        messagebox.showerror("Template Error", f"An error occurred while reading the template:\n{str(e)}")
        return
    
    # Convert Markdown to HTML
    try:
        html_content = markdown.markdown(markdown_text, extensions=['extra', 'codehilite', 'toc'])
    except Exception as e:
        messagebox.showerror("Markdown Error", f"An error occurred while converting Markdown to HTML:\n{str(e)}")
        return
    
    # Replace placeholders
    html_page = template.replace("{{title}}", title).replace("{{content}}", html_content)
    
    # Define the output file path
    # Sanitize filename by removing or replacing invalid characters
    invalid_chars = r'<>:"/\|?*'
    sanitized_title = ''.join(c for c in title if c not in invalid_chars)
    filename = f"{sanitized_title}.html"
    output_path = os.path.join(output_dir, filename)
    
    # Check if file already exists
    if os.path.exists(output_path):
        overwrite = messagebox.askyesno("File Exists", f"The file '{filename}' already exists. Do you want to overwrite it?")
        if not overwrite:
            return
    
    # Write the HTML file
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(html_page)
        messagebox.showinfo("Success", f"HTML page '{filename}' has been generated successfully!\n\nLocation: {output_path}")
        # Clear the inputs
        title_entry.delete(0, tk.END)
        markdown_textbox.delete("1.0", tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while writing the HTML file:\n{str(e)}")

# Function to select output directory
def select_output_directory():
    directory = filedialog.askdirectory()
    if directory:
        output_dir_var.set(directory)

# Initialize the main window
root = tk.Tk()
root.title("Markdown to HTML Generator")
root.geometry("800x700")
root.resizable(False, False)

# Title Label and Entry
title_label = tk.Label(root, text="HTML Page Title:", font=("Arial", 12))
title_label.pack(pady=(20, 5))

title_entry = tk.Entry(root, width=100, font=("Arial", 12))
title_entry.pack(pady=(0, 20))

# Markdown Label and Textbox
markdown_label = tk.Label(root, text="Markdown Content:", font=("Arial", 12))
markdown_label.pack()

markdown_textbox = tk.Text(root, width=95, height=20, font=("Arial", 12), wrap=tk.WORD)
markdown_textbox.pack(pady=(0, 20))

# Output Directory Label and Entry
output_dir_label = tk.Label(root, text="Output Directory:", font=("Arial", 12))
output_dir_label.pack()

output_dir_var = tk.StringVar()
output_dir_entry = tk.Entry(root, textvariable=output_dir_var, width=80, font=("Arial", 12))
output_dir_entry.pack(pady=(0, 5))

browse_button = tk.Button(root, text="Browse", command=select_output_directory, font=("Arial", 10))
browse_button.pack(pady=(0, 20))

# Generate Button
generate_button = tk.Button(root, text="Generate HTML", command=generate_html, font=("Arial", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
generate_button.pack(pady=(0, 20))

# Start the GUI event loop
root.mainloop()
