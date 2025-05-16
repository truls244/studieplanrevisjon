// AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Create context
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isVerified, setIsVerified] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication status when the app loads
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        // Validate token and get user data
        const response = await axios.get('/backend/user/get_user', {withCredentials:true})
        if (response.status === 200) {
          const userData = await response.data;
          setCurrentUser(userData);
          setIsVerified(userData.verified);
        } else {
          // If token is invalid, clear it
          console.error('Invalid token or unauthorized');
          localStorage.removeItem('token');
          setCurrentUser(null);
          setIsVerified(false);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        setCurrentUser(null);
        setIsVerified(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);


  const login = async (email, password) => {
    try {
      const response = await axios.post("backend/user/login", { "email": email, "password": password }, {withCredentials: true} );

      if (response.status !== 200) {
        const errorData = await response.data;
        throw new Error(errorData.message || 'Login failed');
      }

      // Get user details after login
      const userResponse = await axios.get('/backend/user/get_user');

      if (userResponse.status === 200) {
        const userData = await userResponse.data;
        setCurrentUser(userData);
        setIsVerified(userData.verified);
        return { response };
      } else {
        throw new Error('Failed to get user data');
      }
    } catch (error) {
      return { success: false, error: error.response.data.message };
    }
  };


  const logout = () => {
    localStorage.removeItem('token');
    setCurrentUser(null);
    setIsVerified(false);
  };

  // Check if user is authenticated
  const isAuthenticated = !!currentUser;

  const value = {
    currentUser,
    isAuthenticated,
    isVerified,
    isLoading,
    login,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};