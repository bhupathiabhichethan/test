import os
import sys
import subprocess
import platform


EXTENSION_MAP = {
    "java": ".java",
    "python": ".py",
    "c": ".c",
    "cpp": ".cpp",
    "html": ".html",
    "css": ".css",
}

TYPE_ALIASES = {
    "java": "java",
    "j": "java",
    "python": "python",
    "py": "python",
    "c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "html": "html",
    "css": "css",
    "": "all"
}

IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "venv",
    ".venv",
    "__pycache__",
    "node_modules",
    "target",
    "build",
    "dist",
    "Library",
    ".m2",
    ".gradle",
    "sdk",
    "Caches",
    "cache",
    "logs",
    "tmp",
    "temp",
    "vendor",
    "Pods",
    "derivedData",
    "site-packages",
    "lib",
    "bin",
    "include",
    "share",
    "env",
    "numpy_env"
}

IGNORE_PATH_KEYWORDS = {
    "site-packages",
    "dist-packages",
    "ipython",
    "jupyter",
    "anaconda",
    "miniconda",
    "conda",
    "flutter",
    "engine",
    "android/sdk",
    "/test/",
    "/tests/",
    "/mock/",
    "/mocks/",
    "/sample/",
    "/samples/",
    "/example/",
    "/examples/",
    "/library/",
    "/cache/",
    "/caches/",
    "/tmp/",
    "/temp/"
}


def is_comment_line(line_strip):
    return (
        line_strip.startswith("//")
        or line_strip.startswith("#")
        or line_strip.startswith("/*")
        or line_strip.startswith("*")
        or line_strip.startswith("<!--")
    )


def clean_comment_prefix(comment_line):
    line = comment_line.strip()

    prefixes = ["//", "#", "/*", "*", "<!--"]
    for prefix in prefixes:
        if line.startswith(prefix):
            line = line[len(prefix):].strip()
            break

    return line.lower()


def keyword_matches(comment_line, keyword):
    cleaned_comment = clean_comment_prefix(comment_line)
    cleaned_keyword = keyword.strip().lower()
    return cleaned_keyword in cleaned_comment


def is_junk_path(filepath):
    normalized = filepath.replace("\\", "/").lower()

    for word in IGNORE_PATH_KEYWORDS:
        if word in normalized:
            return True

    return False


def score_result(filepath, comment):
    score = 0
    lower_path = filepath.replace("\\", "/").lower()
    lower_comment = clean_comment_prefix(comment)

    if "/desktop/" in lower_path:
        score += 8
    if "/documents/" in lower_path:
        score += 7
    if "/downloads/" in lower_path:
        score += 4
    if "/projects/" in lower_path:
        score += 6
    if "/workspace/" in lower_path:
        score += 6
    if "java(vscode)" in lower_path:
        score += 5

    if lower_comment.startswith("check") or lower_comment.startswith("find"):
        score += 3

    if "logic" in lower_comment or "program" in lower_comment:
        score += 2

    if is_junk_path(filepath):
        score -= 30

    return score


def get_editor_command(editor_name, system):
    editor_name = editor_name.strip().lower()

    if system == "Darwin":
        editor_map = {
            "vscode": ["open", "-a", "Visual Studio Code"],
            "code": ["open", "-a", "Visual Studio Code"],
            "intellij": ["open", "-a", "IntelliJ IDEA"],
            "idea": ["open", "-a", "IntelliJ IDEA"],
            "pycharm": ["open", "-a", "PyCharm"],
            "sublime": ["open", "-a", "Sublime Text"],
            "vim": ["vim"],
            "nano": ["nano"],
            "default": ["open"]
        }
    elif system == "Windows":
        editor_map = {
            "vscode": ["code"],
            "code": ["code"],
            "intellij": ["idea64.exe"],
            "idea": ["idea64.exe"],
            "pycharm": ["pycharm64.exe"],
            "sublime": ["subl.exe"],
            "notepad": ["notepad"],
            "default": ["cmd", "/c", "start", ""]
        }
    else:
        editor_map = {
            "vscode": ["code"],
            "code": ["code"],
            "intellij": ["idea"],
            "idea": ["idea"],
            "pycharm": ["pycharm"],
            "sublime": ["subl"],
            "vim": ["vim"],
            "nano": ["nano"],
            "default": ["xdg-open"]
        }

    return editor_map.get(editor_name)


