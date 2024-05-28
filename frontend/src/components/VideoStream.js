import React from 'react';
import './style.css';

const VideoStream = ({ streamUrl }) => {
  console.log(streamUrl);
  return (
    <div className="video-container">
      <h1>Live Video Feeds</h1>
      <img src={streamUrl} alt="Live Feed" width="720" height="480" />
    </div>
  );
};

export default VideoStream;
