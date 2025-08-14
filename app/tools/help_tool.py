from app.main_ref import mcp
from app.services.faq import ask_help


@mcp.tool(name="help", description="Ask a FAQ question to the knowledge base and get the answer.")
async def tool_help(question: str):
    return await ask_help(question)