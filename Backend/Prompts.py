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
            "you should first use one of the tools provided. After using a "
            "tool the tool output will be provided in the "
            "'scratchpad' below. If you have an answer in the "
            "scratchpad you should use final answer tool to answer the user. "
            "Final answer tool should be called at the end of the conversation only once."
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
                "output": "Use multiply_numbers tool to compute 10 * 5, then call the final answer tool with output."
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
        return HumanMessagePromptTemplate.from_template("{question}")

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
