import os
import markdown

def main():
    # Ask user for the folder containing the .txt files
    input_dir = input("Enter the path to the folder with the .txt files: ").strip()
    # Ask user for the folder where the HTML files should be saved
    output_dir = input("Enter the path to the folder where the .html files will be saved: ").strip()

    # If the output directory doesn't exist, create it
    os.makedirs(output_dir, exist_ok=True)

    # Specify the path to your template.html (make sure template.html is accessible)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "template.html")

    # Read the template file
    if not os.path.isfile(template_path):
        print(f"Template file not found at {template_path}")
        return

    with open(template_path, "r", encoding="utf-8") as template_file:
        template_html = template_file.read()

    # Traverse each .txt file in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".txt"):
            txt_path = os.path.join(input_dir, filename)

            # Read the content of the .txt file
            with open(txt_path, "r", encoding="utf-8") as txt_file:
                markdown_content = txt_file.read()

            # Convert the file’s content from Markdown to HTML
            content_html = markdown.markdown(markdown_content)

            # Use the file name (minus extension) as the title
            base_name = os.path.splitext(filename)[0]
            page_title = base_name  # Or define your own method of deriving the title

            # Inject title and content into the template
            final_html = template_html.replace("{{ title }}", page_title)
            final_html = final_html.replace("{{ content }}", content_html)

            # Save the generated HTML file in the output directory
            output_html_path = os.path.join(output_dir, base_name + ".html")
            with open(output_html_path, "w", encoding="utf-8") as html_file:
                html_file.write(final_html)

    print("HTML generation completed.")

if __name__ == "__main__":
    main()
