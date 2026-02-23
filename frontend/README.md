# ChainGuard — AI Plagiarism Detection Frontend

A production-grade React + Vite frontend for the Blockchain + AI Plagiarism Detection System.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 18 + Vite 5 |
| Routing | React Router v6 |
| Styling | Tailwind CSS v3 + custom CSS variables |
| HTTP | Axios |
| File Upload | react-dropzone |
| Icons | Lucide React |
| Auth | localStorage-based mock (replace with real Node/Express backend) |

---

## Folder Structure

```
src/
├── api/
│   ├── axios.js          ← Axios instance (baseURL: http://localhost:5000)
│   ├── plagiarismApi.js  ← Flask API calls (check, verify, reports, download)
│   └── authService.js    ← Mock Node/Express auth (signup/login)
├── context/
│   ├── AuthContext.jsx   ← User state + localStorage persistence
│   └── ThemeContext.jsx  ← Dark/light mode toggle
├── components/
│   ├── FileUpload.jsx    ← react-dropzone upload zone
│   ├── BlockchainBadge.jsx ← Tx hash, IPFS CID, block number display
│   ├── SourceList.jsx    ← Plagiarized sources with similarity bars
│   ├── DocumentViewer.jsx← Text viewer with highlighted plagiarized sections
│   ├── CircularScore.jsx ← SVG circular progress bar
│   ├── Badges.jsx        ← RiskBadge + CopyButton
│   ├── Sidebar.jsx       ← Navigation sidebar
│   └── Topbar.jsx        ← Top bar with theme toggle
├── pages/
│   ├── Login.jsx         ← Sign in / Sign up page
│   ├── Dashboard.jsx     ← File upload + stats
│   ├── ReportDetails.jsx ← Full results (score, sources, document, blockchain)
│   ├── History.jsx       ← Past reports table with download
│   └── Verify.jsx        ← Blockchain verification portal
└── utils/
    └── mockData.js       ← Demo data generator + localStorage history helpers
```

---

## Quick Start

```bash
# 1. Install dependencies
cd chainguard
npm install

# 2. Start the dev server
npm run dev

# 3. Open in browser
# http://localhost:5173
```

> **Note:** If your Flask backend is not running on `http://localhost:5000`, the app automatically falls back to realistic mock data so you can demo all features offline.

---

## Flask Backend Integration

The frontend talks to these endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/check` | `multipart/form-data`: `file`, `user_id`, `store_on_blockchain` |
| `GET`  | `/verify/:hash` | Returns `{ exists, verified, metadata }` |
| `GET`  | `/reports/:userId` | Returns list of past submissions |
| `GET`  | `/download/:id` | Downloads report JSON |

All calls are in `src/api/plagiarismApi.js`. The Axios base URL is configured in `src/api/axios.js`.

### CORS
Your Flask app already has `CORS(app)`. React dev server runs on port **5173** by default.

---

## Authentication

The mock auth service (`src/api/authService.js`) stores users in `localStorage`. To connect to a real Node/Express + SQLite/JWT backend, replace the `authService.signup` and `authService.login` functions with `axios.post('/auth/signup', ...)` etc.

---

## Key Design Decisions

- **User ID consistency**: The `user.id` from `AuthContext` is always sent with `/check` and `/reports` calls. It's a stable string like `user_1715000000000_ab1c2d`.
- **Report ID = Verification Hash**: The `report_id` field from `/check` is displayed prominently and used as the hash for `/verify/:hash`.
- **Demo mode**: When Flask is unreachable, `generateMockResult()` creates a realistic response so all UI features are demonstrable.
- **History persistence**: Reports are cached in `localStorage` keyed by `chainguard_history_{userId}` as a fallback when `/reports/:userId` is unavailable.

---

## Build for Production

```bash
npm run build
# Output → dist/
```
