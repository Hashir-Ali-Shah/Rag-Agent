"use client";

import { useState, useRef, useEffect } from "react";
import { PaperAirplaneIcon, DocumentDuplicateIcon, XMarkIcon, MicrophoneIcon, StopIcon } from "@heroicons/react/24/solid";

export default function Chat({ chat, updateMessages }) {
  const [input, setInput] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);
  const [audioStream, setAudioStream] = useState(null);
  const messageListRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const speechSynthesisRef = useRef(null);
  const [usevoice, setUseVoice] = useState(false); 

  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'en-US';
      
      recognitionInstance.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        setInput(finalTranscript + interimTranscript);
      };
      
      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        setIsProcessingVoice(false);
      };
      
      recognitionInstance.onend = () => {
        setIsRecording(false);
        setIsProcessingVoice(false);
      };
      
      setRecognition(recognitionInstance);
    }

    return () => {
      if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startVoiceRecording = async () => {
    setUseVoice(true);
    try {
      setIsRecording(true);
      setIsProcessingVoice(true);
      
      if (recognition) {
        recognition.start();
      } else {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        setAudioStream(stream);
        
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];
        
        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };
        
        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          console.log('Audio recorded:', audioBlob);
          setIsProcessingVoice(false);
        };
        
        mediaRecorderRef.current.start();
      }
    } catch (error) {
      console.error('Error starting voice recording:', error);
      setIsRecording(false);
      setIsProcessingVoice(false);
    }
  };

  const stopVoiceRecording = () => {
    if (recognition) {
      recognition.stop();
    }
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    
    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop());
      setAudioStream(null);
    }
    
    setIsRecording(false);
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      
      const voices = window.speechSynthesis.getVoices();
      const preferredVoice = voices.find(voice => 
        voice.name.includes('Google') || 
        voice.name.includes('Microsoft') ||
        voice.lang.startsWith('en')
      );
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      
      speechSynthesisRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    }
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
          if (aiResponse.trim() && usevoice) {
            speakText(aiResponse);
          }
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
      
      speakText(errorMessage);
    } finally {
      setLoading(false);
      setInput("");
      setUploadedFiles([]);
      setUseVoice(false); 
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

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  };

  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [chat.messages]);

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
              {msg.text || (loading && msg.type === "assistant" ? <div className="w-60 h-10 bg-gray-400 rounded animate-pulse"></div>
 : "")}
            </div>
          ))
        )}
      </div>

      {isRecording && (
        <div className="mx-4 mb-2 p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-red-700 font-medium">
              {isProcessingVoice ? "Listening... Click stop when done" : "Recording..."}
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
          disabled={loading}
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
          placeholder={isRecording ? "Listening..." : "Type a message or use voice..."}
          disabled={loading || isRecording}
        />
        
        <button disabled={loading} onClick={sendRequestHandler} className="flex-shrink-0 p-2 rounded-full bg-blue-500 hover:bg-blue-600 disabled:opacity-50">
          <PaperAirplaneIcon className="h-5 w-5 rotate-315 text-white" />
        </button>
        
        <button 
          onClick={stopSpeaking}
          className="flex-shrink-0 p-2 rounded-full bg-orange-500 hover:bg-orange-600 text-white text-xs px-3"
          title="Stop speaking"
        >
          Stop
        </button>
      </div>
    </div>
  );
}