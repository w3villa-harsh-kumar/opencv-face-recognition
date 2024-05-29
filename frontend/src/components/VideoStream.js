import React, { useState } from 'react';
import ListUI from './ListUI';

const VideoStream = ({ streamUrl }) => {
  const [imgSrc, setImgSrc] = useState(streamUrl);

  const handleError = () => {
    setImgSrc('https://cdn.osxdaily.com/wp-content/uploads/2013/12/there-is-no-connected-camera-mac.jpg');
  };

  return (
    <div className="video-container">
      <h1>Live Video Feeds</h1>
      <img 
        src={imgSrc} 
        alt="Live Feed" 
        onError={handleError} 
        width="720" 
        height="480" 
      />
      <ListUI />
    </div>
  );
};

export default VideoStream;
