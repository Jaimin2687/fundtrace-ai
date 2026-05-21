# FundTrace AI - Frontend

Next.js 14 application with TypeScript, Tailwind CSS, and shadcn/ui for real-time fraud detection visualization.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Copy `.env.local.example` to `.env.local` and update:

```bash
cp .env.local.example .env.local
```

Required variables:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
NEXT_PUBLIC_API_KEY=your-api-key
```

### 3. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/          # Main dashboard with live alerts
│   │   │   └── page.tsx
│   │   ├── network/            # Network visualization page
│   │   │   └── page.tsx
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Home page
│   │
│   ├── components/
│   │   ├── AlertCard.tsx       # Alert card component
│   │   ├── LiveAlertPanel.tsx  # WebSocket alert stream
│   │   ├── GraphViewer.tsx     # Force-directed graph
│   │   ├── EvidencePanel.tsx   # Evidence package viewer
│   │   └── ui/                 # shadcn/ui components
│   │
│   └── lib/
│       ├── api.ts              # API client functions
│       └── utils.ts            # Utility functions
│
├── package.json
└── .env.local.example
```

## 🎨 Pages

### Dashboard (`/dashboard`)

Main operational dashboard with:
- **Left Sidebar**: Live alert stream (WebSocket)
- **Center**: Interactive graph visualization
- **Right Panel**: Evidence package (slide-in)
- **Top Bar**: Stats and controls

**Features:**
- Real-time fraud alerts via WebSocket
- Click alert → Load transaction subgraph
- Click node → View evidence package
- Load fraud clusters button
- Auto-updating statistics

### Network Visualization (`/network`)

Dedicated network exploration page with:
- Transaction ID search with depth control (1-4)
- Fraud cluster loading
- Interactive graph with legend
- Evidence panel on node click
- Graph statistics

**Features:**
- Search any transaction by ID
- Configurable traversal depth
- Color-coded nodes (red=fraud, green=legit, gray=unknown)
- Node size based on risk score
- Highlighted node with pulsing effect

## 🧩 Components

### AlertCard

Displays fraud alert with:
- Pattern badge (color-coded)
- Risk score progress bar
- Transaction ID (truncated)
- Timestamp (relative)
- Amount (if present)
- Click to select

### LiveAlertPanel

WebSocket-connected alert stream:
- Connection status indicator
- Last 50 alerts (newest first)
- Auto-scroll to top
- Click alert to load graph

### GraphViewer

Force-directed graph visualization:
- Dynamic import (SSR disabled)
- Color-coded nodes by label
- Size based on risk score
- Pulsing highlight effect
- Click handler for evidence
- Dark background

### EvidencePanel

Slide-in evidence viewer:
- Transaction chain with steps
- Risk scores and patterns
- Narrative description
- Total amount
- Download JSON button

## 🎨 Styling

### Theme

- **Background**: `#0f172a` (slate-950)
- **Cards**: `#1e293b` (slate-900)
- **Borders**: `#334155` (slate-800)
- **Text**: `#e2e8f0` (slate-200)

### Pattern Colors

- **Structuring/Smurfing**: Red (`#ef4444`)
- **Layering**: Orange (`#f97316`)
- **Dormant Account**: Yellow (`#eab308`)
- **Round-tripping**: Purple (`#a855f7`)
- **Default**: Gray (`#6b7280`)

### Risk Score Colors

- **High (>0.85)**: Red
- **Medium (>0.7)**: Orange
- **Low**: Green

## 🔌 API Integration

All API calls use the client in `src/lib/api.ts`:

```typescript
import { fetchGraphFocus, fetchFraudClusters, fetchEvidence, fetchStats } from '@/lib/api';

// Fetch transaction subgraph
const data = await fetchGraphFocus(txId, depth);

// Fetch fraud clusters
const clusters = await fetchFraudClusters();

// Fetch evidence package
const evidence = await fetchEvidence(txId);

// Fetch statistics
const stats = await fetchStats();
```

### WebSocket Connection

```typescript
import { getWebSocketURL } from '@/lib/api';

const ws = new WebSocket(getWebSocketURL());

ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  // Handle alert
};
```

## 📦 Dependencies

### Core
- **Next.js 16**: React framework
- **React 19**: UI library
- **TypeScript**: Type safety

### UI
- **Tailwind CSS**: Utility-first CSS
- **shadcn/ui**: Component library
- **Lucide React**: Icons
- **Framer Motion**: Animations

### Visualization
- **react-force-graph-2d**: Graph visualization
- **three.js**: 3D rendering (peer dependency)

### Utilities
- **date-fns**: Date formatting
- **clsx**: Class name utilities
- **tailwind-merge**: Tailwind class merging

## 🛠️ Development

### Run Development Server

```bash
npm run dev
```

### Build for Production

```bash
npm run build
npm start
```

### Lint Code

```bash
npm run lint
```

## 🎯 Features

### Real-time Updates
- WebSocket connection for live alerts
- Auto-updating statistics
- Instant graph updates

### Interactive Visualization
- Force-directed graph layout
- Zoom and pan controls
- Node highlighting
- Click interactions

### Evidence Generation
- Comprehensive transaction chains
- Pattern detection
- Risk scoring
- JSON export

### Responsive Design
- Dark theme throughout
- Smooth animations
- Loading states
- Error handling

## 🔧 Configuration

### Environment Variables

```env
# Backend API URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# WebSocket URL
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000

# API Key
NEXT_PUBLIC_API_KEY=your-api-key
```

### API Endpoints Used

- `GET /api/v1/graph/focus?txId={id}&depth={n}`
- `GET /api/v1/graph/fraud-clusters`
- `GET /api/v1/graph/evidence/{txId}`
- `GET /api/v1/graph/stats`
- `WebSocket /api/v1/stream/alerts`

## 🐛 Troubleshooting

### WebSocket Connection Failed

Check that:
1. Backend is running on port 8000
2. `NEXT_PUBLIC_WS_BASE_URL` is correct
3. No CORS issues (backend should allow frontend origin)

### Graph Not Rendering

Ensure:
1. `react-force-graph-2d` is installed
2. Component is dynamically imported with `ssr: false`
3. Browser supports Canvas API

### API Calls Failing

Verify:
1. Backend is running
2. `NEXT_PUBLIC_API_KEY` matches backend API_KEY
3. CORS is configured correctly

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [react-force-graph](https://github.com/vasturiano/react-force-graph)

## 🎉 Success Criteria

- ✅ Real-time alert streaming via WebSocket
- ✅ Interactive graph visualization
- ✅ Evidence package generation
- ✅ Search and exploration
- ✅ End-to-end walkthrough
- ✅ Dark theme UI
- ✅ Responsive design
- ✅ Error handling
- ✅ Loading states
