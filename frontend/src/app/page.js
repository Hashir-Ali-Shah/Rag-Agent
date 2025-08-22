"use client";

import { useState } from "react";
import Sidebar from "./components/Sidebar/Sidebar";
import Chat from "./components/ChatWindow/Chat";

export default function Page() {
  const [chats, setChats] = useState([
    { id: 1, title: "New Chat", messages: [] },
  ]);
  const [activeChatId, setActiveChatId] = useState(1);

  const createNewChat = () => {
    const newChat = { id: Date.now(), title: "New Chat", messages: [] };
    setChats([newChat, ...chats]);
    setActiveChatId(newChat.id);
  };

  const updateMessages = (chatId, messagesOrUpdater) => {
    setChats((prev) =>
      prev.map((c) => {
        if (c.id === chatId) {
          const newMessages =
            typeof messagesOrUpdater === "function"
              ? messagesOrUpdater(c.messages)
              : messagesOrUpdater;
          return { ...c, messages: newMessages };
        }
        return c;
      })
    );
  };

  const activeChat = chats?.find((c) => c.id === activeChatId);

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        setActiveChatId={setActiveChatId}
        createNewChat={createNewChat}
      />

      {/* Active Chat */}
      <div className="flex-1 flex flex-col">
        {activeChat && (
          <Chat chat={activeChat} updateMessages={updateMessages} />
        )}
      </div>
    </div>
  );
}