def open_file_with_editor(filepath):
    system = platform.system()

    print("\nChoose editor to open the file:")
    print("1. VS Code")
    print("2. IntelliJ")
    print("3. PyCharm")
    print("4. Sublime Text")
    if system == "Windows":
        print("5. Notepad")
        print("6. Default App")
        editor_choices = {
            "1": "vscode",
            "2": "intellij",
            "3": "pycharm",
            "4": "sublime",
            "5": "notepad",
            "6": "default"
        }
    else:
        print("5. Vim")
        print("6. Nano")
        print("7. Default App")
        editor_choices = {
            "1": "vscode",
            "2": "intellij",
            "3": "pycharm",
            "4": "sublime",
            "5": "vim",
            "6": "nano",
            "7": "default"
        }

    choice = input("Enter your choice: ").strip()
    editor_name = editor_choices.get(choice)

    if editor_name is None:
        print("Invalid editor choice")
        return

    command = get_editor_command(editor_name, system)

    if command is None:
        print("Unsupported editor")
        return

    try:
        subprocess.run(command + [filepath], check=False)
    except FileNotFoundError:
        print(f"{editor_name} is not installed or not available in PATH")
    except Exception as e:
        print("Error opening file:", e)


def resolve_search_path(path_input):
    if not path_input:
        return os.path.expanduser("~")

    expanded_path = os.path.expanduser(path_input)

    if os.path.isabs(expanded_path):
        return expanded_path

    home_based_path = os.path.join(os.path.expanduser("~"), path_input)
    if os.path.exists(home_based_path):
        return home_based_path

    cwd_based_path = os.path.join(os.getcwd(), path_input)
    return cwd_based_path


def main():
    if len(sys.argv) < 2:
        print('Usage: search-comment "keyword" [path]')
        return

    keyword = sys.argv[1].strip()
    path_input = sys.argv[2].strip() if len(sys.argv) >= 3 else ""

    file_type_input = input(
        "Enter file type (java/python/c/cpp/html/css or press Enter for all): "
    ).strip().lower()

    file_type = TYPE_ALIASES.get(file_type_input)

    if file_type is None:
        print("Invalid file type")
        return

    if file_type == "all":
        file_ext = None
    else:
        file_ext = EXTENSION_MAP[file_type]

    start_dir = resolve_search_path(path_input)

    if not os.path.exists(start_dir):
        print(f"Path does not exist: {start_dir}")
        return

    if not os.path.isdir(start_dir):
        print(f"Not a folder: {start_dir}")
        return

    print(f"\nScanning files from: {start_dir}")
    print("Please wait...\n")

    matches = []
    seen_files = set()

    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

        for file in files:
            if file_ext and not file.endswith(file_ext):
                continue

            filepath = os.path.join(root, file)

            if is_junk_path(filepath):
                continue

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, 1):
                        line_strip = line.strip()

                        if is_comment_line(line_strip) and keyword_matches(line_strip, keyword):
                            if filepath not in seen_files:
                                score = score_result(filepath, line_strip)
                                matches.append((score, filepath, lineno, line_strip))
                                seen_files.add(filepath)
                            break

            except Exception:
                pass

    if not matches:
        print("No files found.")
        return

    matches.sort(key=lambda x: x[0], reverse=True)

    print("Found in files:\n")

    for i, (_, file, line, comment) in enumerate(matches, 1):
        print(f"{i}. {file}")
        print(f"   Line {line}: {comment}\n")

    choice = input(
        "Enter the number of the file you want to open (or press Enter to skip): "
    ).strip()

    if choice == "":
        return

    try:
        index = int(choice) - 1

        if index < 0 or index >= len(matches):
            print("Invalid choice")
            return

        filepath = matches[index][1]
        open_file_with_editor(filepath)

    except ValueError:
        print("Please enter a valid number")