# Frontend Architecture Documentation

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Component Architecture](#component-architecture)
5. [State Management](#state-management)
6. [Authentication Flow](#authentication-flow)
7. [API Integration](#api-integration)
8. [UI/UX Design System](#uiux-design-system)
9. [Performance Optimization](#performance-optimization)
10. [Build & Deployment](#build--deployment)

## Overview

The Study Assistant for PTITer frontend is built as a modern Single Page Application (SPA) using React 18 with Vite as the build tool. The application provides an intuitive chat interface for students to interact with AI models and access educational resources.

### Key Features

- **Real-time Chat Interface**: Responsive chat UI with message history
- **Multi-Model AI Support**: Dynamic agent selection for different AI models
- **File Upload & Management**: Drag-and-drop file upload with progress tracking
- **Web Search Integration**: Toggle-enabled web search for real-time information
- **Academic Integration**: PTIT schedule and exam information access
- **Responsive Design**: Mobile-first design with desktop optimization

## Technology Stack

### Core Technologies

- **React 18.2.0**: Modern React with Hooks and Concurrent Features
- **Vite 5.4.10**: Fast build tool and development server
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS 3.4.14**: Utility-first CSS framework
- **Lucide React**: Modern icon library

### Supporting Libraries

- **@supabase/supabase-js**: Authentication and database client
- **React Router DOM**: Client-side routing
- **Axios**: HTTP client for API requests
- **React Hot Toast**: Toast notifications
- **Framer Motion**: Animation library
- **React Dropzone**: File upload functionality

### Development Tools

- **ESLint**: Code linting and quality
- **Prettier**: Code formatting
- **PostCSS**: CSS processing
- **Autoprefixer**: CSS vendor prefixing

## Project Structure

```
frontend/
├── public/
│   └── vite.svg
├── src/
│   ├── main.jsx              # Application entry point
│   ├── App.jsx               # Root component
│   ├── index.css             # Global styles
│   ├── App.css               # Component styles
│   ├── components/           # Reusable components
│   │   ├── ui/               # UI primitives
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Avatar.jsx
│   │   │   ├── Badge.jsx
│   │   │   ├── Dialog.jsx
│   │   │   ├── DropdownMenu.jsx
│   │   │   ├── Label.jsx
│   │   │   ├── Select.jsx
│   │   │   ├── Separator.jsx
│   │   │   ├── Sheet.jsx
│   │   │   ├── Switch.jsx
│   │   │   ├── Textarea.jsx
│   │   │   └── Toast.jsx
│   │   ├── AgentSelector.jsx  # AI model selection
│   │   ├── ChatInput.jsx      # Message input component
│   │   ├── ChatInterface.jsx  # Main chat UI
│   │   ├── Login.jsx          # Authentication forms
│   │   ├── Signup.jsx
│   │   ├── MessageItem.jsx    # Individual message display
│   │   ├── ProtectedRoute.jsx # Route authentication
│   │   └── Settings.jsx       # User preferences
│   ├── lib/
│   │   ├── supabase.js       # Supabase client configuration
│   │   └── utils.js          # Utility functions
│   └── assets/
│       └── avatars/          # Avatar images
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── eslint.config.js
```

## Component Architecture

### 1. Component Hierarchy

```
App
├── Router
│   ├── ProtectedRoute
│   │   └── ChatInterface
│   │       ├── AgentSelector
│   │       ├── MessageList
│   │       │   └── MessageItem (multiple)
│   │       ├── ChatInput
│   │       └── Settings
│   ├── Login
│   └── Signup
```

### 2. Core Components

#### ChatInterface.jsx

Main application interface that orchestrates the chat experience:

```jsx
function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("qwen-3b");
  const [isLoading, setIsLoading] = useState(false);
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // Message handling
  const handleSendMessage = async (message) => {
    // Add user message to state
    // Send to backend API
    // Handle response and update state
  };

  // File upload handling
  const handleFileUpload = async (files) => {
    // Process file upload
    // Update file list
    // Show upload progress
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar with agent selection and settings */}
      <div className="w-64 bg-gray-50 border-r">
        <AgentSelector
          selectedAgent={selectedAgent}
          onAgentChange={setSelectedAgent}
        />
        <Settings
          webSearchEnabled={webSearchEnabled}
          onWebSearchToggle={setWebSearchEnabled}
        />
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        <MessageList messages={messages} />
        <ChatInput
          onSendMessage={handleSendMessage}
          onFileUpload={handleFileUpload}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
```

#### MessageItem.jsx

Individual message display with support for various content types:

```jsx
function MessageItem({ message, isUser }) {
  const renderContent = () => {
    if (message.type === "text") {
      return <div className="prose">{message.content}</div>;
    }
    if (message.type === "file") {
      return <FilePreview file={message.file} />;
    }
    // Handle other message types
  };

  const renderSources = () => {
    if (!message.sources || message.sources.length === 0) return null;

    return (
      <div className="mt-2 border-t pt-2">
        <p className="text-sm text-gray-600 font-medium">Sources:</p>
        {message.sources.map((source, index) => (
          <div key={index} className="text-xs text-blue-600">
            {source.type === "web" ? (
              <a href={source.url} target="_blank" rel="noopener noreferrer">
                {source.title}
              </a>
            ) : (
              <span>{source.filename}</span>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          isUser ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-800"
        }`}
      >
        {renderContent()}
        {renderSources()}
        <div className="text-xs mt-1 opacity-70">
          {format(new Date(message.timestamp), "HH:mm")}
        </div>
      </div>
    </div>
  );
}
```

#### AgentSelector.jsx

AI model selection component with dynamic loading:

```jsx
function AgentSelector({ selectedAgent, onAgentChange }) {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAvailableAgents();
  }, []);

  const fetchAvailableAgents = async () => {
    try {
      const response = await fetch("/api/chat/agents");
      const data = await response.json();
      setAgents(data.agents);
    } catch (error) {
      console.error("Failed to fetch agents:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <Label htmlFor="agent-select">AI Model</Label>
      <Select
        value={selectedAgent}
        onValueChange={onAgentChange}
        disabled={loading}
      >
        {agents.map((agent) => (
          <SelectItem key={agent.id} value={agent.id}>
            <div className="flex items-center gap-2">
              <Badge
                variant={agent.status === "online" ? "success" : "secondary"}
              >
                {agent.status}
              </Badge>
              {agent.display_name}
            </div>
          </SelectItem>
        ))}
      </Select>
    </div>
  );
}
```

### 3. UI Component System

The application uses a custom UI component library built with Tailwind CSS:

#### Button Component

```jsx
const Button = React.forwardRef(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline:
          "border border-input hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "underline-offset-4 hover:underline text-primary",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-9 px-3 rounded-md",
        lg: "h-11 px-8 rounded-md",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);
```

## State Management

### 1. Local State with Hooks

The application primarily uses React's built-in state management:

```jsx
// Global app state
const [user, setUser] = useState(null);
const [isAuthenticated, setIsAuthenticated] = useState(false);
const [loading, setLoading] = useState(true);

// Chat state
const [messages, setMessages] = useState([]);
const [currentChat, setCurrentChat] = useState(null);
const [agents, setAgents] = useState([]);

// UI state
const [sidebarOpen, setSidebarOpen] = useState(false);
const [settings, setSettings] = useState({
  webSearchEnabled: false,
  preferredAgent: "qwen-3b",
});
```

### 2. Context Providers

#### AuthContext

```jsx
const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);

  useEffect(() => {
    // Listen to auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    return { data, error };
  };

  const signOut = async () => {
    const { error } = await supabase.auth.signOut();
    return { error };
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        signIn,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
```

### 3. Custom Hooks

#### useChat Hook

```jsx
function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (content, options = {}) => {
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          message: content,
          agent: options.agent,
          fileIds: options.fileIds,
          webSearchEnabled: options.webSearchEnabled,
        }),
      });

      const data = await response.json();

      // Add messages to state
      setMessages((prev) => [
        ...prev,
        { role: "user", content, timestamp: new Date() },
        {
          role: "assistant",
          content: data.response,
          sources: data.sources,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    messages,
    isLoading,
    sendMessage,
  };
}
```

## Authentication Flow

### 1. Supabase Auth Integration

```jsx
// lib/supabase.js
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

### 2. Protected Routes

```jsx
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !user) {
      navigate("/login");
    }
  }, [user, loading, navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return user ? children : null;
}
```

### 3. Login/Signup Components

```jsx
function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const { error } = await signIn(email, password);

    if (error) {
      toast.error(error.message);
    } else {
      navigate("/");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Sign In</CardTitle>
          <CardDescription>
            Enter your credentials to access your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
```

## API Integration

### 1. HTTP Client Configuration

```jsx
// lib/api.js
import axios from "axios";
import { supabase } from "./supabase";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api",
});

// Request interceptor to add auth token
api.interceptors.request.use(async (config) => {
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }

  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      supabase.auth.signOut();
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 2. API Service Functions

```jsx
// services/chatService.js
import api from "../lib/api";

export const chatService = {
  sendMessage: async (message, options = {}) => {
    const response = await api.post("/chat", {
      message,
      agent: options.agent,
      fileIds: options.fileIds,
      webSearchEnabled: options.webSearchEnabled,
    });
    return response.data;
  },

  getAgents: async () => {
    const response = await api.get("/chat/agents");
    return response.data;
  },

  getChatHistory: async (chatId) => {
    const response = await api.get(`/chat/${chatId}/messages`);
    return response.data;
  },
};

// services/fileService.js
export const fileService = {
  upload: async (file, onProgress) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/file/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: (progressEvent) => {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress?.(progress);
      },
    });
    return response.data;
  },

  list: async () => {
    const response = await api.get("/file/list");
    return response.data;
  },

  delete: async (fileId) => {
    const response = await api.delete(`/file/${fileId}`);
    return response.data;
  },
};
```

## UI/UX Design System

### 1. Design Tokens

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        border: "hsl(214.3 31.8% 91.4%)",
        input: "hsl(214.3 31.8% 91.4%)",
        ring: "hsl(221.2 83.2% 53.3%)",
        background: "hsl(0 0% 100%)",
        foreground: "hsl(222.2 84% 4.9%)",
        primary: {
          DEFAULT: "hsl(221.2 83.2% 53.3%)",
          foreground: "hsl(210 40% 98%)",
        },
        secondary: {
          DEFAULT: "hsl(210 40% 96%)",
          foreground: "hsl(222.2 84% 4.9%)",
        },
        destructive: {
          DEFAULT: "hsl(0 84.2% 60.2%)",
          foreground: "hsl(210 40% 98%)",
        },
        muted: {
          DEFAULT: "hsl(210 40% 96%)",
          foreground: "hsl(215.4 16.3% 46.9%)",
        },
        accent: {
          DEFAULT: "hsl(210 40% 96%)",
          foreground: "hsl(222.2 84% 4.9%)",
        },
        popover: {
          DEFAULT: "hsl(0 0% 100%)",
          foreground: "hsl(222.2 84% 4.9%)",
        },
        card: {
          DEFAULT: "hsl(0 0% 100%)",
          foreground: "hsl(222.2 84% 4.9%)",
        },
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
};
```

