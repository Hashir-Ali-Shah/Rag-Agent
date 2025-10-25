"use client";

export default function Sidebar({ chats = [], activeChatId, setActiveChatId, createNewChat }) {
  const activeChat = chats.find((c) => c.id === activeChatId);
  const isDisabled = activeChat && activeChat.messages.length === 0;

  return (
    <div className="w-64 h-screen flex flex-col bg-[#f7f7f8] border-r border-gray-200">
      {/* New Chat Button */}
      <div className="p-3 border-b border-gray-200">
        <button
          className={`w-full flex items-center gap-2 p-3 rounded-md text-black text-left border border-gray-300 transition-colors ${
            isDisabled 
              ? "bg-gray-200 cursor-not-allowed opacity-60" 
              : "bg-white hover:bg-gray-100"
          }`}
          onClick={createNewChat}
          disabled={isDisabled}
        >
          {/* Plus icon */}
          <svg
            className="w-4 h-4 text-black"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4"></path>
          </svg>
          New Chat
        </button>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-2">
        {chats.map((chat) => (
          <div
            key={chat.id}
            onClick={() => setActiveChatId(chat.id)}
            className={`p-3 text-black cursor-pointer rounded-md mb-2 truncate transition-colors ${
              chat.id === activeChatId 
                ? "bg-gray-300 font-semibold" 
                : "hover:bg-gray-100"
            }`}
          >
            {chat.title}
          </div>
        ))}
      </div>
    </div>
  );
}