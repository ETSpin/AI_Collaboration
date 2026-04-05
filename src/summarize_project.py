import ast
import os
import textwrap


def extract_docstring(node):
    """Return cleaned docstring or empty string."""
    doc = ast.get_docstring(node)
    return textwrap.dedent(doc).strip() if doc else ""

def summarize_file(path):
    """Parse a Python file and extract module, class, and function summaries."""
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    summary = {
        "file": os.path.basename(path),
        "module_doc": extract_docstring(tree),
        "classes": [],
        "functions": []
    }

    for node in tree.body:
        # -------------------------
        # Top-level functions
        # -------------------------
        if isinstance(node, ast.FunctionDef):
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
    """Walk a directory and summarize all .py files."""
    summaries = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                summaries.append(summarize_file(path))

    return summaries


def format_summary(summaries):
    """Format the extracted data into a clean, readable text block."""
    output = []

    for s in summaries:
        output.append(f"\nFILE: {s['file']}")
        output.append("-" * 60)

        if s["module_doc"]:
            output.append("Module Docstring:")
            output.append(textwrap.indent(s["module_doc"], "  "))
            output.append("")

        # -------------------------
        # Classes
        # -------------------------
        if s["classes"]:
            output.append("Classes:")
            for cls in s["classes"]:
                output.append(f"  class {cls['name']}({', '.join(cls['bases'])})")
                if cls["doc"]:
                    output.append(textwrap.indent(cls["doc"], "    "))
                else:
                    output.append("    (no class docstring)")

                # Methods
                for m in cls["methods"]:
                    args = ", ".join(m["args"])
                    output.append(f"    def {m['name']}({args})")
                    if m["doc"]:
                        output.append(textwrap.indent(m["doc"], "      "))
                    else:
                        output.append("      (no method docstring)")
                output.append("")

        # -------------------------
        # Top-level functions
        # -------------------------
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

    return "\n".join(output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Summarize Python project structure.")
    parser.add_argument("directory", help="Directory to scan for .py files")
    parser.add_argument("-o", "--output", help="Output file (optional)", default=None)

    args = parser.parse_args()

    summaries = summarize_directory(args.directory)
    formatted = format_summary(summaries)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(formatted)
        print(f"Summary written to {args.output}")
    else:
        print(formatted)
