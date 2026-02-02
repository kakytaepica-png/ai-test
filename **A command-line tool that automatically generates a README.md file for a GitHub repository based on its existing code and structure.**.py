import os
import sys
import argparse

def get_file_extension(filename):
    """Extracts the file extension from a filename."""
    return os.path.splitext(filename)[1].lower()

def infer_language_from_extension(extension):
    """Infers programming language from file extension."""
    language_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".c": "C",
        ".cpp": "C++",
        ".cs": "C#",
        ".go": "Go",
        ".rb": "Ruby",
        ".php": "PHP",
        ".html": "HTML",
        ".css": "CSS",
        ".sh": "Shell Script",
        ".md": "Markdown",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".xml": "XML",
        ".sql": "SQL",
        ".txt": "Text",
    }
    return language_map.get(extension, "Unknown")

def analyze_directory(root_dir, exclude_dirs=None, exclude_files=None):
    """Analyzes the repository structure and identifies languages."""
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', 'venv', 'node_modules', 'build', 'dist']
    if exclude_files is None:
        exclude_files = []

    language_counts = {}
    file_counts = {}
    total_files = 0
    code_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Apply directory exclusions
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            if filename in exclude_files:
                continue

            filepath = os.path.join(dirpath, filename)
            extension = get_file_extension(filename)
            language = infer_language_from_extension(extension)

            if language != "Unknown":
                language_counts[language] = language_counts.get(language, 0) + 1
                code_files.append(filepath)

            file_counts[filename] = file_counts.get(filename, 0) + 1
            total_files += 1

    return language_counts, code_files, total_files

def generate_readme(repo_name, description, languages, code_files, total_files):
    """Generates the README.md content."""
    readme_content = f"# {repo_name}\n\n"
    readme_content += f"{description}\n\n"

    if languages:
        readme_content += "## Language Breakdown\n\n"
        for lang, count in sorted(languages.items(), key=lambda item: item[1], reverse=True):
            readme_content += f"- {lang}: {count}\n"
        readme_content += "\n"

    if code_files:
        readme_content += "## Project Structure\n\n"
        readme_content += "### Key Files and Directories:\n\n"
        # Displaying a limited number of files for brevity, can be expanded
        max_files_to_list = 15
        listed_files = 0
        for f in sorted(code_files):
            if listed_files < max_files_to_list:
                readme_content += f"- `{os.path.relpath(f, '.')}`\n"
                listed_files += 1
            else:
                readme_content += f"- ... and {len(code_files) - max_files_to_list} more files.\n"
                break
        readme_content += "\n"

    readme_content += "## Getting Started\n\n"
    readme_content += "To get started with this project:\n\n"
    readme_content += "1. Clone the repository:\n"
    readme_content += "   ```bash\n"
    readme_content += f"   git clone [your-repo-url]\n"
    readme_content += "   ```\n\n"
    readme_content += "2. Navigate to the project directory:\n"
    readme_content += "   ```bash\n"
    readme_content += "   cd [your-repo-name]\n"
    readme_content += "   ```\n\n"
    readme_content += "3. (Optional) Follow specific setup instructions for the project.\n\n"

    readme_content += "## Contributing\n\n"
    readme_content += "Contributions are welcome! Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file (if it exists) for details on how to contribute.\n\n"

    readme_content += "## License\n\n"
    readme_content += "This project is licensed under the [LICENSE](LICENSE) file (if it exists).\n"

    return readme_content

def main():
    parser = argparse.ArgumentParser(description="Generate a README.md file for a GitHub repository.")
    parser.add_argument("repo_name", help="The name of the repository.")
    parser.add_argument("-d", "--description", default="A brief description of the project.", help="A short description of the repository.")
    parser.add_argument("-o", "--output", default="README.md", help="The output filename for the README.md file.")
    parser.add_argument("--exclude-dir", action="append", default=[], help="Directory to exclude from analysis (can be used multiple times).")
    parser.add_argument("--exclude-file", action="append", default=[], help="File to exclude from analysis (can be used multiple times).")

    args = parser.parse_args()

    # Add default exclusions to user-provided exclusions
    default_exclude_dirs = ['.git', '__pycache__', 'venv', 'node_modules', 'build', 'dist', '.env', 'dist', 'coverage']
    all_exclude_dirs = default_exclude_dirs + args.exclude_dir

    all_exclude_files = args.exclude_file

    print("Analyzing repository structure...")
    languages, code_files, total_files = analyze_directory(".", exclude_dirs=all_exclude_dirs, exclude_files=all_exclude_files)
    print(f"Analysis complete. Found {total_files} files, with {len(code_files)} identified as code files.")

    readme_content = generate_readme(args.repo_name, args.description, languages, code_files, total_files)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(readme_content)
        print(f"Successfully generated '{args.output}'.")
    except IOError as e:
        print(f"Error writing to file '{args.output}': {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
