// src/App.js
import React, { useState } from "react";
import VideoInputForm from "./components/VideoInputForm";
import VideoStream from "./components/VideoStream";
import "./styles/Listui.css";

const App = () => {
    const [streamUrl, setStreamUrl] = useState("");
    const [inputType, setInputType] = useState("camera");
    const [inputValue, setInputValue] = useState("");

    const handleFormSubmit = (inputType, inputValue) => {
        const streamUrl = `http://localhost:8000/video_feed?input_type=${inputType}&input_value=${inputValue}`;
        setStreamUrl(streamUrl);
    };

    return (
        <div>
            {!streamUrl && <VideoInputForm
                onSubmit={handleFormSubmit}
                inputType={inputType}
                inputValue={inputValue}
                setInputType={setInputType}
                setInputValue={setInputValue}
            />}
            {streamUrl && <VideoStream streamUrl={streamUrl} />}

          

        </div>
    );
};

export default App;
