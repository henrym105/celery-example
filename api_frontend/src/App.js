import React from 'react';
import VideoUploader from './components/VideoUploader';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Video Processor</h1>
        <p>Upload a video and we'll process it for you!</p>
      </header>
      <main className="App-main">
        <VideoUploader />
      </main>
    </div>
  );
}

export default App;
