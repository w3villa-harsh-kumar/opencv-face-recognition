import React from 'react';
import ListUI from './ListUI';

const VideoStream = ({ streamUrl }) => {
  return (
    <div className="video-container">
      <h1>Live Video Feeds</h1>
      <img src={streamUrl} alt="Live Feed" width="720" height="480" />
      <ListUI />
    </div>
  );
};

export default VideoStream;
