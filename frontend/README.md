# Universal AI Frontend — Redesigned

A ChatGPT-quality React frontend for your Universal AI backend.

## 🚀 What's New

### Removed (no longer needed)
- ❌ `App.css` — empty file, deleted
- ❌ Old `MessageBubble.jsx` — buggy regex-based math rendering
- ❌ Old `AgentSelector.jsx` — ugly native `<select>`
- ❌ Old `TypingIndicator.jsx` — just static text
- ❌ Old `MessageActions.jsx` — used `window.alert` / `window.prompt`
- ❌ Old `FilePreview.jsx` — no type icons, no remove
- ❌ Old `Sidebar.jsx` — no search, no grouping, no profile
- ❌ Inline share menu using `window.prompt` (terrible UX)

### Added
- ✅ `WelcomeScreen.jsx` — suggestion cards (like ChatGPT)
- ✅ `ChatInput.jsx` — auto-grow textarea, Enter/Shift+Enter, attach, stop button
- ✅ `TopBar.jsx` — proper dropdown menus for share/options
- ✅ `CodeBlock.jsx` — syntax highlighting + copy button + language label
- ✅ `useLocalStorage.js` — chats persist across page reloads
- ✅ Toast notifications (`react-hot-toast`) — replaces all `alert()` calls

### Improved
- ✅ **Sidebar**: search, date-grouped history (Today/Yesterday/Previous 7 Days/Older), collapsible, profile footer
- ✅ **Messages**: avatars, no buggy math regex (uses `remark-math` + `rehype-katex` properly), opens links in new tab
- ✅ **Mode selector**: pill buttons with icons + tooltips showing model name
- ✅ **Typing indicator**: animated bouncing dots
- ✅ **Send button**: morphs to Stop button while generating (with `AbortController`)
- ✅ **File preview**: type-specific icons, file size, removable chips
- ✅ **Persistence**: chats, mode, sidebar state all survive page reload
- ✅ **Error handling**: friendly error messages + toasts
- ✅ **Regenerate**: re-runs the last user message
- ✅ **Auto-title**: first user message becomes chat title

---

## 📁 File Structure

```
src/
├── App.jsx                          # Main orchestrator
├── main.jsx                         # Entry + Toaster setup
├── index.css                        # Global styles + markdown CSS
├── components/
│   ├── AgentSelector.jsx            # Mode pills (Auto/Moderate/DeepSearch)
│   ├── ChatInput.jsx                # Bottom input bar
│   ├── CodeBlock.jsx                # Syntax-highlighted code with copy
│   ├── FilePreview.jsx              # File chips with icons
│   ├── MessageActions.jsx           # Copy/like/dislike/regenerate
│   ├── MessageBubble.jsx            # User + assistant message rendering
│   ├── Sidebar.jsx                  # Chat history sidebar
│   ├── TopBar.jsx                   # Header with share/options
│   ├── TypingIndicator.jsx          # Animated dots
│   └── WelcomeScreen.jsx            # Empty-state suggestion cards
├── hooks/
│   └── useLocalStorage.js           # Persistent state hook
└── services/
    └── api.js                       # Axios with timeout + interceptors
```

---

## 🛠 Installation

```bash
# Install new deps (added)
npm install react-hot-toast remark-math rehype-katex

# All existing deps still required:
# react-markdown, remark-gfm, react-katex, katex,
# react-syntax-highlighter, lucide-react, framer-motion, axios

npm run dev
```

---

## ⚙️ Environment

Create a `.env` file in the frontend root:

```
VITE_API_URL=http://127.0.0.1:8000
```

---

## ✨ Key UX Improvements over ChatGPT

1. **Local model awareness** — mode selector shows which Ollama model is in use
2. **Persistent local-first storage** — no server required for chat history
3. **Better file UX** — file size + type icons + removable chips
4. **Stop button** — cancel mid-generation (uses `AbortController`)
5. **No popup hell** — all confirmations are toasts, not `alert()`

---

## 🔌 Backend Contract

The frontend posts to `POST /chat` with FormData:

| Field    | Type     | Description                          |
|----------|----------|--------------------------------------|
| message  | string   | User's text input                    |
| mode     | string   | `Auto`, `Moderate`, or `DeepSearch`  |
| files    | File[]   | Zero or more uploaded files          |

Expected response:

```json
{ "response": "the assistant's reply (markdown)" }
```

This matches your existing FastAPI `orchestrator.py`.
