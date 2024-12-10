import os
import tkinter as tk
from tkinter import filedialog, messagebox
import markdown
import shutil  # Für das Kopieren von Dateien

# Funktion zum Auswählen der Bilddatei
def select_image_file():
    filetypes = (
        ("Bilddateien", "*.png *.jpg *.jpeg *.gif *.bmp"),
        ("Alle Dateien", "*.*")
    )
    filepath = filedialog.askopenfilename(title="Bilddatei auswählen", initialdir=os.getcwd(), filetypes=filetypes)
    if filepath:
        image_path_var.set(filepath)

# Funktion zum Generieren der HTML und Einbetten des Bildes
def generate_html():
    title = title_entry.get().strip()
    markdown_text = markdown_textbox.get("1.0", tk.END).strip()
    output_dir = output_dir_var.get().strip()
    image_path = image_path_var.get().strip()  # Bildpfad erhalten

    if not title:
        messagebox.showerror("Input Error", "Bitte gib einen Titel für die HTML-Seite ein.")
        return
    if not markdown_text:
        messagebox.showerror("Input Error", "Bitte gib den Markdown-Inhalt ein.")
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
        messagebox.showerror("Template Error", f"Template-Datei nicht gefunden unter {template_path}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the HTML template
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            template = file.read()
    except Exception as e:
        messagebox.showerror("Template Error", f"Beim Lesen der Template-Datei ist ein Fehler aufgetreten:\n{str(e)}")
        return
    
    # Convert Markdown to HTML
    try:
        html_content = markdown.markdown(markdown_text, extensions=['extra', 'codehilite', 'toc'])
    except Exception as e:
        messagebox.showerror("Markdown Error", f"Beim Konvertieren von Markdown zu HTML ist ein Fehler aufgetreten:\n{str(e)}")
        return
    
    # Optional: Bild hinzufügen
    if image_path:
        if not os.path.isfile(image_path):
            messagebox.showerror("Bild Fehler", f"Die ausgewählte Bilddatei wurde nicht gefunden:\n{image_path}")
            return
        
        # Definiere den Zielpfad für das Bild
        image_filename = os.path.basename(image_path)
        sanitized_image_filename = ''.join(c for c in image_filename if c not in r'<>:"/\|?*')
        destination_image_path = os.path.join(output_dir, sanitized_image_filename)
        
        try:
            # Kopiere die Bilddatei ins Ausgabeordner
            if not os.path.exists(destination_image_path):
                shutil.copy(image_path, destination_image_path)
        except Exception as e:
            messagebox.showerror("Bild Fehler", f"Beim Kopieren der Bilddatei ist ein Fehler aufgetreten:\n{str(e)}")
            return
        
        # Füge den <img>-Tag zum HTML-Inhalt hinzu
        # Optional: Du kannst hier weitere Attribute wie width, height, alt etc. hinzufügen
        img_tag = f'<img src="{sanitized_image_filename}" alt="Bild" style="max-width:100%; height:auto;">'
        html_content += f"\n<br>\n{img_tag}"  # Fügt das Bild nach dem Inhalt ein
    
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
        overwrite = messagebox.askyesno("Datei existiert", f"Die Datei '{filename}' existiert bereits. Möchtest du sie überschreiben?")
        if not overwrite:
            return
    
    # Write the HTML file
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(html_page)
        messagebox.showinfo("Erfolg", f"HTML-Seite '{filename}' wurde erfolgreich generiert!\n\nOrt: {output_path}")
        
        # Clear the inputs
        title_entry.delete(0, tk.END)
        markdown_textbox.delete("1.0", tk.END)
        image_path_var.set("")  # Leere das Bildfeld
    except Exception as e:
        messagebox.showerror("Fehler", f"Beim Schreiben der HTML-Datei ist ein Fehler aufgetreten:\n{str(e)}")

# Funktion zum Auswählen des Ausgabeordners (besteht bereits)
def select_output_directory():
    directory = filedialog.askdirectory()
    if directory:
        output_dir_var.set(directory)

# Initialize the main window
root = tk.Tk()
root.title("Markdown zu HTML Generator")
root.geometry("800x800")  # Erhöhe die Höhe, um Platz für das neue Bildfeld zu haben
root.resizable(False, False)

# Erstelle einen Top-Frame für die oberen Eingabeelemente
top_frame = tk.Frame(root)
top_frame.pack(pady=10, padx=10, anchor='nw')

# HTML Seitentitel Label und Entry
title_label = tk.Label(top_frame, text="HTML Seitentitel:", font=("Arial", 12))
title_label.pack(anchor='w')

title_entry = tk.Entry(top_frame, width=100, font=("Arial", 12))
title_entry.pack(fill='x', pady=(0, 10))

# Ausgabeordner Label und Entry
output_dir_label = tk.Label(top_frame, text="Ausgabeordner:", font=("Arial", 12))
output_dir_label.pack(anchor='w')

output_dir_var = tk.StringVar()
output_dir_entry = tk.Entry(top_frame, textvariable=output_dir_var, width=80, font=("Arial", 12))
output_dir_entry.pack(fill='x', pady=(0, 5))

browse_button = tk.Button(top_frame, text="Durchsuchen", command=select_output_directory, font=("Arial", 10))
browse_button.pack(anchor='e', pady=(0, 10))

# Optionales Bild Label und Entry
image_label = tk.Label(top_frame, text="Optionales Bild:", font=("Arial", 12))
image_label.pack(anchor='w')

image_path_var = tk.StringVar()
image_path_entry = tk.Entry(top_frame, textvariable=image_path_var, width=80, font=("Arial", 12), state='readonly')
image_path_entry.pack(fill='x', pady=(0, 5))

browse_image_button = tk.Button(top_frame, text="Bild auswählen", command=select_image_file, font=("Arial", 10))
browse_image_button.pack(anchor='e', pady=(0, 10))

# Generate Button
generate_button = tk.Button(top_frame, text="HTML Generieren", command=generate_html, font=("Arial", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
generate_button.pack(anchor='e', pady=(0, 10))

# Markdown Label und Textbox
markdown_label = tk.Label(root, text="Markdown Inhalt:", font=("Arial", 12))
markdown_label.pack(anchor='w', padx=10)

markdown_textbox = tk.Text(root, width=95, height=20, font=("Arial", 12), wrap=tk.WORD)
markdown_textbox.pack(pady=(0, 20), padx=10)

# Starte die GUI-Ereignisschleife
root.mainloop()
