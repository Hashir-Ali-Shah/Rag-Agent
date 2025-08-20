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
            "You are a helpful AI assistant.\n"
            "You're a helpful assistant. When answering a user's question "
            """You should ONLY use a tool if it is directly relevant to answering the question. 
            Never repeat the same tool call more than once. 
            If the tool output is sufficient, call the final_answer tool immediately and stop. 
            If no tool is useful, skip tools and directly call final_answer. 
            Final answer tool must be called exactly once at the end."""
            "tool the tool output will be provided in the "
            "'scratchpad' below. If you have an answer in the "
            "scratchpad you should use final answer tool to answer the user. "
            "Final answer tool should be called at the end of the conversation only once."
            "use the context provided to answer the questions if possible.\n"
        )

    @staticmethod
    def few_shot_prompt() -> FewShotChatMessagePromptTemplate:
        examples = [
            {
                "input": "What is 2 + 3?",
                "output": "Use add_numbers tool to compute 2 + 3, then call the final answer tool with output."
            },
            {
                "input": "What is 10 * 5?",
                "output": "Use multiply_numbers tool to compute 10 * 5, then immediately call the final answer tool with output."
            },
            {
                "input": "tell me about langchain?",
                "output": "No relevant tools available for this question, so use final answer tool to answer the user."
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
        return HumanMessagePromptTemplate.from_template("{question}  \n Use the following for context {context}")

    @staticmethod
    def history_intro() -> SystemMessagePromptTemplate:
        return SystemMessagePromptTemplate.from_template("Below is the chat history:")

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
