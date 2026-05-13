import { useState, useEffect, createContext, useContext } from 'react';
import { api } from '../lib/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('vg_token');
            if (token) {
                try {
                    const userData = await api.getProfile();
                    setUser(userData);
                    setIsAuthenticated(true);
                } catch (err) {
                    console.error("Auth check failed:", err);
                    localStorage.removeItem('vg_token');
                }
            }
            setLoading(false);
        };
        checkAuth();
    }, []);

    const login = async (credentials) => {
        const data = await api.login(credentials);
        localStorage.setItem('vg_token', data.access_token);
        const userData = await api.getProfile();
        setUser(userData);
        setIsAuthenticated(true);
        return data;
    };

    const logout = () => {
        localStorage.removeItem('vg_token');
        setUser(null);
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
