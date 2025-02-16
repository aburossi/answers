import os
import markdown

# --- Extraction Functions ---

def extract_transcript_from_folder1(file_path):
    """
    Extracts the transcript from an MD file in folder1.
    Assumes YAML front matter (if present) is enclosed between lines with only '---'.
    If no YAML is detected, the whole file is treated as transcript.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    transcript_lines = []
    # Check if file starts with YAML front matter
    if lines and lines[0].strip() == '---':
        # Find the closing '---'
        try:
            end_yaml_index = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == '---')
            transcript_lines = lines[end_yaml_index+1:]
        except StopIteration:
            # No closing '---', treat entire file as transcript
            transcript_lines = lines
    else:
        transcript_lines = lines

    return ''.join(transcript_lines).strip()


def extract_text_after_marker(file_path, marker="%-%-%-"):
    """
    Extracts all text after the line that starts with marker in the given file.
    Returns the text (or an empty string if marker not found).
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    marker_index = None
    for idx, line in enumerate(lines):
        if line.strip().startswith(marker):
            marker_index = idx
            break

    if marker_index is not None and marker_index < len(lines) - 1:
        return ''.join(lines[marker_index+1:]).strip()
    else:
        return ""


def find_corresponding_file(filename, folder2):
    """
    Walks through all subdirectories of folder2 to find a file matching filename.
    Returns the full path if found, else None.
    """
    for root, dirs, files in os.walk(folder2):
        if filename in files:
            return os.path.join(root, filename)
    return None


# --- HTML Generation Function ---

def generate_html_from_markdown(markdown_content, title, output_html_path, template_path):
    """
    Converts markdown_content to HTML using the provided template.
    The template should contain placeholders '{{title}}' and '{{content}}'.
    Saves the generated HTML to output_html_path.
    """
    # Read the HTML template
    try:
        with open(template_path, "r", encoding="utf-8") as tf:
            template = tf.read()
    except Exception as e:
        print(f"Error reading template file at {template_path}: {e}")
        return False

    # Convert Markdown to HTML
    html_body = markdown.markdown(markdown_content)

    # Replace placeholders; image placeholder is replaced with empty string (unless you wish to add one)
    html_output = template.replace("{{title}}", title).replace("{{content}}", html_body).replace("{{image}}", "")

    # Write HTML to file
    try:
        with open(output_html_path, "w", encoding="utf-8") as out_file:
            out_file.write(html_output)
        return True
    except Exception as e:
        print(f"Error saving HTML file {output_html_path}: {e}")
        return False


# --- Main Integrated Process ---

def process_files_and_generate_html(folder1, folder2, html_output_dir):
    """
    For each MD file in folder1, extracts the transcript and finds the corresponding
    MD file in folder2 (to get additional text after the marker). Combines the content,
    saves a new Markdown file in folder1, and then converts that Markdown to HTML using
    a template. The HTML file is saved in html_output_dir.
    """
    # Determine template location (assumed to be in the same folder as this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "template.html")
    if not os.path.isfile(template_path):
        print(f"Error: Template file not found at {template_path}.")
        return

    os.makedirs(html_output_dir, exist_ok=True)

    for filename in os.listdir(folder1):
        if not filename.lower().endswith('.md'):
            continue

        file_path1 = os.path.join(folder1, filename)
        print(f"Processing {file_path1}...")

        # Extract transcript from folder1 file
        transcript = extract_transcript_from_folder1(file_path1)

        # Find corresponding file in folder2 subdirectories
        corresponding_file = find_corresponding_file(filename, folder2)
        if not corresponding_file:
            print(f"Warning: No corresponding file for {filename} found in folder2. Skipping.")
            continue

        # Extract text after the marker in the corresponding file
        additional_text = extract_text_after_marker(corresponding_file)
        if not additional_text:
            print(f"Warning: Marker '%-%-%-' not found or no text after marker in {corresponding_file}.")

        # Combine the additional text and transcript
        combined_content = additional_text + "\n\n" + transcript

        # Save the new Markdown file in folder1 with 'answers_' prefix
        new_md_filename = f"answers_{filename}"
        new_md_file_path = os.path.join(folder1, new_md_filename)
        try:
            with open(new_md_file_path, 'w', encoding='utf-8') as md_out:
                md_out.write(combined_content)
            print(f"Generated Markdown file: {new_md_file_path}")
        except Exception as e:
            print(f"Error writing Markdown file {new_md_file_path}: {e}")
            continue

        # Define the title using the original filename (without the 'answers_' prefix)
        title = os.path.splitext(filename)[0]
        # Define HTML output file path
        html_file_path = os.path.join(html_output_dir, f"{title}.html")

        # Generate HTML file from combined markdown content
        success = generate_html_from_markdown(combined_content, title, html_file_path, template_path)
        if success:
            print(f"Generated HTML file: {html_file_path}")
        else:
            print(f"Failed to generate HTML for {new_md_filename}.")


def main():
    folder1 = input("Enter the path for folder1 (MD files with YAML and transcript): ").strip()
    folder2 = input("Enter the path for folder2 (subfolders containing MD files): ").strip()

    # Fixed output directory for HTML files
    html_output_dir = r"D:\OneDrive - bbw.ch\+GIT\answers\output"

    if not os.path.isdir(folder1):
        print(f"Error: {folder1} is not a valid directory.")
        return
    if not os.path.isdir(folder2):
        print(f"Error: {folder2} is not a valid directory.")
        return

    process_files_and_generate_html(folder1, folder2, html_output_dir)


if __name__ == "__main__":
    main()
