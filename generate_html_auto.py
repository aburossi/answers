import os
import markdown

def main():
    # Ask for the folder with the .txt files
    input_dir = input("Enter the path to the folder with the .txt files: ").strip()
    # Ask for the folder where the .html files will be saved
    output_dir = input("Enter the path to the folder where the .html files will be saved: ").strip()

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Locate template.html
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "template.html")

    # Check for template file
    if not os.path.isfile(template_path):
        print(f"Template file not found at {template_path}")
        return

    # Read the template HTML
    with open(template_path, "r", encoding="utf-8") as template_file:
        template_html = template_file.read()

    # Process each .txt file in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".txt"):
            txt_path = os.path.join(input_dir, filename)

            # Read the .txt file contents
            with open(txt_path, "r", encoding="utf-8") as txt_file:
                markdown_content = txt_file.read()

            # Convert Markdown to HTML
            content_html = markdown.markdown(markdown_content)

            # Use the filename (without extension) as the title
            base_name = os.path.splitext(filename)[0]
            page_title = base_name

            # Replace placeholders in the template
            # Make sure you use the exact text from your template: {{title}} and {{content}}
            final_html = (template_html
                          .replace("{{title}}", page_title)
                          .replace("{{content}}", content_html))

            # Save the generated HTML in the output directory
            output_html_path = os.path.join(output_dir, f"{base_name}.html")
            with open(output_html_path, "w", encoding="utf-8") as html_file:
                html_file.write(final_html)

    print("HTML generation completed.")

if __name__ == "__main__":
    main()
