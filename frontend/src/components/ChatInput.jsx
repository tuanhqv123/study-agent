import { useState, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Paperclip, Globe, Sparkle, ArrowUp, X } from "lucide-react";
import { useTheme } from "./ui/theme-provider";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";

const ChatInput = ({
  onSendMessage,
  isLoading,
  onFileUpload,
  userId,
  selectedAgent,
  activeFileContexts,
  clearFileContext,
}) => {
  const [message, setMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [thinking, setThinking] = useState(false);
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
    let userMessage = message.trim(); // Message hiển thị cho user
    let backendMessage = userMessage; // Message gửi cho backend

    // Nếu bật web search thì không bao giờ thêm /no_thinking
    if (!webSearchEnabled && isQwenModel && !thinking) {
      backendMessage = userMessage + " /no_thinking";
    }

    onSendMessage(userMessage, webSearchEnabled, backendMessage);
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
    const files = Array.from(e.target.files); // Support multiple files
    if (!files.length) return;

    // Validate each file
    for (const file of files) {
      // Validate file type (PDF only)
      const supportedTypes = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx
        "application/msword", // .doc
      ];

      if (!supportedTypes.includes(file.type)) {
        alert(`File "${file.name}": Chỉ hỗ trợ file PDF, DOC, DOCX`);
        return;
      }

      // Maximum file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert(`File "${file.name}": File quá lớn. Kích thước tối đa là 10MB`);
        return;
      }
    }

    setIsUploading(true);
    setUploadStatus(`Đang upload ${files.length} file(s)...`);

    try {
      // Upload files sequentially to avoid overwhelming the server
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setUploadStatus(
          `Đang upload file ${i + 1}/${files.length}: ${file.name}`
        );
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
          throw new Error(`Upload failed for ${file.name}`);
        }

        const data = await response.json();

        // Call the onFileUpload callback with file ID and name
        if (onFileUpload && data.file_id) {
          onFileUpload(data.file_id, file.name);
        }

        // Don't show success message, file context will be added to UI
      }

      // Reset file input
      e.target.value = null;
    } catch (error) {
      console.error("File upload error:", error);
      setUploadStatus(`❌ Lỗi upload: ${error.message}`);
      alert("Không thể tải lên file. Vui lòng thử lại sau.");
    } finally {
      setTimeout(() => {
        setIsUploading(false);
        setUploadStatus("");
      }, 2000);
    }
  };

  const handleGoogleDriveClick = async () => {
    try {
      console.log("Starting Google Drive file selection...");

      // Dynamic import Google Drive service
      const { default: googleDriveService } = await import(
        "../services/googleDriveService.js"
      );

      console.log("Google Drive service imported successfully");

      setIsUploading(true);
      setUploadStatus("Đang mở Google Drive Picker...");

      // Open Google Drive Picker
      const selectedFiles = await googleDriveService.openPicker();

      if (selectedFiles && selectedFiles.length > 0) {
        setUploadStatus(`Đang xử lý ${selectedFiles.length} file(s)...`);

        for (let i = 0; i < selectedFiles.length; i++) {
          const pickedFile = selectedFiles[i];
          try {
            setUploadStatus(
              `Đang xử lý file ${i + 1}/${selectedFiles.length}: ${
                pickedFile.name
              }`
            );

            // Get file info
            const fileInfo = await googleDriveService.getFileInfo(
              pickedFile.id
            );

            // Check if it's a supported file type
            const supportedTypes = [
              "application/pdf",
              "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx
              "application/msword", // .doc
              "application/vnd.google-apps.document", // Google Docs
            ];

            if (!supportedTypes.includes(fileInfo.mimeType)) {
              alert(
                `File "${fileInfo.name}": Chỉ hỗ trợ file PDF, DOC, DOCX và Google Docs`
              );
              continue;
            }

            // Check file size (10MB limit)
            if (fileInfo.size && parseInt(fileInfo.size) > 10 * 1024 * 1024) {
              alert(
                `File "${fileInfo.name}": File quá lớn. Kích thước tối đa là 10MB`
              );
              continue;
            }

            setUploadStatus(
              `Đang tải xuống ${fileInfo.name} từ Google Drive...`
            );

            // Download file from Google Drive
            const file = await googleDriveService.downloadFile(
              pickedFile.id,
              fileInfo.name
            );

            console.log(`Downloaded file ${fileInfo.name}:`, {
              size: file.size,
              type: file.type,
              name: file.name,
            });

            setUploadStatus(`Đang upload ${file.name} lên server...`);

            // Upload to our server
            const formData = new FormData();
            formData.append("file", file);
            formData.append("user_id", userId);

            const response = await fetch("http://localhost:8000/file/upload", {
              method: "POST",
              body: formData,
            });

            if (!response.ok) {
              const errorText = await response.text();
              throw new Error(
                `Upload failed for ${fileInfo.name}: ${errorText}`
              );
            }

            const data = await response.json();

            // Call the onFileUpload callback with file ID and name
            if (onFileUpload && data.file_id) {
              onFileUpload(data.file_id, file.name);
            }

            // Don't show success message, file context will be added to UI
          } catch (fileError) {
            console.error(
              `Error processing file ${pickedFile.name}:`,
              fileError
            );
            setUploadStatus(
              `❌ Lỗi xử lý file ${pickedFile.name}: ${fileError.message}`
            );
            alert(
              `Không thể xử lý file ${pickedFile.name}. Vui lòng thử lại.\nLỗi: ${fileError.message}`
            );
          }
        }
      }
    } catch (error) {
      console.error("Google Drive upload error:", error);
      setUploadStatus(`❌ Lỗi Google Drive: ${error.message}`);
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
      setTimeout(() => {
        setIsUploading(false);
        setUploadStatus("");
      }, 2000); // Keep status visible for 2 seconds
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
          {/* Display active file contexts if present */}
          {activeFileContexts && activeFileContexts.length > 0 && (
            <div className="mb-2">
              <div className="flex flex-wrap gap-2">
                {activeFileContexts.map((fileContext) => (
                  <div
                    key={fileContext.id}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm w-fit ${
                      isLight
                        ? "bg-blue-50 text-blue-700"
                        : "bg-[#2a2a2a] text-[#d1cfc0]/70"
                    }`}
                  >
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className="truncate max-w-[150px]">
                            {fileContext.name}
                          </span>
                        </TooltipTrigger>
                        <TooltipContent>{fileContext.name}</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        e.preventDefault();
                        clearFileContext(fileContext.id);
                      }}
                      className="text-muted-foreground hover:text-foreground p-0.5 rounded-full hover:bg-gray-200 dark:hover:bg-[#333333] transition-colors"
                      aria-label="Xóa file"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

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
                accept=".pdf,.doc,.docx"
                multiple // Enable multiple file selection
                onChange={handleFileChange}
                className="hidden"
                disabled={isLoading || isUploading}
              />
              <DropdownMenu>
                <DropdownMenuTrigger>
                  <Button
                    type="button"
                    size="icon"
                    className={`${iconBtnStyle} ${
                      isUploading ? activeBtnStyle : ""
                    }`}
                    disabled={isLoading || isUploading}
                    title="Đính kèm file PDF"
                  >
                    <Paperclip className="h-5 w-5" strokeWidth={2.5} />
                    <span className="sr-only">Đính kèm file</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={handleFileButtonClick}>
                    Upload từ máy tính
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleGoogleDriveClick}>
                    Chọn từ Google Drive
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

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
          {(isUploading || uploadStatus) && (
            <div
              className={`mb-2 flex items-center justify-center p-2 rounded-md text-sm ${
                uploadStatus.includes("❌")
                  ? isLight
                    ? "bg-red-50 text-red-700"
                    : "bg-red-900/20 text-red-400"
                  : isLight
                  ? "bg-blue-50 text-blue-700"
                  : "bg-[#2a2a2a] text-[#d1cfc0]/70"
              }`}
            >
              {!uploadStatus.includes("❌") && (
                <div
                  className={`h-2 w-2 animate-pulse rounded-full mr-2 ${
                    isLight ? "bg-blue-600" : "bg-blue-400"
                  }`}
                ></div>
              )}
              {uploadStatus || "Đang tải lên file..."}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default ChatInput;
