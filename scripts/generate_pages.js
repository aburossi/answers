const fs = require('fs');
const path = require('path');
const marked = require('marked');

// Define paths
const templatePath = path.join(__dirname, '../templates/template.html');
const markdownDir = path.join(__dirname, '../markdown');
const outputDir = path.join(__dirname, '../generated');

// Ensure the output directory exists
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

// Read the HTML template
const template = fs.readFileSync(templatePath, 'utf-8');

// Function to generate HTML from Markdown
function generateHTML(filename) {
    const markdownPath = path.join(markdownDir, filename);
    const markdown = fs.readFileSync(markdownPath, 'utf-8');
    const htmlContent = marked.parse(markdown);
    const title = path.basename(filename, '.md');

    // Replace placeholders in the template
    let html = template.replace('{{title}}', title);
    html = html.replace('{{content}}', htmlContent);

    return html;
}

// Read all Markdown files and generate HTML
fs.readdir(markdownDir, (err, files) => {
    if (err) {
        console.error('Error reading markdown directory:', err);
        return;
    }

    files.forEach(file => {
        if (path.extname(file) === '.md') {
            const html = generateHTML(file);
            const outputFilename = path.basename(file, '.md') + '.html';
            const outputPath = path.join(outputDir, outputFilename);

            fs.writeFileSync(outputPath, html, 'utf-8');
            console.log(`Generated ${outputPath}`);
        }
    });
});
