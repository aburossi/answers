import os

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
    
    # Find the index of the line that starts with the marker
    marker_index = None
    for idx, line in enumerate(lines):
        if line.strip().startswith(marker):
            marker_index = idx
            break

    if marker_index is not None and marker_index < len(lines) - 1:
        # Return text after the marker line
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

def main():
    folder1 = input("Enter the path for folder1 (MD files with YAML and transcript): ").strip()
    folder2 = input("Enter the path for folder2 (subfolders containing MD files): ").strip()

    # Check if the folders exist
    if not os.path.isdir(folder1):
        print(f"Error: {folder1} is not a valid directory.")
        return
    if not os.path.isdir(folder2):
        print(f"Error: {folder2} is not a valid directory.")
        return

    # Process each MD file in folder1
    for filename in os.listdir(folder1):
        if not filename.lower().endswith('.md'):
            continue

        folder1_file = os.path.join(folder1, filename)
        print(f"Processing {folder1_file}...")

        # Extract transcript from folder1 file
        transcript = extract_transcript_from_folder1(folder1_file)

        # Search for corresponding file in folder2 subdirectories
        corresponding_file = find_corresponding_file(filename, folder2)
        if not corresponding_file:
            print(f"Warning: Could not find a corresponding file for {filename} in folder2.")
            continue

        # Extract text after the marker from the corresponding file
        additional_text = extract_text_after_marker(corresponding_file)
        if not additional_text:
            print(f"Warning: Marker '%-%-%-' not found or no text after marker in {corresponding_file}.")
        
        # Create the new file content: additional_text followed by the transcript
        new_content = additional_text + "\n\n" + transcript

        # Create new file name: answers_<original_filename>
        new_filename = f"answers_{filename}"
        new_file_path = os.path.join(folder1, new_filename)

        with open(new_file_path, 'w', encoding='utf-8') as new_file:
            new_file.write(new_content)

        print(f"Generated {new_file_path}")

if __name__ == "__main__":
    main()
