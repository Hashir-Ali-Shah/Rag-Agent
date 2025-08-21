"use client";

import { useState, useRef, useEffect } from "react";
import { PaperAirplaneIcon, DocumentDuplicateIcon, XMarkIcon } from "@heroicons/react/24/solid";

export default function Chat({ chat, updateMessages }) {
  const [input, setInput] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const messageListRef = useRef(null);
  const fileInputRef = useRef(null);

  // Send message handler
  const sendMessage = () => {
    if (!input.trim() && uploadedFiles.length === 0) return;

    if (input.trim()) {
      const userMsg = { id: Date.now(), type: "user", text: input };
      const aiMsg = {
        id: Date.now() + 1,
        type: "assistant",
        text: "This is a sample response.",
      };
      updateMessages(chat.id, [...chat.messages, userMsg, aiMsg]);
    }

    // Clear input and uploaded files
    setInput("");
    setUploadedFiles([]);
  };

  // Handle Enter key
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Auto-resize textarea
  const handleInput = (e) => {
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 128) + "px";
    setInput(e.target.value);
  };

  // Handle file selection
const handleFileChange = (e) => {
  const files = Array.from(e.target.files).filter(Boolean); // ignore undefined
  if (files.length === 0) return;
  setUploadedFiles((prev) => [...prev, ...files]);
  e.target.value = ""; // reset input
};

  // Remove a specific uploaded file
  const removeFile = (index) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // Scroll to bottom on new messages
  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [chat.messages]);

  return (
    <div className="flex-1 flex flex-col h-full bg-white">
      {/* Message List */}
      <div
        ref={messageListRef}
        className="flex-1 overflow-y-auto overflow-x-hidden p-4 space-y-2 flex flex-col"
      >
          {chat.messages.length === 0 ? (
<div className="flex-1 flex items-center justify-center">
  <div className="p-6 rounded-md bg-gray-100 text-black text-lg font-semibold max-w-lg text-center">
     Welcome! How can i help you today?
  </div>
</div>
  ):
        (chat.messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-2 rounded-md max-w-[75%] break-words whitespace-pre-wrap overflow-wrap break-all ${
              msg.type === "user"
                ? "self-end bg-green-100 text-black"
                : "self-start bg-gray-100 text-black"
            }`}
          >
            {msg.text}
          </div>
        )))}

      </div>
    
      {/* Uploaded Files Badges */}
      {uploadedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2 p-2 mx-4 mb-1">
          {uploadedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-2 bg-gray-100 rounded-md px-2 py-1 text-gray-700"
            >
              <span className="truncate max-w-[80%]">{file.name}</span>
              <button
                onClick={() => removeFile(index)}
                className="flex-shrink-0 p-1 rounded-full hover:bg-gray-300"
              >
                <XMarkIcon className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input Bar */}
      <div className="p-4 border-t border-gray-200 flex items-end gap-2">
        {/* Upload Button */}
        <button
          onClick={() => fileInputRef.current.click()}
          className="flex-shrink-0 p-2 rounded-full bg-gray-200 hover:bg-gray-300"
        >
          <DocumentDuplicateIcon className="h-5 w-5 text-gray-700" />
        </button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Textarea */}
        <textarea
          className="flex-1 p-2 rounded-md border border-gray-300 resize-none overflow-hidden max-h-32 break-words whitespace-pre-wrap"
          rows={1}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
        />

        {/* Send Button */}
        <button
          onClick={sendMessage}
          className="flex-shrink-0 p-2 rounded-full bg-blue-500 hover:bg-blue-600"
        >
          <PaperAirplaneIcon className="h-5 w-5 rotate-315" />
        </button>
      </div>
    </div>
  );
}