### 2. Typography System

```css
/* index.css */
.prose {
  @apply text-gray-700 leading-relaxed;
}

.prose h1 {
  @apply text-2xl font-bold text-gray-900 mb-4;
}

.prose h2 {
  @apply text-xl font-semibold text-gray-900 mb-3;
}

.prose h3 {
  @apply text-lg font-medium text-gray-900 mb-2;
}

.prose p {
  @apply mb-4;
}

.prose code {
  @apply bg-gray-100 px-1 py-0.5 rounded text-sm font-mono;
}

.prose pre {
  @apply bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto;
}
```

### 3. Animation System

```jsx
// Using Framer Motion for smooth animations
import { motion, AnimatePresence } from "framer-motion";

function MessageList({ messages }) {
  return (
    <div className="flex-1 overflow-y-auto p-4">
      <AnimatePresence>
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <MessageItem message={message} />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
```

## Performance Optimization

### 1. Code Splitting

```jsx
import { lazy, Suspense } from "react";

// Lazy load components
const Settings = lazy(() => import("./components/Settings"));
const FileManager = lazy(() => import("./components/FileManager"));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/settings" element={<Settings />} />
        <Route path="/files" element={<FileManager />} />
      </Routes>
    </Suspense>
  );
}
```

### 2. Memoization

