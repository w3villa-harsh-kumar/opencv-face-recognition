import React from 'react';

const VideoInputForm = ({ onSubmit, inputType, inputValue, setInputType, setInputValue }) => {

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue) {
      alert('The input field is empty. Please enter a value.');
      return;
    }
    try {
      onSubmit(inputType, inputValue);
    } catch (error) {
      console.error('Error starting video stream:', error);
    }
  };

  return (
    <div className="form-wrapper">
      <form className="form-container" onSubmit={handleSubmit}>
        <div>
          <label>
            <input
              type="radio"
              value="camera"  
              checked={inputType === 'camera'}
              onChange={() => setInputType('camera')}
            />
            Camera Index
          </label>
          <label>
            <input
              type="radio"
              value="rtsp"
              checked={inputType === 'rtsp'}
              onChange={() => setInputType('rtsp')}
            />
            RTSP URL
          </label>
        </div>
        <div>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={inputType === 'camera' ? 'Enter Camera Index (e.g., 0, 1)' : 'Enter RTSP URL'}
          />
        </div>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default VideoInputForm;
