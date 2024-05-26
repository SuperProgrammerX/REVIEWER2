import React, { useState, useEffect, useRef } from 'react';

const TypingText = ({ text }) => {
  const [currentText, setCurrentText] = useState('');
  const charsPerSecond = 1000;
  const messageEndRef = useRef(null);

  useEffect(() => {
    const words = text.split(' ');
    let wordIndex = 0;
    let charIndexInWord = 0;

    const intervalId = setInterval(() => {
      if (charIndexInWord < words[wordIndex].length) {
        charIndexInWord++;
        setCurrentText((prevText) => prevText + words[wordIndex][charIndexInWord - 1]);
      } else if (wordIndex < words.length - 1) {
        setCurrentText((prevText) => prevText + ' ');
        charIndexInWord = 0;
        wordIndex++;
      } else if (charIndexInWord === words[wordIndex].length) {
        clearInterval(intervalId);
      }

      // Scroll to the end of the message as text updates
      messageEndRef.current?.scrollIntoView({ behavior: "smooth" });

    }, 1000 / charsPerSecond);

    return () => clearInterval(intervalId);
  }, [text]);

  return (
    <>
      <pre>{currentText}</pre>
      <div ref={messageEndRef} /> {/* This div acts as an anchor for scrolling */}
    </>
  );
};

export default TypingText;