```jsx
import { memo, useMemo, useCallback } from "react";

const MessageItem = memo(({ message, isUser }) => {
  const formattedTime = useMemo(() => {
    return format(new Date(message.timestamp), "HH:mm");
  }, [message.timestamp]);

  return (
    <div className={`message ${isUser ? "user" : "assistant"}`}>
      {message.content}
      <span className="timestamp">{formattedTime}</span>
    </div>
  );
});

function ChatInterface() {
  const handleSendMessage = useCallback(async (message) => {
    // Message sending logic
  }, []);

  return <ChatInput onSendMessage={handleSendMessage} />;
}
```

### 3. Virtual Scrolling for Large Message Lists

```jsx
import { FixedSizeList as List } from "react-window";

function VirtualizedMessageList({ messages }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <MessageItem message={messages[index]} />
    </div>
  );

  return (
    <List height={600} itemCount={messages.length} itemSize={100} width="100%">
      {Row}
    </List>
  );
}
```

### 4. Image Optimization

```jsx
function OptimizedImage({ src, alt, ...props }) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(false);

  return (
    <div className="relative">
      {!isLoaded && !error && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse rounded" />
      )}
      <img
        src={src}
        alt={alt}
        onLoad={() => setIsLoaded(true)}
        onError={() => setError(true)}
        className={`transition-opacity duration-300 ${
          isLoaded ? "opacity-100" : "opacity-0"
        }`}
        {...props}
      />
    </div>
  );
}
```

## Build & Deployment

### 1. Vite Configuration

```js
// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          ui: ["@radix-ui/react-dialog", "@radix-ui/react-select"],
          supabase: ["@supabase/supabase-js"],
        },
      },
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
```

### 2. Environment Configuration

```env
# .env.development
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_BASE_URL=http://localhost:5000/api

# .env.production
VITE_SUPABASE_URL=your_production_supabase_url
VITE_SUPABASE_ANON_KEY=your_production_supabase_anon_key
VITE_API_BASE_URL=https://your-api-domain.com/api
```

### 3. Build Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext js,jsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write src/**/*.{js,jsx,css,md}",
    "type-check": "tsc --noEmit"
  }
}
```

### 4. Deployment Configuration

#### Netlify Deployment

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"
```

#### Vercel Deployment

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

This frontend architecture provides a robust, scalable, and maintainable foundation for the Study Assistant application, with modern React patterns, comprehensive state management, and optimized performance.
