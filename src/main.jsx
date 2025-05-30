import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';  // Include global styles if any
import App from './App.jsx';  // Your main App component
import 'bootstrap-icons/font/bootstrap-icons.css';
import '@fortawesome/fontawesome-free/css/all.min.css';


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
