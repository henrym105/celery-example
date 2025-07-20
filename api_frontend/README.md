# Video Processor Frontend

A React frontend for uploading and processing videos through a Celery backend.

## Features

- Drag & drop video upload interface
- Real-time processing progress tracking
- Download processed videos
- Responsive design
- Error handling and validation

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000).

### Configuration

The app is configured to proxy API requests to `http://localhost:8000` where your FastAPI backend should be running.

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm run eject` - Ejects from Create React App (irreversible)

## Usage

1. Select a video file using the file picker
2. Click "Upload & Process Video"
3. Monitor the real-time progress
4. Download the processed video when complete

## Backend Integration

This frontend is designed to work with the FastAPI + Celery backend that provides these endpoints:

- `POST /upload-and-process/` - Upload and start processing
- `GET /status/{task_id}` - Check processing status
- `GET /download/{task_id}` - Download processed video
