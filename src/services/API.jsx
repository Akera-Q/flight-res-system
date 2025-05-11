import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

// JWT Auth Interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Helper: Standardize errors
const handleError = (error) => {
  const message = error.response?.data?.detail || error.message;
  throw new Error(message);
};

// Auth
export const registerUser = (userData) => 
  api.post('/register/', userData).catch(handleError);

export const loginUser = async (username, password) => {
  try {
    const response = await api.post('/token', new URLSearchParams({ 
      username, 
      password 
    }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    localStorage.setItem('authToken', response.data.access_token);
    return { username, token: response.data.access_token };
  } catch (error) {
    handleError(error);
  }
};

export const logoutUser = () => {
  localStorage.removeItem('authToken');
};

// Flights
export const getFlights = () => api.get('/flights/').catch(handleError);
export const createFlight = (flightData) => 
  api.post('/flights/', flightData).catch(handleError);
export const deleteFlight = (flightId) => 
  api.delete(`/flights/${flightId}/`).catch(handleError);

// User
export const getUserProfile = () => 
  api.get('/user/profile/').catch(handleError);

// Auth Check
export const checkAuth = async () => {
  if (!localStorage.getItem('authToken')) return false;
  try {
    await getUserProfile(); // Test token validity
    return true;
  } catch {
    return false;
  }
};