"use client";

import { useState, useRef, useEffect } from "react";
import { PaperAirplaneIcon, DocumentDuplicateIcon, XMarkIcon } from "@heroicons/react/24/solid";

export default function Chat({ chat, updateMessages }) {
  const [input, setInput] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const messageListRef = useRef(null);
  const fileInputRef = useRef(null);

  // Send message and files via HTTP request
  const sendRequestHandler = async () => {
    if (!input.trim() && uploadedFiles.length === 0) return;

    setLoading(true);

    // Store the current input to clear it later
    const currentInput = input;

    // Add user message locally
    const userMsg = { id: Date.now(), type: "user", text: currentInput };
    const tempAiMsg = { id: Date.now() + 1, type: "assistant", text: "" };
    
    // Ensure we have a valid messages array before updating
    const currentMessages = Array.isArray(chat.messages) ? chat.messages : [];
    const newMessages = [...currentMessages, userMsg, tempAiMsg];
    updateMessages(chat.id, newMessages);

    // Prepare FormData for the request
    const formData = new FormData();
    formData.append("chat_id", chat.id);
    formData.append("message", currentInput);
    
    // Append files to FormData
    uploadedFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("https://rag-agent-3bps.onrender.com/chat", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Handle streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiResponse = "";
      let chunkCount = 0;

      console.log(`[${chat.id}] Starting to read stream...`);

      while (true) {
        const { done, value } = await reader.read();
        
        console.log(`[${chat.id}] Stream chunk ${++chunkCount}: done=${done}, value=${value}`);
        
        if (done) {
          console.log(`[${chat.id}] Stream completed after ${chunkCount} chunks`);
          break;
        }
        
        const chunk = decoder.decode(value, { stream: true });
        console.log(`[${chat.id}] Decoded chunk: "${chunk}"`);
        aiResponse += chunk;
        
        // Update the AI message with accumulated response
        updateMessages(chat.id, (currentMessages) => 
          currentMessages.map((msg, i, arr) => {
            if (i === arr.length - 1 && msg.type === "assistant") {
              return { ...msg, text: aiResponse };
            }
            return msg;
          })
        );
      }
      
      console.log(`[${chat.id}] Final response: "${aiResponse}"`);
    } catch (error) {
      console.error("Error sending message:", error);
      
      // Update the AI message with error
      updateMessages(chat.id, (currentMessages) => 
        currentMessages.map((msg, i, arr) => {
          if (i === arr.length - 1 && msg.type === "assistant") {
            return { ...msg, text: "Sorry, there was an error processing your request." };
          }
          return msg;
        })
      );
    } finally {
      setLoading(false);
      // Clear input and uploaded files
      setInput("");
      setUploadedFiles([]);
    }
  };

  // Handle Enter key
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendRequestHandler();
      setInput("");
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
    const files = Array.from(e.target.files).filter(Boolean);
    if (files.length === 0) return;
    setUploadedFiles((prev) => [...prev, ...files]);
    e.target.value = "";
  };

  // Remove uploaded file
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
      {/* Message list */}
      <div ref={messageListRef} className="flex-1 overflow-y-auto p-4 space-y-2 flex flex-col">
        {!chat.messages || chat.messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
           <div className="p-6 rounded-md bg-gray-100 text-black text-3xl font-semibold max-w-lg text-center">

              Welcome! How can I help you today?
            </div>
          </div>
        ) : (
          (chat.messages || []).map((msg) => (
            <div
              key={msg.id}
              className={`p-2 rounded-md max-w-[75%] break-words whitespace-pre-wrap overflow-wrap break-all ${
                msg.type === "user" ? "self-end bg-green-100 text-black" : "self-start bg-gray-100 text-black"
              }`}
            >
              {msg.text || (loading && msg.type === "assistant" ? <div className="w-60 h-10 bg-gray-400 rounded animate-pulse"></div>
 : "")}
            </div>
          ))
        )}
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2 p-2 mx-4 mb-1">
          {uploadedFiles.map((file, index) => (
            <div key={index} className="flex items-center gap-2 bg-gray-100 rounded-md px-2 py-1 text-gray-700">
              <span className="truncate max-w-[80%]">{file.name}</span>
              <button onClick={() => removeFile(index)} className="flex-shrink-0 p-1 rounded-full hover:bg-gray-300">
                <XMarkIcon className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input Bar */}
      <div className="p-4 border-t border-gray-200 flex items-end gap-2">
        <button onClick={() => fileInputRef.current.click()} className="flex-shrink-0 p-2 rounded-full bg-gray-200 hover:bg-gray-300">
          <DocumentDuplicateIcon className="h-5 w-5 text-gray-700" />
        </button>
        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" multiple />
        <textarea
          className="flex-1 p-2 rounded-md border border-gray-300 resize-none overflow-hidden max-h-32 break-words whitespace-pre-wrap"
          rows={1}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          disabled={loading}
        />
        <button disabled={loading} onClick={sendRequestHandler} className="flex-shrink-0 p-2 rounded-full bg-blue-500 hover:bg-blue-600 disabled:opacity-50">
          <PaperAirplaneIcon className="h-5 w-5 rotate-315" />
        </button>
      </div>
    </div>
  );
}