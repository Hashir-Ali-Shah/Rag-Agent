from langchain_core.tools import tool, BaseTool
import inspect  

class MathTools:
    """Collection of basic math tools."""

    @staticmethod
    @tool
    async def add_numbers(a: float, b: float) -> float:
        """Add two numbers."""
        return float(a) + float(b)

    @staticmethod
    @tool
    async def multiply_numbers(a: float, b: float) -> float:
        """Multiply two numbers."""
        return float(a) * float(b)

    @staticmethod
    @tool
    async def divide_numbers(a: float, b: float) -> float:
        """Divide two numbers. Raises error if b is zero."""
        a = float(a)
        b = float(b)
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    @staticmethod
    @tool
    async def subtract_numbers(a: float, b: float) -> float:
        """Subtract second number from the first number."""
        return float(a) - float(b)

    @staticmethod
    @tool
    async def final_answer(answer: str) -> str:
        """Use this tool to give the final answer to the user. 
        Always call this at the end instead of repeating other tools."""
        return answer
    
    @classmethod
    def get_tools(cls):
        """Return all @tool-decorated callables from this class."""
        tools = []
        for name, member in inspect.getmembers(cls):
            if isinstance(member, BaseTool):  # catches all LangChain tools
                tools.append(member)
        return tools

if __name__ == "__main__":
    math_tools = MathTools()
    print("hello")
    print(MathTools.get_tools())