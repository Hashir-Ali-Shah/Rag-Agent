"use client";

import { useState, useRef, useEffect } from "react";
import { PaperAirplaneIcon, DocumentDuplicateIcon, XMarkIcon, MicrophoneIcon, StopIcon } from "@heroicons/react/24/solid";

export default function Chat({ chat, updateMessages }) {
  const [input, setInput] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);
  const messageListRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const wsRef = useRef(null);
  const silenceTimerRef = useRef(null);

  const startVoiceRecording = async () => {
    try {
      setIsRecording(true);
      setIsProcessingVoice(false);
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        
        if (audioChunksRef.current.length === 0) {
          console.error('No audio data recorded');
          setIsRecording(false);
          setIsProcessingVoice(false);
          return;
        }
        
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        console.log('Audio recorded, size:', audioBlob.size);
        
        setIsProcessingVoice(true);
        await sendVoiceToWebSocket(audioBlob);
      };
      
      mediaRecorderRef.current.start();
      console.log('Recording started');
      
      // Auto-stop after 2 seconds of silence detection
      // For simplicity, we'll just set a timer
      silenceTimerRef.current = setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          stopVoiceRecording();
        }
      }, 5000); // 5 seconds max recording
      
    } catch (error) {
      console.error('Error starting voice recording:', error);
      setIsRecording(false);
      setIsProcessingVoice(false);
    }
  };

  const stopVoiceRecording = () => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      console.log('Recording stopped');
    }
    
    setIsRecording(false);
  };

  const sendVoiceToWebSocket = async (audioBlob) => {
    return new Promise((resolve, reject) => {
      try {
        const ws = new WebSocket(`ws://127.0.0.1:8000/voice?chat_id=${chat.id}`);
        wsRef.current = ws;
        
        ws.onopen = async () => {
          console.log('WebSocket connected');
          
          // Send audio data as bytes
          const arrayBuffer = await audioBlob.arrayBuffer();
          ws.send(arrayBuffer);
          
          // Wait 2 seconds then send break signal
          setTimeout(() => {
            ws.send('BREAK');
            console.log('Break signal sent');
          }, 2000);
        };
        
        let aiResponse = "";
        
        ws.onmessage = (event) => {
          console.log('Received from WebSocket:', event.data);
          aiResponse += event.data;
          
          // Update messages in real-time
          updateMessages(chat.id, (currentMessages) => {
            const existingMessages = Array.isArray(currentMessages) ? currentMessages : [];
            
            // Check if we already have an assistant message being built
            if (existingMessages.length > 0 && existingMessages[existingMessages.length - 1].type === "assistant") {
              return existingMessages.map((msg, i, arr) => {
                if (i === arr.length - 1) {
                  return { ...msg, text: aiResponse };
                }
                return msg;
              });
            } else {
              // Create new assistant message
              return [...existingMessages, { id: Date.now(), type: "assistant", text: aiResponse }];
            }
          });
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsProcessingVoice(false);
          reject(error);
        };
        
        ws.onclose = () => {
          console.log('WebSocket closed');
          setIsProcessingVoice(false);
          wsRef.current = null;
          resolve();
        };
        
      } catch (error) {
        console.error('Error in WebSocket communication:', error);
        setIsProcessingVoice(false);
        reject(error);
      }
    });
  };

  const sendRequestHandler = async () => {
    if (!input.trim() && uploadedFiles.length === 0) return;

    setLoading(true);

    const currentInput = input;

    const userMsg = { id: Date.now(), type: "user", text: currentInput };
    const tempAiMsg = { id: Date.now() + 1, type: "assistant", text: "" };
    
    const currentMessages = Array.isArray(chat.messages) ? chat.messages : [];
    const newMessages = [...currentMessages, userMsg, tempAiMsg];
    updateMessages(chat.id, newMessages);

    const formData = new FormData();
    formData.append("chat_id", chat.id);
    formData.append("message", currentInput);
    
    uploadedFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

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
      
      const errorMessage = "Sorry, there was an error processing your request.";
      updateMessages(chat.id, (currentMessages) => 
        currentMessages.map((msg, i, arr) => {
          if (i === arr.length - 1 && msg.type === "assistant") {
            return { ...msg, text: errorMessage };
          }
          return msg;
        })
      );
    } finally {
      setLoading(false);
      setInput("");
      setUploadedFiles([]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendRequestHandler();
      setInput("");
    }
  };

  const handleInput = (e) => {
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 128) + "px";
    setInput(e.target.value);
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files).filter(Boolean);
    if (files.length === 0) return;
    setUploadedFiles((prev) => [...prev, ...files]);
    e.target.value = "";
  };

  const removeFile = (index) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [chat.messages]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
      }
    };
  }, []);

  return (
    <div className="flex-1 flex flex-col h-full bg-white">
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
              {msg.text || (loading && msg.type === "assistant" ? <div className="w-60 h-10 bg-gray-400 rounded animate-pulse"></div> : "")}
            </div>
          ))
        )}
      </div>

      {(isRecording || isProcessingVoice) && (
        <div className="mx-4 mb-2 p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-red-700 font-medium">
              {isRecording ? "Recording... Click stop when done" : "Processing voice..."}
            </span>
          </div>
        </div>
      )}

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

      <div className="p-4 border-t border-gray-200 flex items-end gap-2">
        <button onClick={() => fileInputRef.current.click()} className="flex-shrink-0 p-2 rounded-full bg-gray-200 hover:bg-gray-300">
          <DocumentDuplicateIcon className="h-5 w-5 text-gray-700" />
        </button>
        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" multiple />
        
        <button 
          onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
          disabled={loading || isProcessingVoice}
          className={`flex-shrink-0 p-2 rounded-full transition-colors ${
            isRecording 
              ? "bg-red-500 hover:bg-red-600" 
              : "bg-purple-500 hover:bg-purple-600"
          } disabled:opacity-50`}
        >
          {isRecording ? (
            <StopIcon className="h-5 w-5 text-white" />
          ) : (
            <MicrophoneIcon className="h-5 w-5 text-white" />
          )}
        </button>
        
        <textarea
          className="flex-1 p-2 rounded-md text-black border border-gray-300 resize-none overflow-hidden max-h-32 break-words whitespace-pre-wrap"
          rows={1}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={isRecording ? "Recording..." : isProcessingVoice ? "Processing..." : "Type a message or use voice..."}
          disabled={loading || isRecording || isProcessingVoice}
        />
        
        <button disabled={loading || isProcessingVoice} onClick={sendRequestHandler} className="flex-shrink-0 p-2 rounded-full bg-blue-500 hover:bg-blue-600 disabled:opacity-50">
          <PaperAirplaneIcon className="h-5 w-5 rotate-315 text-white" />
        </button>
      </div>
    </div>
  );
}