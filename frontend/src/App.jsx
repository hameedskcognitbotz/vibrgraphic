import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import AmbientBackground from './components/AmbientBackground';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Generate from './pages/Generate';
import Gallery from './pages/Gallery';
import Settings from './pages/Settings';
import { useAuth } from './hooks/useAuth';

const App = () => {
    const { isAuthenticated } = useAuth();
    const location = useLocation();
    
    // Smooth scroll to top on route change
    useEffect(() => {
        window.scrollTo(0, 0);
    }, [location.pathname]);

    return (
        <div className="min-h-screen flex flex-col relative overflow-hidden">
            <AmbientBackground />
            <Navbar />
            
            <main className="flex-grow pt-24 pb-12">
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    
                    {/* Protected Routes */}
                    <Route 
                        path="/dashboard" 
                        element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} 
                    />
                    <Route 
                        path="/generate" 
                        element={isAuthenticated ? <Generate /> : <Navigate to="/login" />} 
                    />
                    <Route 
                        path="/gallery" 
                        element={isAuthenticated ? <Gallery /> : <Navigate to="/login" />} 
                    />
                    <Route 
                        path="/settings" 
                        element={isAuthenticated ? <Settings /> : <Navigate to="/login" />} 
                    />
                </Routes>
            </main>

            <Footer />
        </div>
    );
};

export default App;
