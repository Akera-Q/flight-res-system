import React, { useEffect } from "react";
import axios from "axios";

const InteractionTracker = () => {
  const trackClick = async (event) => {
    const data = {
      event: "click",
      x: event.clientX,
      y: event.clientY,
    };
    console.log("📡 Click detected:", data); //testing line
    try {
      await axios.post("http://127.0.0.1:5000/api/track", data);
      console.log("Click event sent:", data);
    } catch (error) {
      console.error("Error sending click event:", error);
    }
  };

  const trackScroll = async () => {
    const data = {
      event: "scroll",
      scrollTop: document.documentElement.scrollTop,
      scrollHeight: document.documentElement.scrollHeight,
    };
    console.log("📡 Scroll detected:", data); //testing line
    try {
      await axios.post("http://127.0.0.1:5000/api/track", data);
      console.log("Scroll event sent:", data);
    } catch (error) {
      console.error("Error sending scroll event:", error);
    }
  };

  useEffect(() => {
    document.addEventListener("click", trackClick);
    window.addEventListener("scroll", trackScroll);

    return () => {
      document.removeEventListener("click", trackClick);
      window.removeEventListener("scroll", trackScroll);
    };
  }, []);

  return null;
};

export default InteractionTracker;
