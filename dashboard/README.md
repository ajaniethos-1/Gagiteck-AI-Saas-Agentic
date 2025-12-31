# Gagiteck Dashboard

Web dashboard for the Gagiteck AI SaaS Platform.

## Features

- **Dashboard Overview** - View stats, recent activity, and quick actions
- **Agent Management** - Create, configure, and run AI agents
- **Workflow Builder** - Design and trigger automated workflows
- **Execution Monitoring** - Track runs and view logs

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Environment Variables

Create a `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Tech Stack

- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **Icons**: Lucide React
- **Language**: TypeScript

## Project Structure

```
dashboard/
├── src/
│   ├── components/     # Reusable UI components
│   │   ├── ui/         # Base UI components
│   │   └── layout.tsx  # Main layout
│   ├── pages/          # Next.js pages
│   │   ├── agents/     # Agent management
│   │   ├── workflows/  # Workflow management
│   │   └── index.tsx   # Dashboard home
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility functions
│   └── styles/         # Global styles
├── public/             # Static assets
└── package.json
```

## Development

```bash
# Run with hot reload
npm run dev

# Type checking
npx tsc --noEmit

# Lint
npm run lint
```

## License

MIT
