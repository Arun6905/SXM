import asyncio
from fastmcp import Client


# ---------------------------------------
# Code Analysis Agent
# ---------------------------------------

class CodeAgent:

    async def analyze(self, client, code: str, language: str):

        # Select MCP tool based on language
        if language == "Python":
            tool_name = "analyze_code"
        else:
            tool_name = "analyze_cpp"

        result = await client.call_tool(
            tool_name,
            {"code": code}
        )

        return result.data   # 🔥 FastMCP 2.x fix


# ---------------------------------------
# Verification Agent
# ---------------------------------------

class VerificationAgent:

    async def verify(self, client, corrected_code: str, language: str):

        if language == "Python":
            tool_name = "analyze_code"
        else:
            tool_name = "analyze_cpp"

        result = await client.call_tool(
            tool_name,
            {"code": corrected_code}
        )

        result = result.data  # 🔥 FastMCP fix

        if not result.get("bug_found", False):
            return {
                "verification_passed": True,
                "verification_message": "Corrected code executed successfully."
            }
        else:
            return {
                "verification_passed": False,
                "verification_message": result.get("error_message", "Verification failed.")
            }


# ---------------------------------------
# Planner Agent (Main Orchestrator)
# ---------------------------------------

class PlannerAgent:

    def __init__(self):
        self.code_agent = CodeAgent()
        self.verification_agent = VerificationAgent()

    async def handle_request(self, code: str, language: str):

        async with Client("http://127.0.0.1:8004/sse") as client:

            # -----------------------------
            # Step 1 — Analyze
            # -----------------------------

            error_info = await self.code_agent.analyze(client, code, language)

            if not error_info.get("bug_found", False):
                return {
                    "bug_found": False,
                    "message": "No bugs detected."
                }

            # -----------------------------
            # Step 2 — Prepare Explanation
            # -----------------------------

            explanation = (
                f"{error_info.get('error_type')}: "
                f"{error_info.get('error_message')}"
            )

            corrected_code = self.simple_fix(code, error_info, language)

            # -----------------------------
            # Step 3 — Verification
            # -----------------------------

            verification = await self.verification_agent.verify(
                client,
                corrected_code,
                language
            )

            # -----------------------------
            # Final Response
            # -----------------------------

            return {
                "bug_found": True,
                "bug_line": error_info.get("bug_line"),
                "error_type": error_info.get("error_type"),
                "explanation": explanation,
                "corrected_code": corrected_code,
                "verification": verification
            }

    # ---------------------------------------
    # Simple Fix Logic (Demo Only)
    # ---------------------------------------

    def simple_fix(self, code: str, error_info: dict, language: str):

        if language == "Python":

            error_type = error_info.get("error_type", "")

            # Fix missing colon
            if error_type == "SyntaxError":
                lines = code.split("\n")
                line_no = error_info.get("bug_line", 1) - 1
                
                if "if" in lines[line_no] and not lines[line_no].strip().endswith(":"):
                    lines[line_no] += ":"
                
                return "\n".join(lines)

            # Fix indentation
            if error_type == "IndentationError":
                lines = code.split("\n")
                line_no = error_info.get("bug_line", 1) - 1
                lines[line_no] = "    " + lines[line_no]
                return "\n".join(lines)

            # Fix type error
            if error_type == "TypeError":
                return code.replace("+", ",")  # simple demo fix

        return code

# ---------------------------------------
# Manual Test
# ---------------------------------------

if __name__ == "__main__":

    sample_code = """
a = "5"
b = 10
print(a + b)
"""

    planner = PlannerAgent()

    result = asyncio.run(planner.handle_request(sample_code, "Python"))

    print(result)