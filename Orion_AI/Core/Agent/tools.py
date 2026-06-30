from Core.Agent.schemas import Tool
from skills.file_reader import file_read
from skills.web_search import search_response_adapter
TOOLS = {
      "file_read": Tool(
          name="file_read",
          description='reads a file. args: {"path": "<file path>"}',
          run=file_read,
        ),
        "web_search": Tool(
            name= "web_search",
            description='searches the web for up-to-date information. args: {"query": "<search query>"}',
            run=search_response_adapter,
        )
    }