from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder
)

class ChatBotPrompts:
    @staticmethod
    def system_prompt() -> SystemMessagePromptTemplate:
        return SystemMessagePromptTemplate.from_template(
          """  You are a helpful AI assistant. 

            - Only use a tool if it is directly relevant to answering the user’s question.  
            - Never repeat the same tool call more than once unless necessary.  
            - If a tool’s output fully answers the question, immediately call the `final_answer` tool and stop.  
            - If no tool is useful, skip tools and directly call `final_answer`.  
            - The `final_answer` tool must be called exactly once, at the end.  
            - Tool outputs will appear in the scratchpad. If the scratchpad already contains the answer, use `final_answer` to return it.  
            - Always use the provided context when possible.  """

        )

    @staticmethod
    def few_shot_prompt() -> FewShotChatMessagePromptTemplate:
        examples = [
            {
                "input": "What is 2 + 3?",
                "output": "Use add_numbers tool to compute 2 + 3, then call the final answer tool with output."
                "answer should be like this => the answer of 2+3 is 5"
            },
            {
                "input": "What is 10 * 5?",
                "output": "Use multiply_numbers tool to compute 10 * 5, then immediately call the final answer tool with output"
                "answer should be like this => the solution of 10*5 is 50."
            },
            {
                "input": "tell me about langchain?",
                "output": "No relevant tools available for this question, so use final answer tool to answer the user."
                "answer should be like this => Langchain is an open-source framework for building applications powered by language models"
                "with some explanation you might add"
            },
                {"input": "tell me about langchain?",
                "output": "No relevant tools available for this question, so use final answer tool to answer the user."
                "answer should never be like this => answer: Langchain is an open-source framework for building applications powered by language models"
            },
        ]

        example_prompt = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template("{input}"),
            AIMessagePromptTemplate.from_template("{output}")
        ])

        return FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples
        )

    @staticmethod
    def user_prompt() -> HumanMessagePromptTemplate:
        return HumanMessagePromptTemplate.from_template("query starts {question} query ends  \n Use the following for context {context}")

    @staticmethod
    def history_intro() -> SystemMessagePromptTemplate:
        return SystemMessagePromptTemplate.from_template("Below is list of your previous interact with user:"
        "this is only chat history do not mix this up with few shot examples")

    @staticmethod
    def build_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ChatBotPrompts.system_prompt(),
            ChatBotPrompts.few_shot_prompt(),
            ChatBotPrompts.history_intro(),
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ChatBotPrompts.user_prompt(),
        ])
