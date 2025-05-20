import { useState, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Paperclip, Globe, Sparkle, ArrowUp } from "lucide-react";
import { useTheme } from "./ui/theme-provider";

const ChatInput = ({
  onSendMessage,
  isLoading,
  onFileUpload,
  userId,
  selectedAgent,
}) => {
  const [message, setMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [thinking, setThinking] = useState(true);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const { theme } = useTheme();
  const isLight = theme === "light";

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      const newHeight = Math.min(textarea.scrollHeight, 200);
      textarea.style.height = `${newHeight}px`;
    }
  }, [message]);

  const isQwenModel = selectedAgent && selectedAgent.startsWith("qwen");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;
    let finalMessage = message.trim();
    // Nếu bật web search thì không bao giờ thêm /no_thinking
    if (!webSearchEnabled && isQwenModel && !thinking) {
      finalMessage = finalMessage + " /no_thinking";
    }
    onSendMessage(finalMessage, webSearchEnabled);
    setMessage("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const toggleWebSearch = () => {
    setWebSearchEnabled(!webSearchEnabled);
  };

  const toggleThinking = () => {
    setThinking((prev) => !prev);
  };

  const handleFileButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type (PDF only)
    if (file.type !== "application/pdf") {
      alert("Chỉ hỗ trợ tải lên file PDF");
      return;
    }

    // Maximum file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert("File quá lớn. Kích thước tối đa là 10MB");
      return;
    }

    setIsUploading(true);

    try {
      // Create form data
      const formData = new FormData();
      formData.append("file", file);

      // Sử dụng userId từ props thay vì từ localStorage
      if (userId) {
        formData.append("user_id", userId);
        console.log("Uploading file with user ID:", userId);
      } else {
        console.error("Missing user ID for file upload");
        alert("Không thể tải lên file: Thiếu thông tin người dùng");
        setIsUploading(false);
        return;
      }

      // Send file to backend
      const response = await fetch("http://localhost:8000/file/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      // Call the onFileUpload callback with file ID and name
      if (onFileUpload && data.file_id) {
        onFileUpload(data.file_id, file.name);
      }

      // Reset file input
      e.target.value = null;
    } catch (error) {
      console.error("File upload error:", error);
      alert("Không thể tải lên file. Vui lòng thử lại sau.");
    } finally {
      setIsUploading(false);
    }
  };

  // Style chung cho các nút icon
  const iconBtnStyle = `h-10 w-10 flex-shrink-0 rounded-full border-none bg-transparent text-gray-500 dark:text-[#d1cfc0]/70 hover:bg-gray-200 dark:hover:bg-[#333333] flex items-center justify-center`;
  const activeBtnStyle = isLight
    ? "bg-blue-100 text-blue-700 hover:bg-blue-200"
    : "bg-[#2a2a2a] text-blue-400 hover:bg-[#333333]";
  const thinkingActiveStyle = isLight
    ? "bg-blue-100 text-blue-700 hover:bg-blue-200"
    : "bg-[#2a2a2a] text-blue-400 hover:bg-[#333333]";

  return (
    <div
      className={`bg-gray-100 dark:bg-[#232323] py-2 px-0 rounded-2xl`}
      style={{ borderTop: "none" }}
    >
      <div className="w-full">
        <form
          onSubmit={handleSubmit}
          className={`relative flex flex-col w-full rounded-2xl bg-gray-100 dark:bg-[#232323] p-3`}
          style={{ border: "none", boxShadow: "none" }}
        >
          {/* Textarea nhập tin nhắn */}
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhắn tin với Study Assistant AI..."
            className={`flex-1 min-h-[40px] max-h-[200px] resize-none border-0 bg-transparent p-2 rounded-xl ${
              isLight
                ? "text-gray-800 placeholder-gray-400"
                : "text-[#d1cfc0] placeholder-[#d1cfc0]/50"
            } focus:outline-none focus-visible:ring-0 focus:ring-0 focus-within:ring-0`}
            disabled={isLoading || isUploading}
            rows={1}
            style={{ background: "transparent" }}
          />

          {/* Hàng nút chức năng dưới Textarea */}
          <div className="flex items-center justify-between mt-2 w-full">
            <div className="flex gap-2">
              {/* Nút upload file */}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
                disabled={isLoading || isUploading}
              />
              <Button
                type="button"
                onClick={handleFileButtonClick}
                size="icon"
                className={iconBtnStyle}
                disabled={isLoading || isUploading}
                title="Đính kèm file PDF"
              >
                <Paperclip className="h-5 w-5" strokeWidth={2.5} />
                <span className="sr-only">Đính kèm file</span>
              </Button>

              {/* Nút Thinking (nếu là Qwen) */}
              {isQwenModel && (
                <Button
                  type="button"
                  onClick={toggleThinking}
                  size="icon"
                  className={
                    iconBtnStyle + " " + (thinking ? thinkingActiveStyle : "")
                  }
                  disabled={isLoading || isUploading}
                  title={
                    thinking
                      ? "Đang bật chế độ Thinking"
                      : "Đang tắt chế độ Thinking"
                  }
                >
                  <Sparkle className="h-5 w-5" strokeWidth={2.5} />
                  <span className="sr-only">Thinking</span>
                </Button>
              )}

              {/* Nút Search */}
              <Button
                type="button"
                onClick={toggleWebSearch}
                size="icon"
                className={
                  iconBtnStyle + (webSearchEnabled ? " " + activeBtnStyle : "")
                }
                disabled={isLoading || isUploading}
                title={
                  webSearchEnabled ? "Tắt tìm kiếm web" : "Bật tìm kiếm web"
                }
              >
                <Globe className="h-5 w-5" strokeWidth={2.5} />
                <span className="sr-only">Tìm kiếm web</span>
              </Button>
            </div>
            {/* Nút gửi tin nhắn ở bên phải */}
            <Button
              type="submit"
              disabled={!message.trim() || isLoading || isUploading}
              size="icon"
              className={`h-10 w-10 flex-shrink-0 rounded-full ml-2 ${
                isLight
                  ? "bg-blue-600 text-white hover:bg-blue-700 border border-blue-700"
                  : "bg-[#2a2a2a] text-[#d1cfc0] hover:bg-[#333333] border border-[#d1cfc0]/10"
              }`}
            >
              <ArrowUp className="h-6 w-6" strokeWidth={2.5} />
              <span className="sr-only">Gửi</span>
            </Button>
          </div>

          {/* Upload status indicator */}
          {isUploading && (
            <div
              className={`absolute -top-10 left-0 right-0 flex items-center justify-center p-2 rounded-md text-sm ${
                isLight
                  ? "bg-blue-50 text-blue-700"
                  : "bg-[#2a2a2a] text-[#d1cfc0]/70"
              }`}
            >
              <div
                className={`h-2 w-2 animate-pulse rounded-full mr-2 ${
                  isLight ? "bg-blue-600" : "bg-blue-400"
                }`}
              ></div>
              Đang tải lên file...
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default ChatInput;
