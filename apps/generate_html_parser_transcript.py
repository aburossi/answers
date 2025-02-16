import os
import re
import markdown

# --- Extraction Functions ---

def extract_transcript_from_folder1(file_path):
    """
    Extracts the transcript from an MD file in folder1.
    If YAML front matter is present (enclosed between lines with only '---'),
    the code searches for a line starting with "## Transcript" after the YAML block.
    - If found, extraction starts at that line.
    - If not found, the heading "## Transcript" is inserted at the beginning.
    If no YAML is present, the entire file is returned as-is.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if lines and lines[0].strip() == '---':
        # YAML front matter exists.
        try:
            end_yaml_index = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == '---')
        except StopIteration:
            end_yaml_index = 0  # Fallback if no closing marker is found.

        transcript_start_index = None
        for i in range(end_yaml_index + 1, len(lines)):
            if lines[i].strip().startswith("## Transcript"):
                transcript_start_index = i
                break

        if transcript_start_index is not None:
            transcript_lines = lines[transcript_start_index:]
        else:
            # Insert "## Transcript" heading since it's not present.
            transcript_lines = ["## Transcript\n"] + lines[end_yaml_index + 1:]
    else:
        # No YAML front matter; return entire file.
        transcript_lines = lines

    return ''.join(transcript_lines).strip()


def extract_text_after_marker(file_path, marker="%-%-%-"):
    """
    Extracts all text after the line that starts with the marker in the given file.
    Returns the text (or an empty string if the marker is not found).
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    marker_index = None
    for idx, line in enumerate(lines):
        if line.strip().startswith(marker):
            marker_index = idx
            break

    if marker_index is not None and marker_index < len(lines) - 1:
        return ''.join(lines[marker_index + 1:]).strip()
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


# --- Additional Text Processing ---

def process_additional_text(raw_text):
    """
    Processes the raw text extracted from folder2 (i.e. after '%-%-%-') and returns
    a cleaned Markdown string with the following structure:
      - The original heading (e.g. "# LP-MATERIAL")
      - A new heading "## Antworten Verständnisfragen"
      - A clean numbered list of answers extracted from the lines after a warning marker (">[!warning]")
    
    It does so by:
      1. Finding the first heading (line starting with '#').
      2. Locating the line starting with ">[!warning]".
      3. Collecting subsequent lines (that start with '>') as answer items.
      4. Removing the leading ">" and any existing numbering, then re-numbering them.
    """
    lines = raw_text.splitlines()
    lp_heading = ""
    answers_lines = []
    
    # 1. Get the LP-MATERIAL heading (first line that starts with '#')
    for line in lines:
        if line.strip().startswith("#"):
            lp_heading = line.strip()
            break
    
    # 2. Find the index of the warning line (line starting with ">[!warning]")
    warning_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith(">[!warning]"):
            warning_index = i
            break
    if warning_index is None:
        # If no warning marker is found, return the original text unchanged.
        return raw_text

    # 3. Collect all lines after the warning line that start with ">"
    for line in lines[warning_index+1:]:
        stripped_line = line.strip()
        if stripped_line.startswith(">"):
            # Remove the leading ">" and any surrounding whitespace.
            clean_line = stripped_line[1:].strip()
            answers_lines.append(clean_line)
        else:
            continue

    # 4. Reformat the answers as a clean numbered list.
    numbered_list = []
    for idx, ans in enumerate(answers_lines, start=1):
        # Remove any existing numbering (if present) using regex.
        ans = re.sub(r'^\d+\.\s*', '', ans)
        numbered_list.append(f"{idx}. {ans}")
    
    # Build the final processed text.
    final_text = lp_heading + "\n\n" + "## Antworten Verständnisfragen" + "\n\n" + "\n".join(numbered_list)
    return final_text


# --- HTML Generation Function ---

def generate_html_from_markdown(markdown_content, title, output_html_path, template_path):
    """
    Converts markdown_content to HTML using the provided template.
    The template should contain placeholders '{{title}}' and '{{content}}'.
    Saves the generated HTML to output_html_path.
    """
    try:
        with open(template_path, "r", encoding="utf-8") as tf:
            template = tf.read()
    except Exception as e:
        print(f"Error reading template file at {template_path}: {e}")
        return False

    html_body = markdown.markdown(markdown_content)

    # Replace placeholders; the image placeholder is replaced with an empty string.
    html_output = template.replace("{{title}}", title)\
                          .replace("{{content}}", html_body)\
                          .replace("{{image}}", "")

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
    For each MD file in folder1, extracts the transcript (ensuring the "## Transcript" heading is included)
    and finds the corresponding MD file in folder2 (to get additional text after the marker).
    It then:
      1. Processes the additional text to create a clean Markdown section containing:
         - The original LP heading
         - A new heading "## Antworten Verständnisfragen"
         - A clean numbered list of answers.
      2. Combines this processed additional text with the transcript.
      3. Saves a new Markdown file in folder1.
      4. Converts the combined content into HTML using a template. The HTML file is saved in html_output_dir.
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

        # Extract transcript from folder1 file (ensuring "## Transcript" is included)
        transcript = extract_transcript_from_folder1(file_path1)

        # Find corresponding file in folder2 subdirectories.
        corresponding_file = find_corresponding_file(filename, folder2)
        if not corresponding_file:
            print(f"Warning: No corresponding file for {filename} found in folder2. Skipping.")
            continue

        # Extract raw text after the marker in the corresponding file.
        raw_additional_text = extract_text_after_marker(corresponding_file)
        if not raw_additional_text:
            print(f"Warning: Marker '%-%-%-' not found or no text after marker in {corresponding_file}.")
            continue

        # Process the additional text to clean and reformat it.
        processed_additional_text = process_additional_text(raw_additional_text)

        # Combine the processed additional text and transcript.
        combined_content = processed_additional_text + "\n\n" + transcript

        # Save the new Markdown file in folder1 with 'answers_' prefix.
        new_md_filename = f"answers_{filename}"
        new_md_file_path = os.path.join(folder1, new_md_filename)
        try:
            with open(new_md_file_path, 'w', encoding='utf-8') as md_out:
                md_out.write(combined_content)
            print(f"Generated Markdown file: {new_md_file_path}")
        except Exception as e:
            print(f"Error writing Markdown file {new_md_file_path}: {e}")
            continue

        # Use the original file name (without the 'answers_' prefix) as the title for the HTML file.
        title = os.path.splitext(filename)[0]
        html_file_path = os.path.join(html_output_dir, f"{title}.html")

        success = generate_html_from_markdown(combined_content, title, html_file_path, template_path)
        if success:
            print(f"Generated HTML file: {html_file_path}")
        else:
            print(f"Failed to generate HTML for {new_md_filename}.")


def main():
    folder1 = input("Enter the path for folder1 (MD files with YAML and transcript): ").strip()
    folder2 = input("Enter the path for folder2 (subfolders containing MD files): ").strip()

    # Fixed output directory for HTML files.
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
