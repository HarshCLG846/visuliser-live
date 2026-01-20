import React from 'react';
import './Loader.css';

const Loader = ({ message }) => {
  const [currentMessage, setCurrentMessage] = React.useState(message);

  React.useEffect(() => {
    const messages = [
      "Analyzing structure...",
      "Applying materials...",
      "Rendering preview...",
      "Finalizing details..."
    ];
    let index = 0;

    // Set initial based on prop but then rotate
    if (message) setCurrentMessage(message);

    const interval = setInterval(() => {
      index = (index + 1) % messages.length;
      setCurrentMessage(messages[index]);
    }, 2000);

    return () => clearInterval(interval);
  }, [message]);

  return (
    <div className="loader-overlay">
      <div className="loader-content">
        <div className="loader-icon-container">
          <svg className="loader-house-svg" viewBox="0 0 100 100" width="80" height="80">
            {/* House Outline */}
            <path
              className="house-path"
              d="M50 10 L90 40 V90 H10 V40 L50 10 Z"
              fill="none"
              stroke="#F5E6A8"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* Door/Window Detail */}
            <path
              className="house-path-detail"
              d="M35 90 V55 H65 V90"
              fill="none"
              stroke="#F5E6A8"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>
        <div className="loader-text">
          <h3>{currentMessage}</h3>
          <p>AI is designing your exterior...</p>
        </div>
      </div>
    </div>
  );
};

export default Loader;
