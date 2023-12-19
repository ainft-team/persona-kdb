from typing import Optional, Type
from pydantic import BaseModel, Field

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.agents import AgentType, initialize_agent
from langchain.chains import LLMMathChain
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.tools.render import format_tool_to_openai_function
from langchain.utilities import SerpAPIWrapper


# tools = [
#     SoulstoneRewardTool(),
# ]
# agent = initialize_agent(
#     tools, llm, 

class SoulstoneRewardTool(BaseTool):
    name = "soulstone_giver"
    description = "useful for giving users soulstone if they provide good quality of conversation on training Mars"

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        """Use the tool."""
        return self.run(query)
    
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ):
        """Use the tool."""
        return self.arun(query)