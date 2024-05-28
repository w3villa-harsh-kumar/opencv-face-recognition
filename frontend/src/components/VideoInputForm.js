const VideoInputForm = ({ onSubmit, inputType, inputValue, setInputType, setInputValue }) => {

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      onSubmit(inputType, inputValue,);
    } catch (error) {
      console.error('Error starting video stream:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
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
  );
};

export default VideoInputForm;
