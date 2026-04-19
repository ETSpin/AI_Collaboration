import ast
import os
import textwrap


def extract_docstring(node):
    doc = ast.get_docstring(node)
    return textwrap.dedent(doc).strip() if doc else ""

def extract_todos(source):
    todos = []
    for line in source.splitlines():
        line_strip = line.strip()
        if line_strip.startswith("#") and "TODO" in line_strip.upper():
            todos.append(line_strip)
    return todos

def summarize_file(path):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    summary = {
        "file": os.path.basename(path),
        "module_doc": extract_docstring(tree),
        "imports": [],
        "classes": [],
        "functions": [],
        "constants": [],
        "todos": extract_todos(source)
    }

    for node in tree.body:

        # -------------------------
        # Imports
        # -------------------------
        if isinstance(node, ast.Import):
            summary["imports"].append(
                ", ".join([alias.name for alias in node.names])
            )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = ", ".join([alias.name for alias in node.names])
            summary["imports"].append(f"from {module} import {names}")

        # -------------------------
        # Top-level constants
        # -------------------------
        elif isinstance(node, ast.Assign):
            if all(isinstance(t, ast.Name) for t in node.targets):
                for t in node.targets:
                    summary["constants"].append(t.id)

        # -------------------------
        # Top-level functions
        # -------------------------
        elif isinstance(node, ast.FunctionDef):
            summary["functions"].append({
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "doc": extract_docstring(node)
            })

        # -------------------------
        # Classes
        # -------------------------
        elif isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "bases": [ast.unparse(base) for base in node.bases],
                "doc": extract_docstring(node),
                "methods": []
            }

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    class_info["methods"].append({
                        "name": item.name,
                        "args": [arg.arg for arg in item.args.args],
                        "doc": extract_docstring(item)
                    })

            summary["classes"].append(class_info)

    return summary


def summarize_directory(directory):
    summaries = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                summaries.append(summarize_file(path))
    return summaries


def format_summary(summaries):
    output = []

    for s in summaries:
        output.append(f"\nFILE: {s['file']}")
        output.append("-" * 60)

        # Module docstring
        if s["module_doc"]:
            output.append("Module Docstring:")
            output.append(textwrap.indent(s["module_doc"], "  "))
            output.append("")

        # Imports
        if s["imports"]:
            output.append("Imports:")
            for imp in s["imports"]:
                output.append(f"  {imp}")
            output.append("")

        # Constants
        if s["constants"]:
            output.append("Top-level Constants:")
            for c in s["constants"]:
                output.append(f"  {c}")
            output.append("")

        # Classes
        if s["classes"]:
            output.append("Classes:")
            for cls in s["classes"]:
                bases = f"({', '.join(cls['bases'])})" if cls["bases"] else ""
                output.append(f"  class {cls['name']}{bases}")
                if cls["doc"]:
                    output.append(textwrap.indent(cls["doc"], "    "))
                else:
                    output.append("    (no class docstring)")

                for m in cls["methods"]:
                    args = ", ".join(m["args"])
                    output.append(f"    def {m['name']}({args})")
                    if m["doc"]:
                        output.append(textwrap.indent(m["doc"], "      "))
                    else:
                        output.append("      (no method docstring)")
                output.append("")

        # Functions
        if s["functions"]:
            output.append("Top-level Functions:")
            for fn in s["functions"]:
                args = ", ".join(fn["args"])
                output.append(f"  def {fn['name']}({args})")
                if fn["doc"]:
                    output.append(textwrap.indent(fn["doc"], "    "))
                else:
                    output.append("    (no function docstring)")
            output.append("")

        # TODOs
        if s["todos"]:
            output.append("TODO Comments:")
            for todo in s["todos"]:
                output.append(f"  {todo}")
            output.append("")

    return "\n".join(output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Summarize Python project structure.")
    parser.add_argument("directory", help="Directory to scan for .py files")
    parser.add_argument("-o", "--output", help="Output file (optional)", default=None)

    args = parser.parse_args()

    summaries = summarize_directory(args.directory)
    formatted = format_summary(summaries)

    # Always write summary into the target directory as project_summary.txt
    output_path = os.path.join(args.directory, "project_summary.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted)

    print(f"Summary written to {output_path}")
