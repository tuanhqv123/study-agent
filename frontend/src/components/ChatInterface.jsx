import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";
import MessageItem from "./MessageItem";
import ChatInput from "./ChatInput";
import Settings from "./Settings";
import AgentSelector from "./AgentSelector";
import {
  X,
  Settings as SettingsIcon,
  Clock,
  Edit3,
  Plus,
  Paperclip,
} from "lucide-react";
// Import theme toggle
import { ThemeToggle } from "./ui/theme-toggle";
import { useTheme } from "./ui/theme-provider";
import { Tabs, TabsList, TabsTrigger } from "./ui/tabs";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "./ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";

const ChatInterface = () => {
  const navigate = useNavigate();
  const { theme } = useTheme();
  const isLight = theme === "light";
  const [user, setUser] = useState(null);
  const [chatSessions, setChatSessions] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [activeFileContexts, setActiveFileContexts] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const messagesEndRef = useRef(null);
  const [selectedTab, setSelectedTab] = useState("thread");
  const [spaceDialogOpen, setSpaceDialogOpen] = useState(false);
  const [spaceName, setSpaceName] = useState("");
  const [spaceDescription, setSpaceDescription] = useState("");
  const [spacePrompt, setSpacePrompt] = useState("");
  const [spaceError, setSpaceError] = useState("");
  // Spaces management
  const [spaces, setSpaces] = useState([]);
  const [activeSpace, setActiveSpace] = useState(null);
  // Edit space dialog
  const [editSpaceDialogOpen, setEditSpaceDialogOpen] = useState(false);
  const [editSpaceName, setEditSpaceName] = useState("");
  const [editSpaceDescription, setEditSpaceDescription] = useState("");
  const [editSpacePrompt, setEditSpacePrompt] = useState("");
  const [editSpaceId, setEditSpaceId] = useState(null);

  // Space file upload states
  const [isSpaceUploading, setIsSpaceUploading] = useState(false);
  const [spaceFiles, setSpaceFiles] = useState([]);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const checkAuth = async () => {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (user) {
        setUser(user);
        // Load user spaces
        await loadSpaces(user.id);
        // Load chat sessions
        const { data, error: sessionsError } = await supabase
          .from("chat_sessions")
          .select("*")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false });

        if (sessionsError) {
          console.error("Error loading chat sessions:", sessionsError);
          return;
        }

        setChatSessions(data || []);

        if (data?.length > 0) {
          // Load most recent chat
          setActiveChat(data[0].id);
          loadMessages(data[0].id);

          // Load agent preference if exists
          const { data: chatData } = await supabase
            .from("chat_sessions")
            .select("agent_id")
            .eq("id", data[0].id)
            .single();

          if (chatData && chatData.agent_id) {
            setSelectedAgent(chatData.agent_id);
          }
        } else {
          // Create a new chat session if user has none
          await createNewChatSession(user.id);
        }
      }
    };
    checkAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  const loadMessages = async (chatId) => {
    const { data } = await supabase
      .from("messages")
      .select("*")
      .eq("chat_id", chatId)
      .order("created_at", { ascending: true });

    // Debug sources
    if (data && data.length > 0) {
      console.log("Loaded messages from DB:", data.length);
      // Kiểm tra xem có message nào có sources không
      const messagesWithSources = data.filter(
        (msg) => msg.sources && msg.sources.length > 0
      );
      console.log("Messages with sources:", messagesWithSources.length);
      if (messagesWithSources.length > 0) {
        console.log("First message with sources:", messagesWithSources[0]);
      }
    }

    setMessages(data || []);

    // Load agent preference when switching chats
    const { data: chatData } = await supabase
      .from("chat_sessions")
      .select("agent_id")
      .eq("id", chatId)
      .single();

    if (chatData && chatData.agent_id) {
      setSelectedAgent(chatData.agent_id);
    } else {
      setSelectedAgent(null); // Reset to default if no agent is set
    }
  };

  // New function to create a chat session
  const createNewChatSession = async (userId, spaceId = null) => {
    const payload = { user_id: userId, agent_id: selectedAgent };
    if (spaceId) payload.space_id = spaceId;
    const { data, error } = await supabase
      .from("chat_sessions")
      .insert([payload])
      .select()
      .single();

    if (error) {
      console.error("Error creating new chat session:", error);
      return null;
    }

    setChatSessions((prev) => [data, ...prev]);
    setActiveChat(data.id);
    setMessages([]);
    return data;
  };

  // Enhanced function to handle chat session limit
  const handleNewChat = async () => {
    // Check if user has reached the limit of 10 chat sessions
    if (chatSessions.length >= 10) {
      // Find the oldest chat session
      const oldestSession = [...chatSessions].sort(
        (a, b) => new Date(a.created_at) - new Date(b.created_at)
      )[0];

      // Delete the oldest chat session
      await supabase.from("chat_sessions").delete().eq("id", oldestSession.id);

      // Also delete associated messages
      await supabase.from("messages").delete().eq("chat_id", oldestSession.id);

      // Remove from state
      setChatSessions((prev) =>
        prev.filter((session) => session.id !== oldestSession.id)
      );
    }

    // Create new chat session (for thread, not space)
    const spaceId = selectedTab === "space" ? activeSpace : null;
    await createNewChatSession(user.id, spaceId);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate("/login");
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle agent selection change
  const handleAgentChange = async (agentId) => {
    setSelectedAgent(agentId);

    // Save the selected agent to the current chat session
    if (activeChat) {
      try {
        await supabase
          .from("chat_sessions")
          .update({ agent_id: agentId })
          .eq("id", activeChat);

        // Add a system message indicating agent change
        const { data: agentData } = await fetch(
          "http://localhost:8000/agents"
        ).then((res) => res.json());
        const agents = agentData?.agents || [];
        const newAgent = agents.find((a) => a.id === agentId);

        if (newAgent) {
          setMessages((prev) => [
            ...prev,
            {
              role: "system",
              content: `Switched to ${newAgent.display_name} ${newAgent.avatar}. ${newAgent.description}`,
              chat_id: activeChat,
              created_at: new Date().toISOString(),
            },
          ]);
        }
      } catch (error) {
        console.error("Error updating agent for chat session:", error);
      }
    }
  };

  // Handle file upload success from ChatInput
  const handleFileUpload = (fileId, fileName) => {
    // Check if file already exists to prevent duplicates
    const existingFile = activeFileContexts.find((file) => file.id === fileId);
    if (!existingFile) {
      setActiveFileContexts((prev) => [
        ...prev,
        { id: fileId, name: fileName },
      ]);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: `Đã tải file "${fileName}" lên. Bạn có thể hỏi về nội dung.`,
        },
      ]);
    }
  };

  // Clear file context when user clicks remove
  const clearFileContext = async (fileId) => {
    if (!fileId) return;

    const fileToRemove = activeFileContexts.find((file) => file.id === fileId);
    if (!fileToRemove) return;

    try {
      await fetch(`http://localhost:8000/file/${fileId}?user_id=${user.id}`, {
        method: "DELETE",
      });
      setMessages((prev) => [
        ...prev,
        { role: "system", content: `Đã xóa file "${fileToRemove.name}".` },
      ]);
    } catch (e) {
      console.error("Error deleting file context:", e);
    }

    // Remove the file from activeFileContexts array
    setActiveFileContexts((prev) => prev.filter((file) => file.id !== fileId));
  };

  // Update sendMessage to include web_search_enabled
  const handleSendMessage = async (
    userMessage,
    webSearchEnabled,
    backendMessage
  ) => {
    if (!userMessage.trim() || isLoading) return;

    // Use backendMessage if provided, otherwise use userMessage
    const messageToSend = backendMessage || userMessage;

    // Create a new chat session in this space on first message
    let currentActiveChat = activeChat;
    if (selectedTab === "space" && !activeChat && activeSpace) {
      const newSession = await createNewChatSession(user.id, activeSpace);
      if (!newSession) {
        console.error("Failed to create new chat session");
        return;
      }
      // Set currentActiveChat to the new session
      currentActiveChat = newSession.id;
      setActiveChat(newSession.id);
    }

    // Name chat session with user's first message (for both thread and space)
    const isFirstMessage = messages.length === 0;
    if (isFirstMessage && currentActiveChat) {
      const sessionName = userMessage.trim(); // Use user message for name
      try {
        await supabase
          .from("chat_sessions")
          .update({ name: sessionName })
          .eq("id", currentActiveChat);
        setChatSessions((prev) =>
          prev.map((s) =>
            s.id === currentActiveChat ? { ...s, name: sessionName } : s
          )
        );
      } catch (err) {
        console.error("Error naming chat session:", err);
      }
    }

    // Ensure we have an active chat before proceeding
    if (!currentActiveChat) {
      console.error("No active chat session available");
      return;
    }

    setIsLoading(true);

    try {
      const newMessage = {
        role: "user",
        content: userMessage, // Display user message in UI
        chat_id: currentActiveChat,
        created_at: new Date().toISOString(),
      };

      // Add message to UI immediately (for display only)
      setMessages((prev) => [...prev, newMessage]);

      // Get university credentials
      const { data: credentials, error: credentialsError } = await supabase
        .from("university_credentials")
        .select(
          "university_username, university_password, access_token, refresh_token, token_expiry"
        )
        .eq("user_id", user?.id)
        .single();

      if (credentialsError && credentialsError.code !== "PGRST116") {
        console.error(
          "Error loading university credentials:",
          credentialsError
        );
      }

      // Prepare the request payload with user ID and credentials
      const payload = {
        stream: true,
        message: messageToSend, // Send original user message
        conversation_history: messages,
        user_id: user?.id || null,
        university_credentials: credentials || null,
        file_ids: activeFileContexts.map((file) => file.id), // Send array of file IDs
        agent_id: selectedAgent,
        web_search_enabled: webSearchEnabled || false,
        chat_id: currentActiveChat, // Thêm chat_id để backend có thể lưu tin nhắn
        space_id: selectedTab === "space" ? activeSpace : null, // Thêm space_id để backend lấy space prompt
      };

      console.log("Sending chat request with user ID:", user?.id);
      if (credentials) {
        console.log("University credentials found for user");
      } else {
        console.log("No university credentials found for user");
      }

      if (webSearchEnabled) {
        console.log("Web search is enabled for this request");
      }

      try {
        const response = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`);
        }

        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantContent = "";
        // Initialize assistant message in UI
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "",
            chat_id: currentActiveChat,
            created_at: new Date().toISOString(),
          },
        ]);
        let done = false;
        while (!done) {
          const { value, done: doneReading } = await reader.read();
          done = doneReading;
          if (value) {
            const chunk = decoder.decode(value);
            assistantContent += chunk;
            // Update last message content
            setMessages((prev) => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1] = {
                ...newMessages[newMessages.length - 1],
                content: assistantContent,
              };
              return newMessages;
            });
          }
        }

        // Reload messages from database to get updated messages with sources from backend
        setTimeout(async () => {
          try {
            const { data: updatedMessages } = await supabase
              .from("messages")
              .select("*")
              .eq("chat_id", currentActiveChat)
              .order("created_at", { ascending: true });

            if (updatedMessages) {
              setMessages(updatedMessages);
              console.log("Reloaded messages from database");
              if (webSearchEnabled) {
                console.log("Retrieved messages with web search sources");
              }
            }
          } catch (error) {
            console.error("Error reloading messages:", error);
          }
        }, 2000); // Wait 2 seconds for backend to save messages

        // No need to update chat session name here - we already named it with user message
      } catch (requestError) {
        console.error("Error communicating with backend:", requestError);

        // Show friendly error message in chat
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này. Vui lòng thử lại sau hoặc liên hệ hỗ trợ kỹ thuật.",
            chat_id: currentActiveChat,
            created_at: new Date().toISOString(),
          },
        ]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      // Show error in chat
      const errorMessage = {
        role: "assistant",
        content: "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
        chat_id: currentActiveChat,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Add function to delete a chat session
  const handleDeleteChat = async (sessionId, e) => {
    // Prevent click event from bubbling up to parent
    e.stopPropagation();

    // If this is the active chat, switch to another chat if available
    if (activeChat === sessionId) {
      const remainingSessions = chatSessions.filter((s) => s.id !== sessionId);
      if (remainingSessions.length > 0) {
        setActiveChat(remainingSessions[0].id);
        loadMessages(remainingSessions[0].id);
      } else {
        setActiveChat(null);
        setMessages([]);
      }
    }

    // Delete messages first (foreign key constraint)
    await supabase.from("messages").delete().eq("chat_id", sessionId);

    // Delete the session
    await supabase.from("chat_sessions").delete().eq("id", sessionId);

    // Update state to remove the deleted session
    setChatSessions((prev) =>
      prev.filter((session) => session.id !== sessionId)
    );
  };

  // Handle creation of a new space
  const handleCreateSpace = async (e) => {
    e.preventDefault();
    setSpaceError("");
    if (!spaceName.trim()) {
      setSpaceError("Space name is required.");
      return;
    }
    // Call API to create space
    try {
      const { data, error } = await supabase
        .from("spaces")
        .insert([
          {
            user_id: user.id,
            name: spaceName,
            description: spaceDescription,
            prompt: spacePrompt,
          },
        ])
        .select()
        .single();
      if (error) throw error;
      // Update spaces list and activeSpace
      setSpaces((prev) => [data, ...prev]);
      setActiveSpace(data.id);
      // Clear activeChat when switching to new space
      setActiveChat(null);
      // Clear form and close dialog
      setSpaceName("");
      setSpaceDescription("");
      setSpacePrompt("");
      setSpaceDialogOpen(false);
      setMessages([]);
    } catch (err) {
      console.error("Error creating space:", err);
      setSpaceError("Failed to create space.");
    }
  };

  // Load Spaces helper
  const loadSpaces = async (userId) => {
    const { data, error } = await supabase
      .from("spaces")
      .select("*")
      .eq("user_id", userId)
      .order("created_at", { ascending: false });
    if (error) console.error("Error loading spaces:", error);
    else setSpaces(data || []);
  };

  // Handle editing a space
  const handleEditSpace = (space) => {
    setEditSpaceId(space.id);
    setEditSpaceName(space.name);
    setEditSpaceDescription(space.description || "");
    setEditSpacePrompt(space.prompt || "");
    setEditSpaceDialogOpen(true);
  };

  // Handle updating a space
  const handleUpdateSpace = async (e) => {
    e.preventDefault();
    try {
      const { error } = await supabase
        .from("spaces")
        .update({
          name: editSpaceName,
          description: editSpaceDescription,
          prompt: editSpacePrompt,
        })
        .eq("id", editSpaceId);

      if (error) {
        console.error("Error updating space:", error);
        return;
      }

      // Refresh spaces
      await loadSpaces(user.id);
      setEditSpaceDialogOpen(false);

      // Reset form
      setEditSpaceId(null);
      setEditSpaceName("");
      setEditSpaceDescription("");
      setEditSpacePrompt("");
    } catch (error) {
      console.error("Error updating space:", error);
    }
  };

  // Handle space file upload (local files)
  const handleSpaceFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length || !activeSpace) return;

    // Validate each file
    for (const file of files) {
      const supportedTypes = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx
        "application/msword", // .doc
      ];

      if (!supportedTypes.includes(file.type)) {
        alert(`File "${file.name}": Chỉ hỗ trợ file PDF, DOC, DOCX`);
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        alert(`File "${file.name}": File quá lớn. Kích thước tối đa là 10MB`);
        return;
      }
    }

    setIsSpaceUploading(true);

    try {
      // Add all files to UI with uploading state first
      const tempFiles = files.map((file) => ({
        id: `temp-${Date.now()}-${file.name}`,
        filename: file.name,
        created_at: new Date().toISOString(),
        isUploading: true,
        originalFile: file,
      }));

      setSpaceFiles((prev) => [...prev, ...tempFiles]);

      // Upload files sequentially and update their status
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const tempFileId = tempFiles[i].id;

        try {
          const formData = new FormData();
          formData.append("file", file);
          formData.append("user_id", user.id);
          formData.append("space_id", activeSpace);

          const response = await fetch("http://localhost:8000/file/upload", {
            method: "POST",
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`Upload failed for ${file.name}`);
          }

          const data = await response.json();
          console.log(`Uploaded ${file.name} to space:`, data);

          // Remove temp file and add real file data
          setSpaceFiles((prev) => {
            const filtered = prev.filter((f) => f.id !== tempFileId);
            return [
              {
                id: data.file_id,
                filename: file.name,
                created_at: new Date().toISOString(),
                isUploading: false,
              },
              ...filtered,
            ];
          });
        } catch (fileError) {
          console.error(`Error uploading ${file.name}:`, fileError);
          // Remove failed temp file
          setSpaceFiles((prev) => prev.filter((f) => f.id !== tempFileId));
          alert(`Không thể tải lên file ${file.name}. Vui lòng thử lại.`);
        }
      }

      // Reset file input
      e.target.value = null;
    } catch (error) {
      console.error("Space file upload error:", error);
      alert("Không thể tải lên file. Vui lòng thử lại sau.");

      // Clean up temp files on error
      setSpaceFiles((prev) => prev.filter((f) => !f.isUploading));
    } finally {
      setIsSpaceUploading(false);
    }
  };

  // Load files for current space
  const loadSpaceFiles = async (spaceId) => {
    if (!spaceId) return;

    try {
      const { data, error } = await supabase
        .from("user_files")
        .select("id, filename, created_at")
        .eq("space_id", spaceId)
        .order("created_at", { ascending: false });

      if (error) {
        console.error("Error loading space files:", error);
        return;
      }

      setSpaceFiles(data || []);
    } catch (error) {
      console.error("Error loading space files:", error);
    }
  };

  // Handle Google Drive file selection for Space
  const handleGoogleDriveUpload = async () => {
    if (!activeSpace) return;

    try {
      // Dynamic import Google Drive service
      const { default: googleDriveService } = await import(
        "../services/googleDriveService.js"
      );

      setIsSpaceUploading(true);

      // Open Google Drive Picker
      const selectedFiles = await googleDriveService.openPicker();

      if (selectedFiles && selectedFiles.length > 0) {
        // Get file info for all files first and validate
        const validFiles = [];
        for (const pickedFile of selectedFiles) {
          try {
            const fileInfo = await googleDriveService.getFileInfo(
              pickedFile.id
            );

            const supportedTypes = [
              "application/pdf",
              "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              "application/msword",
            ];

            if (!supportedTypes.includes(fileInfo.mimeType)) {
              alert(`File "${fileInfo.name}": Chỉ hỗ trợ file PDF, DOC, DOCX`);
              continue;
            }

            if (fileInfo.size && parseInt(fileInfo.size) > 10 * 1024 * 1024) {
              alert(
                `File "${fileInfo.name}": File quá lớn. Kích thước tối đa là 10MB`
              );
              continue;
            }

            validFiles.push({ pickedFile, fileInfo });
          } catch (error) {
            console.error(
              `Error getting file info for ${pickedFile.name}:`,
              error
            );
            alert(`Không thể lấy thông tin file ${pickedFile.name}`);
          }
        }

        // Add all valid files to UI with uploading state
        const tempFiles = validFiles.map(({ fileInfo }) => ({
          id: `temp-gd-${Date.now()}-${fileInfo.name}`,
          filename: fileInfo.name,
          created_at: new Date().toISOString(),
          isUploading: true,
        }));

        setSpaceFiles((prev) => [...prev, ...tempFiles]);

        // Process each file
        for (let i = 0; i < validFiles.length; i++) {
          const { pickedFile, fileInfo } = validFiles[i];
          const tempFileId = tempFiles[i].id;

          try {
            // Download file from Google Drive
            const file = await googleDriveService.downloadFile(
              pickedFile.id,
              fileInfo.name
            );

            // Upload to our server with space_id
            const formData = new FormData();
            formData.append("file", file);
            formData.append("user_id", user.id);
            formData.append("space_id", activeSpace);

            const response = await fetch("http://localhost:8000/file/upload", {
              method: "POST",
              body: formData,
            });

            if (!response.ok) {
              throw new Error(`Upload failed for ${fileInfo.name}`);
            }

            const data = await response.json();
            console.log(
              `Uploaded ${fileInfo.name} to space from Google Drive:`,
              data
            );

            // Remove temp file and add real file data
            setSpaceFiles((prev) => {
              const filtered = prev.filter((f) => f.id !== tempFileId);
              return [
                {
                  id: data.file_id,
                  filename: fileInfo.name,
                  created_at: new Date().toISOString(),
                  isUploading: false,
                },
                ...filtered,
              ];
            });
          } catch (fileError) {
            console.error(`Error processing file ${fileInfo.name}:`, fileError);
            // Remove failed temp file
            setSpaceFiles((prev) => prev.filter((f) => f.id !== tempFileId));
            alert(`Không thể xử lý file ${fileInfo.name}. Vui lòng thử lại.`);
          }
        }
      }
    } catch (error) {
      console.error("Google Drive space upload error:", error);
      if (error.message.includes("popup_blocked_by_browser")) {
        alert("Trình duyệt đã chặn popup. Vui lòng cho phép popup và thử lại.");
      } else if (error.message.includes("access_denied")) {
        alert(
          "Bạn cần cấp quyền truy cập Google Drive để sử dụng tính năng này."
        );
      } else {
        alert("Không thể kết nối với Google Drive. Vui lòng thử lại sau.");
      }
    } finally {
      setIsSpaceUploading(false);
    }
  };

  // Handle delete space file
  const handleDeleteSpaceFile = async (fileId) => {
    try {
      const response = await fetch(
        `http://localhost:8000/file/${fileId}?user_id=${user.id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete file");
      }

      // Refresh space files
      await loadSpaceFiles(activeSpace);

      // Show success message
      setMessages((prev) => [
        ...prev,
        { role: "system", content: "Đã xóa file khỏi Space." },
      ]);
    } catch (error) {
      console.error("Error deleting space file:", error);
      alert("Không thể xóa file. Vui lòng thử lại sau.");
    }
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar - fixed height, no scrolling */}
      <div className="w-64 bg-card border-r border-border flex flex-col h-screen overflow-hidden">
        <div className="flex-1 flex flex-col">
          {/* Logo */}
          <div className="flex justify-center items-center mt-6 mb-2">
            <h1 className="font-['Montserrat',sans-serif] font-semibold text-foreground text-2xl tracking-wide">
              <em>&#8220;forPTITer&#8221;</em>
            </h1>
          </div>
          {/* Chat Sessions or Spaces */}
          {selectedTab === "thread" && (
            <>
              <button
                onClick={handleNewChat}
                className="mx-4 mb-2 w-auto p-2 bg-secondary rounded-lg text-foreground hover:bg-accent border border-border"
              >
                + New Chat
              </button>
              <div className="overflow-y-auto flex-1 px-4 mt-4">
                {chatSessions
                  .filter((session) => !session.space_id)
                  .map((session) => (
                    <div
                      key={session.id}
                      className={`p-3 hover:bg-secondary cursor-pointer relative group mb-2 rounded-lg ${
                        activeChat === session.id ? "bg-accent" : ""
                      }`}
                      onClick={() => {
                        setActiveChat(session.id);
                        loadMessages(session.id);
                      }}
                    >
                      <div className="pr-7">
                        <p className="text-sm text-foreground truncate font-medium">
                          {session.name || "New Chat"}
                        </p>
                      </div>
                      <button
                        onClick={(e) => handleDeleteChat(session.id, e)}
                        className="absolute top-1/2 right-2 -translate-y-1/2 text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 transition-opacity"
                        aria-label="Delete chat"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
              </div>
            </>
          )}
          {selectedTab === "space" && (
            <>
              <Dialog open={spaceDialogOpen} onOpenChange={setSpaceDialogOpen}>
                <DialogTrigger asChild>
                  <button className="mx-4 mb-2 w-auto p-2 bg-secondary rounded-lg text-foreground hover:bg-accent border border-border">
                    + New Space
                  </button>
                </DialogTrigger>
                <DialogContent>
                  <form onSubmit={handleCreateSpace} className="space-y-4">
                    <DialogHeader>
                      <DialogTitle>Create a Space</DialogTitle>
                      <DialogDescription>
                        Organize your chats and knowledge by topic, project, or
                        course.
                      </DialogDescription>
                    </DialogHeader>
                    <div>
                      <label className="block text-sm font-medium text-white mb-1">
                        Title
                      </label>
                      <input
                        type="text"
                        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-0"
                        placeholder="Team Space..."
                        value={spaceName}
                        onChange={(e) => setSpaceName(e.target.value)}
                        required
                        maxLength={100}
                      />
                    </div>
                    <div>
                      <label
                        className={`block text-sm font-medium ${
                          isLight ? "text-gray-700" : "text-white"
                        } mb-1`}
                      >
                        Description{" "}
                        <span className="text-xs text-muted-foreground">
                          (optional)
                        </span>
                      </label>
                      <Textarea
                        placeholder="A collaborative space for discussing latest insights..."
                        value={spaceDescription}
                        onChange={(e) => setSpaceDescription(e.target.value)}
                        maxLength={300}
                      />
                    </div>
                    <div>
                      <label
                        className={`block text-sm font-medium ${
                          isLight ? "text-gray-700" : "text-white"
                        } mb-1`}
                      >
                        Custom Instructions{" "}
                        <span className="text-xs text-muted-foreground">
                          (optional)
                        </span>
                      </label>
                      <Textarea
                        placeholder="Always respond in a formal tone and prioritize data-driven insights..."
                        value={spacePrompt}
                        onChange={(e) => setSpacePrompt(e.target.value)}
                        maxLength={1000}
                      />
                    </div>
                    {spaceError && (
                      <div className="text-red-500 text-sm">{spaceError}</div>
                    )}
                    <DialogFooter>
                      <DialogClose asChild>
                        <Button type="button" variant="secondary">
                          Cancel
                        </Button>
                      </DialogClose>
                      <Button type="submit" variant="default">
                        Continue
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>

              {/* Edit Space Dialog */}
              <Dialog
                open={editSpaceDialogOpen}
                onOpenChange={setEditSpaceDialogOpen}
              >
                <DialogContent>
                  <form onSubmit={handleUpdateSpace} className="space-y-4">
                    <DialogHeader>
                      <DialogTitle>Edit Space</DialogTitle>
                      <DialogDescription>
                        Update your space information and settings.
                      </DialogDescription>
                    </DialogHeader>
                    <div>
                      <label
                        className={`block text-sm font-medium ${
                          isLight ? "text-gray-700" : "text-white"
                        } mb-1`}
                      >
                        Title
                      </label>
                      <input
                        type="text"
                        className={`w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 ${
                          isLight
                            ? "bg-gray-100 border-gray-300 text-gray-800 placeholder-gray-400 focus:ring-blue-200"
                            : "bg-white/5 border-white/10 text-white placeholder-white/30 focus:ring-white/20"
                        }`}
                        placeholder="Team Space..."
                        value={editSpaceName}
                        onChange={(e) => setEditSpaceName(e.target.value)}
                        required
                        maxLength={100}
                      />
                    </div>
                    <div>
                      <label
                        className={`block text-sm font-medium ${
                          isLight ? "text-gray-700" : "text-white"
                        } mb-1`}
                      >
                        Description{" "}
                        <span className="text-xs text-muted-foreground">
                          (optional)
                        </span>
                      </label>
                      <Textarea
                        placeholder="A collaborative space for discussing latest insights..."
                        value={editSpaceDescription}
                        onChange={(e) =>
                          setEditSpaceDescription(e.target.value)
                        }
                        maxLength={300}
                      />
                    </div>
                    <div>
                      <label
                        className={`block text-sm font-medium ${
                          isLight ? "text-gray-700" : "text-white"
                        } mb-1`}
                      >
                        Custom Instructions{" "}
                        <span className="text-xs text-muted-foreground">
                          (optional)
                        </span>
                      </label>
                      <Textarea
                        placeholder="Always respond in a formal tone and prioritize data-driven insights..."
                        value={editSpacePrompt}
                        onChange={(e) => setEditSpacePrompt(e.target.value)}
                        maxLength={1000}
                      />
                    </div>
                    <DialogFooter>
                      <DialogClose asChild>
                        <Button type="button" variant="secondary">
                          Cancel
                        </Button>
                      </DialogClose>
                      <Button type="submit" variant="default">
                        Save Changes
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
              <div className="overflow-y-auto flex-1 px-4 mt-4">
                {spaces.map((space) => (
                  <div
                    key={space.id}
                    className={`p-3 hover:bg-secondary cursor-pointer relative group mb-2 rounded-lg ${
                      activeSpace === space.id ? "bg-accent" : ""
                    }`}
                    onClick={() => {
                      setActiveSpace(space.id);
                      setActiveChat(null);
                      setMessages([]);
                      loadSpaceFiles(space.id); // Load files when selecting space
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        <p className="text-sm text-foreground truncate font-medium">
                          {space.name}
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditSpace(space);
                        }}
                        className="text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                        aria-label="Edit space"
                      >
                        <Edit3 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
        {/* Toggle Thread / Space */}
        <div className="flex justify-center px-4 py-2">
          <Tabs
            value={selectedTab}
            onValueChange={(newTab) => {
              setSelectedTab(newTab);
              // Reset activeChat when switching between thread and space
              if (newTab === "space") {
                setActiveChat(null);
                setMessages([]);
              } else if (newTab === "thread") {
                // Load the most recent thread chat if available
                const threadSessions = chatSessions.filter((s) => !s.space_id);
                if (threadSessions.length > 0) {
                  setActiveChat(threadSessions[0].id);
                  loadMessages(threadSessions[0].id);
                } else {
                  setActiveChat(null);
                  setMessages([]);
                }
              }
            }}
          >
            <TabsList className="flex flex-row space-x-2 w-full">
              <TabsTrigger
                value="thread"
                className="flex-1 bg-secondary rounded-lg text-foreground hover:bg-accent"
              >
                Thread
              </TabsTrigger>
              <TabsTrigger
                value="space"
                className="flex-1 bg-secondary rounded-lg text-foreground hover:bg-accent"
              >
                Space
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        {user && (
          <div className="p-4 border-t border-border mt-auto">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground truncate">
                {user.email}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="w-full p-2 bg-red-500/10 text-red-500 rounded-lg hover:bg-red-500/20"
            >
              Log Out
            </button>
          </div>
        )}
      </div>
      {/* Add Settings modal */}
      {user && (
        <Settings
          isOpen={settingsOpen}
          onClose={() => setSettingsOpen(false)}
          userId={user.id}
        />
      )}
      {/* Chat Area - scrollable area with fixed position */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Sticky header */}
        <div className="sticky top-0 bg-card/90 backdrop-blur-sm border-b border-border z-10 shadow-sm">
          <div className="flex items-center justify-between px-8 py-3">
            <div className="flex items-center gap-3">
              <div className="w-50">
                <AgentSelector
                  selectedAgent={selectedAgent}
                  onAgentChange={handleAgentChange}
                />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center space-x-4">
                <ThemeToggle />
                <button
                  onClick={() => setSettingsOpen(true)}
                  className="p-1.5 rounded-full bg-secondary hover:bg-accent transition-colors"
                  aria-label="Settings"
                >
                  <SettingsIcon className="h-4 w-4 text-muted-foreground" />
                </button>
              </div>
            </div>
          </div>
        </div>
        <div
          className={`flex-1 overflow-y-auto ${
            activeFileContexts?.length > 0 ? "pb-56" : "pb-40"
          }`}
        >
          <div className="mx-auto p-4 pt-8">
            {selectedTab === "space" && !activeChat && (
              <div className="w-full flex justify-center">
                <div className="w-1/2 mt-8">
                  <div className="flex items-center justify-between mb-4">
                    <h1 className="text-4xl font-bold text-foreground">
                      {spaces.find((s) => s.id === activeSpace)?.name}
                    </h1>
                    {activeSpace && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <button
                            className={`p-2 rounded-lg border-2 border-dashed transition-colors ${
                              isLight
                                ? "border-gray-300 hover:border-blue-400 hover:bg-blue-50"
                                : "border-gray-600 hover:border-blue-400 hover:bg-blue-900/20"
                            }`}
                            disabled={isSpaceUploading}
                          >
                            <Plus className="h-5 w-5" />
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => fileInputRef.current?.click()}
                            disabled={isSpaceUploading}
                          >
                            <Paperclip className="mr-2 h-4 w-4" />
                            Upload từ máy tính
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={handleGoogleDriveUpload}
                            disabled={isSpaceUploading}
                          >
                            <svg
                              className="mr-2 h-4 w-4"
                              viewBox="0 0 24 24"
                              fill="currentColor"
                            >
                              <path d="M6.28 3L3 8.07V12h6.07l2.5-4.35L8.84 3H6.28zM4.11 14H0l2.07 3.68L4.11 14zM8.84 3L12 8.07V12h6.07l2.5-4.35L17.84 3H8.84z" />
                            </svg>
                            Chọn từ Google Drive
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
                  </div>
                  <p className="text-base text-muted-foreground mb-6">
                    {spaces.find((s) => s.id === activeSpace)?.description}
                  </p>

                  {/* Hidden file input for space uploads */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx"
                    onChange={handleSpaceFileUpload}
                    className="hidden"
                  />

                  {/* Display space files */}
                  {spaceFiles.length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold text-foreground mb-3">
                        Files trong Space ({spaceFiles.length})
                      </h3>
                      <div className="space-y-2">
                        {spaceFiles.map((file) => (
                          <div
                            key={file.id}
                            className={`flex items-center justify-between p-3 rounded-lg border ${
                              isLight
                                ? "bg-gray-50 border-gray-200"
                                : "bg-gray-800 border-gray-700"
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <Paperclip className="h-4 w-4 text-muted-foreground" />
                              <div className="flex-1 max-w-[400px]">
                                <p className="text-sm font-medium text-foreground truncate">
                                  {file.filename}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {new Date(file.created_at).toLocaleDateString(
                                    "vi-VN"
                                  )}
                                </p>
                              </div>
                            </div>
                            {file.isUploading ? (
                              <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full" />
                            ) : (
                              <button
                                onClick={() => handleDeleteSpaceFile(file.id)}
                                className="text-red-500 hover:text-red-700 p-1 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                                aria-label="Xóa file"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="space-y-3">
                    {chatSessions.filter((s) => s.space_id === activeSpace)
                      .length > 0 ? (
                      chatSessions
                        .filter((s) => s.space_id === activeSpace)
                        .map((session) => (
                          <div
                            key={session.id}
                            onClick={() => {
                              setActiveChat(session.id);
                              loadMessages(session.id);
                            }}
                            className="w-full border-b border-border pb-4 cursor-pointer hover:bg-accent/30 transition-colors rounded-t-lg p-3"
                          >
                            <div className="space-y-2">
                              <p className="text-foreground font-medium leading-relaxed">
                                {session.name || "New Chat"}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {new Date(
                                  session.created_at
                                ).toLocaleDateString("vi-VN", {
                                  day: "2-digit",
                                  month: "2-digit",
                                  year: "numeric",
                                  hour: "2-digit",
                                  minute: "2-digit",
                                })}
                              </p>
                            </div>
                          </div>
                        ))
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        No sessions yet. Send a message to start.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
            {(selectedTab === "thread" ||
              (selectedTab === "space" && activeChat)) && (
              <div className="mt-8">
                {messages.map((message, index) => (
                  <MessageItem key={index} message={message} />
                ))}
                {isLoading && (
                  <div className="flex items-center gap-2 p-4">
                    <div className="flex space-x-1">
                      <div className="h-2 w-2 animate-bounce rounded-full bg-muted" />
                      <div
                        className="h-2 w-2 animate-bounce rounded-full bg-muted"
                        style={{ animationDelay: "150ms" }}
                      />
                      <div
                        className="h-2 w-2 animate-bounce rounded-full bg-muted"
                        style={{ animationDelay: "300ms" }}
                      />
                    </div>
                    <span className="text-sm text-muted-foreground">
                      Study Assistant AI đang trả lời...
                    </span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>
        {(selectedTab === "thread" || selectedTab === "space") && (
          <div className="absolute bottom-0 left-64 right-0 bg-background">
            <div className="mx-auto max-w-2xl px-4 pb-4">
              <ChatInput
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
                onFileUpload={handleFileUpload}
                userId={user?.id}
                activeFileContexts={activeFileContexts}
                clearFileContext={clearFileContext}
                selectedAgent={selectedAgent}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
