const VideoStream = ({ streamUrl }) => {
  console.log(streamUrl);
  return (
    <div>
      <h1>Live Video Feed</h1>
       <img src={streamUrl} alt="Live Feed" width="720" height="480" />
    </div>
  );
};

export default VideoStream;
