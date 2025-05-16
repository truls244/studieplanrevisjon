import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './validateuser';


const ProtectedRoute = () => {
  const { isAuthenticated, isVerified, isLoading } = useAuth();

  
  if (!isAuthenticated && !isLoading) {
    // Save the attempted URL for redirecting after login
    return <Navigate to="/login" />;
  }

  if (!isVerified && !isLoading) {
    // Save the attempted URL for redirecting after verification
    return <Navigate to="/verify" />;
  }

  return <Outlet />;
};

export default ProtectedRoute