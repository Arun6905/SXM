from fastmcp import FastMCP
import ast
import traceback
import re

# Create MCP instance
mcp = FastMCP("Debug_Server")


# ----------------------------------------------------
# PYTHON ANALYZER
# ----------------------------------------------------

@mcp.tool()
def analyze_code(code: str) -> dict:
    """
    Analyze Python code and detect syntax/runtime errors.
    """

    try:
        ast.parse(code)

        compiled = compile(code, "<string>", "exec")
        exec(compiled, {})

        return {
            "bug_found": False,
            "bug_line": None,
            "error_type": None,
            "error_message": "No error detected."
        }

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        line_number = tb[-1].lineno if tb else getattr(e, 'lineno', None)

        return {
            "bug_found": True,
            "bug_line": line_number,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


# ----------------------------------------------------
# C++ ANALYZER (Basic Static Version)
# ----------------------------------------------------

@mcp.tool()
def analyze_cpp(code: str) -> dict:
    """
    Basic C++ static analysis (pattern-based).
    """

    lines = code.split("\n")
    bugs = []

    for i, line in enumerate(lines, start=1):

        # Missing semicolon detection
        if (
            line.strip() and
            not line.strip().startswith("//") and
            not line.strip().endswith(";") and
            not line.strip().endswith("{") and
            not line.strip().endswith("}") and
            "(" not in line and
            "=" in line
        ):
            bugs.append({
                "line_number": i,
                "error_type": "SyntaxError",
                "error_message": "Possible missing semicolon."
            })

        # Division by zero
        if re.search(r"/\s*0", line):
            bugs.append({
                "line_number": i,
                "error_type": "RuntimeError",
                "error_message": "Possible division by zero."
            })

        # Using namespace std missing
        if "cout" in line and "std::" not in line:
            bugs.append({
                "line_number": i,
                "error_type": "NamespaceError",
                "error_message": "cout used without std::"
            })

    if not bugs:
        return {
            "bug_found": False,
            "bug_line": None,
            "error_type": None,
            "error_message": "No major issues detected."
        }

    # Return first bug (your planner expects single bug)
    first_bug = bugs[0]

    return {
        "bug_found": True,
        "bug_line": first_bug["line_number"],
        "error_type": first_bug["error_type"],
        "error_message": first_bug["error_message"]
    }


# ----------------------------------------------------
# RUN SERVER
# ----------------------------------------------------

if __name__ == "__main__":
    print("Starting Debug MCP Server...")
    mcp.run(transport="sse", port=8004)