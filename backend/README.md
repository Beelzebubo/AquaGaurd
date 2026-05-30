# Hackathon-Hydro

A full-stack AI-powered hydrological monitoring and disaster prediction application for Nepal.

## Project Structure

```
Hackathon-Hydro/
├── frontend/         # Vite + React + Bun frontend
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── routes/
│   │   ├── hooks/
│   │   ├── data/
│   │   ├── styles.css
│   │   └── router.tsx
│   └── [config files]
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── routes/
│   │   └── models/
│   ├── audio/
│   ├── Datasets/
│   ├── requirements.txt
│   └── [additional scripts]
└── .env              # Environment variables
```

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Copy .env.example and fill in your values
   cp .env.example .env
   ```

5. Run the backend server:
   ```bash
   cd app && python main.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies using Bun:
   ```bash
   bun install
   ```

3. Start the development server:
   ```bash
   bun dev
   ```
   
   The frontend will be available at `http://localhost:5173`

## Features

- **AI-Powered River Flow Prediction**: Predict water levels and flow rates for major rivers in Nepal
- **Disaster Prediction**: Early warning system for floods and water-related disasters
- **IFC Compliance Monitoring**: Real-time monitoring of river infrastructure
- **Voice Commands**: Voice-activated interface for hands-free operation
- **Interactive Maps**: Visual representation of river systems and monitoring stations

## Tech Stack

### Frontend
- **Framework**: React with Vite
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query
- **Routing**: TanStack Router
- **Build Tool**: Bun

### Backend
- **Framework**: FastAPI
- **Python Version**: 3.11+
- **ML/Inference**: ONNX, Transformers
- **API**: RESTful with OpenAPI documentation

## API Endpoints

See the backend API documentation at `http://localhost:8000/docs`

## License

MIT
