import getpass
import os

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain.chat_models import init_chat_model


model = init_chat_model("gpt-4o-mini", temperature=0.7)

