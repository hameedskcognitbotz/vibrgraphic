// ============================================================
// VibeGraphic — Main Application
// Premium SaaS UI for AI Infographic Generator
// ============================================================

import { api } from './api.js';
import { store } from './store.js';
import { router } from './router.js';

// ============================================================
// SVG Icons (inline for zero-dependency)
// ============================================================
const ICONS = {
    logo: `<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="lg" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
            <stop stop-color="#3b82f6"/><stop offset="1" stop-color="#8b5cf6"/>
        </linearGradient></defs>
        <rect width="32" height="32" rx="8" fill="url(#lg)"/>
        <path d="M8 22L13 10l5 8 3-4 3 8" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        <circle cx="13" cy="10" r="2" fill="#fff"/>
    </svg>`,
    sparkles: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.912 5.813L20 10l-6.088 1.187L12 17l-1.912-5.813L4 10l6.088-1.187z"/><path d="M18 14l.962 2.926L22 18l-3.038.574L18 22l-.962-3.426L14 18l3.038-.074z" opacity=".6"/></svg>`,
    zap: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
    image: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>`,
    download: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
    eye: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
    logout: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`,
    grid: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>`,
    home: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
    plus: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
    search: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
    check: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
    x: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`,
    arrowRight: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>`,
    shield: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
    layers: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>`,
    globe: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>`,
    clock: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
    palette: `<svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="7" r="1" fill="currentColor"/><circle cx="16" cy="10" r="1" fill="currentColor"/><circle cx="8" cy="10" r="1" fill="currentColor"/><circle cx="15" cy="15" r="1" fill="currentColor"/><path d="M7 15a2 2 0 012-2h0a2 2 0 012 2v0a2 2 0 01-2 2h0a2 2 0 01-2-2z" fill="currentColor"/></svg>`,
};

// ============================================================
// Toast Notifications
// ============================================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const iconColors = {
        success: '#10b981', error: '#ef4444', info: '#06b6d4', warning: '#f59e0b'
    };
    const iconPaths = {
        success: 'M20 6L9 17l-5-5',
        error: 'M18 6L6 18M6 6l12 12',
        info: 'M12 2a10 10 0 100 20 10 10 0 000-20zm0 14v-4m0-4h.01',
        warning: 'M12 9v4m0 4h.01M10.29 3.86l-8.7 15.08A1 1 0 002.46 21h17.08a1 1 0 00.87-1.5l-8.7-15.06a1 1 0 00-1.74 0z'
    };

    toast.innerHTML = `
        <svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="${iconColors[type]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="${iconPaths[type]}"/>
        </svg>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ============================================================
// Shared Components
// ============================================================

function renderNavbar(isAuthenticated = false) {
    const currentHash = window.location.hash || '#/';

    if (!isAuthenticated) {
        return `
        <nav class="navbar" id="navbar">
            <div class="container">
                <a href="#/" class="navbar-brand">
                    ${ICONS.logo}
                    <span class="navbar-brand-text"><span>Vibe</span>Graphic</span>
                </a>
                <div class="navbar-links">
                    <a href="#/" class="nav-hide-mobile">Home</a>
                    <a href="#/login" class="btn btn-ghost btn-sm">Log In</a>
                    <a href="#/register" class="btn btn-primary btn-sm">
                        ${ICONS.sparkles} Get Started
                    </a>
                </div>
            </div>
        </nav>`;
    }

    return `
    <nav class="navbar" id="navbar">
        <div class="container">
            <a href="#/dashboard" class="navbar-brand">
                ${ICONS.logo}
                <span class="navbar-brand-text"><span>Vibe</span>Graphic</span>
            </a>
            <div class="navbar-links">
                <a href="#/dashboard" class="${currentHash.includes('dashboard') ? 'active' : ''}">
                    ${ICONS.home} <span class="nav-hide-mobile">Dashboard</span>
                </a>
                <a href="#/generate" class="${currentHash.includes('generate') ? 'active' : ''}">
                    ${ICONS.sparkles} <span class="nav-hide-mobile">Generate</span>
                </a>
                <a href="#/gallery" class="${currentHash.includes('gallery') ? 'active' : ''}">
                    ${ICONS.grid} <span class="nav-hide-mobile">Gallery</span>
                </a>
                <a href="#/settings" class="${currentHash.includes('settings') ? 'active' : ''}">
                    ${ICONS.settings} <span class="nav-hide-mobile">Settings</span>
                </a>
                <button onclick="window.__logout()" id="logout-btn">
                    ${ICONS.logout} <span class="nav-hide-mobile">Logout</span>
                </button>
            </div>
        </div>
    </nav>`;
}

function renderFooter() {
    return `
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-brand">
                    ${ICONS.logo}
                    <span>VibeGraphic</span>
                </div>
                <div class="footer-links">
                    <a href="#/">Home</a>
                    <a href="#/login">Login</a>
                    <a href="https://github.com" target="_blank">GitHub</a>
                </div>
                <span class="footer-copy">&copy; 2026 VibeGraphic. All rights reserved.</span>
            </div>
        </div>
    </footer>`;
}

function renderStatusBadge(status) {
    const labels = {
        pending: 'Pending',
        processing: 'Processing',
        completed: 'Completed',
        failed: 'Failed'
    };
    return `<span class="badge badge-${status}"><span class="badge-dot"></span>${labels[status] || status}</span>`;
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now - d;
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// ============================================================
// LANDING PAGE
// ============================================================
function renderLanding() {
    return `
    ${renderNavbar(false)}
    <div class="ambient-bg"></div>
    <div class="landing-page page-transition">
        <!-- Hero -->
        <section class="hero">
            <div class="container">
                <div class="hero-badge">
                    <span class="dot"></span>
                    Powered by AI — Generate in seconds
                </div>
                <h1>
                    Transform Ideas Into<br>
                    <span class="gradient-text">Stunning Infographics</span>
                </h1>
                <p class="hero-subtitle">
                    Enter any topic and let our AI create beautiful, data-driven infographics 
                    with charts, insights, and premium designs — instantly.
                </p>
                <div class="hero-cta">
                    <a href="#/register" class="btn btn-primary btn-lg" id="hero-cta-primary">
                        ${ICONS.sparkles} Start Creating Free
                    </a>
                    <a href="#/login" class="btn btn-secondary btn-lg" id="hero-cta-secondary">
                        Log In ${ICONS.arrowRight}
                    </a>
                </div>

                <!-- Visual Mockup -->
                <div class="hero-visual">
                    <div class="hero-visual-card">
                        <div class="hero-visual-inner">
                            <div class="hero-mockup">
                                <div class="mockup-card animate-in animate-in-delay-1">
                                    <div class="mockup-card-bar" style="background: linear-gradient(90deg, #3b82f6, #8b5cf6); height: 10px; border-radius: 5px; margin-bottom: 12px;"></div>
                                    <div class="mockup-card-line" style="width: 90%;"></div>
                                    <div class="mockup-card-line" style="width: 75%;"></div>
                                    <div class="mockup-card-line" style="width: 55%;"></div>
                                    <div style="display: flex; gap: 6px; margin-top: 12px;">
                                        <div style="flex:2; height: 50px; background: rgba(59,130,246,0.2); border-radius: 6px;"></div>
                                        <div style="flex:3; height: 50px; background: rgba(139,92,246,0.2); border-radius: 6px;"></div>
                                        <div style="flex:1; height: 50px; background: rgba(16,185,129,0.2); border-radius: 6px;"></div>
                                    </div>
                                </div>
                                <div class="mockup-card animate-in animate-in-delay-2">
                                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                                        <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #10b981, #059669);"></div>
                                        <div>
                                            <div class="mockup-card-line" style="width: 80px; height: 6px;"></div>
                                            <div class="mockup-card-line" style="width: 50px; height: 4px; margin-top: 4px;"></div>
                                        </div>
                                    </div>
                                    <div style="display: flex; gap: 4px; align-items: flex-end; height: 60px; padding-top: 4px;">
                                        <div style="flex:1; height: 30%; background: rgba(59,130,246,0.4); border-radius: 3px 3px 0 0;"></div>
                                        <div style="flex:1; height: 55%; background: rgba(59,130,246,0.5); border-radius: 3px 3px 0 0;"></div>
                                        <div style="flex:1; height: 40%; background: rgba(59,130,246,0.4); border-radius: 3px 3px 0 0;"></div>
                                        <div style="flex:1; height: 75%; background: rgba(139,92,246,0.5); border-radius: 3px 3px 0 0;"></div>
                                        <div style="flex:1; height: 90%; background: rgba(139,92,246,0.6); border-radius: 3px 3px 0 0;"></div>
                                        <div style="flex:1; height: 65%; background: rgba(59,130,246,0.45); border-radius: 3px 3px 0 0;"></div>
                                    </div>
                                </div>
                                <div class="mockup-card animate-in animate-in-delay-3">
                                    <div class="mockup-card-bar" style="background: linear-gradient(90deg, #ec4899, #f59e0b); height: 10px; border-radius: 5px; margin-bottom: 12px;"></div>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                                        <div style="height: 28px; background: rgba(236,72,153,0.15); border-radius: 6px;"></div>
                                        <div style="height: 28px; background: rgba(245,158,11,0.15); border-radius: 6px;"></div>
                                        <div style="height: 28px; background: rgba(16,185,129,0.15); border-radius: 6px;"></div>
                                        <div style="height: 28px; background: rgba(59,130,246,0.15); border-radius: 6px;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Stats -->
        <section class="stats-bar">
            <div class="container">
                <div class="stats-grid">
                    <div class="stat-item animate-in">
                        <h3 class="gradient-text">10K+</h3>
                        <p>Infographics Created</p>
                    </div>
                    <div class="stat-item animate-in animate-in-delay-1">
                        <h3 class="gradient-text">&lt;30s</h3>
                        <p>Generation Time</p>
                    </div>
                    <div class="stat-item animate-in animate-in-delay-2">
                        <h3 class="gradient-text">6-10</h3>
                        <p>Rich Data Sections</p>
                    </div>
                    <div class="stat-item animate-in animate-in-delay-3">
                        <h3 class="gradient-text">100%</h3>
                        <p>AI Powered</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Features -->
        <section class="features-section" id="features">
            <div class="container">
                <div class="section-header">
                    <span class="eyebrow">Features</span>
                    <h2>Everything You Need to<br><span class="gradient-text">Create Visual Content</span></h2>
                    <p>Our AI engine analyzes your topic and generates rich, data-backed infographics with stunning visuals.</p>
                </div>
                <div class="features-grid">
                    <div class="feature-card animate-in animate-in-delay-1">
                        <div class="feature-icon feature-icon-blue">${ICONS.zap}</div>
                        <h3>AI-Powered Generation</h3>
                        <p>Simply enter a topic and our Gemini-powered AI creates complete infographics with data insights, statistics, and beautiful chart visualizations in under 30 seconds.</p>
                    </div>
                    <div class="feature-card animate-in animate-in-delay-2">
                        <div class="feature-icon feature-icon-violet">${ICONS.layers}</div>
                        <h3>Rich Visual Templates</h3>
                        <p>Each infographic features 6–10 content sections with circular layouts, dynamic charts, themed color palettes, and AI-generated image prompts for every section.</p>
                    </div>
                    <div class="feature-card animate-in animate-in-delay-3">
                        <div class="feature-icon feature-icon-emerald">${ICONS.globe}</div>
                        <h3>Instant Export & Share</h3>
                        <p>Download high-resolution PNG infographics instantly. Every generated graphic is stored securely and accessible from your personal gallery anytime.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- How It Works -->
        <section class="how-section">
            <div class="container">
                <div class="section-header">
                    <span class="eyebrow">How It Works</span>
                    <h2>Three Steps to<br><span class="gradient-text">Beautiful Infographics</span></h2>
                </div>
                <div class="steps-grid">
                    <div class="step animate-in animate-in-delay-1">
                        <div class="step-number gradient-text">1</div>
                        <h3>Enter Your Topic</h3>
                        <p>Type any topic — from "Artificial Intelligence" to "Climate Change" — and our AI takes it from there.</p>
                    </div>
                    <div class="step animate-in animate-in-delay-2">
                        <div class="step-number gradient-text">2</div>
                        <h3>AI Generates Content</h3>
                        <p>Our Gemini AI creates structured data sections, charts, insights, and visual metadata in seconds.</p>
                    </div>
                    <div class="step animate-in animate-in-delay-3">
                        <div class="step-number gradient-text">3</div>
                        <h3>Download & Share</h3>
                        <p>Get a premium, high-resolution PNG infographic ready to share on social media or presentations.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- CTA -->
        <section class="cta-section">
            <div class="container">
                <div class="cta-box">
                    <h2>Ready to Create Your<br><span class="gradient-text">First Infographic?</span></h2>
                    <p>Join thousands of creators using VibeGraphic to turn ideas into stunning visual content.</p>
                    <a href="#/register" class="btn btn-primary btn-lg" id="cta-get-started">
                        ${ICONS.sparkles} Get Started — It's Free
                    </a>
                </div>
            </div>
        </section>

        ${renderFooter()}
    </div>`;
}

// ============================================================
// AUTH PAGES
// ============================================================
function renderLogin() {
    return `
    <div class="ambient-bg"></div>
    <div class="auth-page page-transition">
        <div class="auth-card">
            <div class="auth-header">
                <a href="#/" class="auth-logo">
                    ${ICONS.logo}
                    <span class="gradient-text">VibeGraphic</span>
                </a>
                <h1>Welcome back</h1>
                <p>Log in to your account to continue creating</p>
            </div>
            <form class="auth-form" id="login-form" autocomplete="on">
                <div class="form-group">
                    <label class="form-label" for="login-email">Email address</label>
                    <input type="email" id="login-email" class="form-input" placeholder="you@example.com" required autocomplete="email">
                </div>
                <div class="form-group">
                    <label class="form-label" for="login-password">Password</label>
                    <input type="password" id="login-password" class="form-input" placeholder="••••••••" required autocomplete="current-password">
                </div>
                <button type="submit" class="btn btn-primary btn-lg" id="login-submit">
                    Log In
                </button>
                <div class="auth-divider"><span>OR</span></div>
                <a href="/api/v1/auth/login/google" class="btn btn-secondary btn-lg btn-google">
                    <svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg"><path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z" fill="#4285F4"/><path d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z" fill="#34A853"/><path d="M3.964 10.706c-.18-.54-.282-1.117-.282-1.706s.102-1.166.282-1.706V4.962H.957C.347 6.177 0 7.55 0 9s.347 2.823.957 4.038l3.007-2.332z" fill="#FBBC05"/><path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.962l3.007 2.332C4.672 5.164 6.656 3.58 9 3.58z" fill="#EA4335"/></svg>
                    Continue with Google
                </a>
            </form>
            <div class="auth-footer">
                Don't have an account? <a href="#/register">Create one free</a>
            </div>
        </div>
    </div>`;
}

function renderRegister() {
    return `
    <div class="ambient-bg"></div>
    <div class="auth-page page-transition">
        <div class="auth-card">
            <div class="auth-header">
                <a href="#/" class="auth-logo">
                    ${ICONS.logo}
                    <span class="gradient-text">VibeGraphic</span>
                </a>
                <h1>Create your account</h1>
                <p>Start generating stunning infographics for free</p>
            </div>
            <form class="auth-form" id="register-form" autocomplete="on">
                <div class="form-group">
                    <label class="form-label" for="register-email">Email address</label>
                    <input type="email" id="register-email" class="form-input" placeholder="you@example.com" required autocomplete="email">
                </div>
                <div class="form-group">
                    <label class="form-label" for="register-password">Password</label>
                    <input type="password" id="register-password" class="form-input" placeholder="Create a strong password" required minlength="6" autocomplete="new-password">
                    <div class="password-strength" id="password-strength">
                        <div class="password-strength-bar" id="pw-bar-1"></div>
                        <div class="password-strength-bar" id="pw-bar-2"></div>
                        <div class="password-strength-bar" id="pw-bar-3"></div>
                        <div class="password-strength-bar" id="pw-bar-4"></div>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary btn-lg" id="register-submit">
                    ${ICONS.sparkles} Create Account
                </button>
            </form>
            <div class="auth-footer">
                Already have an account? <a href="#/login">Log in</a>
            </div>
        </div>
    </div>`;
}

// ============================================================
// DASHBOARD PAGE
// ============================================================
function renderDashboard() {
    const jobs = store.state.jobs;
    const completedCount = jobs.filter(j => j.status === 'completed').length;
    const processingCount = jobs.filter(j => j.status === 'processing' || j.status === 'pending').length;
    const failedCount = jobs.filter(j => j.status === 'failed').length;

    const jobCardsHtml = jobs.length === 0 
        ? `<div class="empty-state">
                <div class="empty-state-icon">${ICONS.palette}</div>
                <h3>No infographics yet</h3>
                <p>Create your first AI-powered infographic by entering a topic above.</p>
                <a href="#/generate" class="btn btn-primary" id="empty-state-generate">${ICONS.sparkles} Create Your First</a>
           </div>`
        : `<div class="jobs-grid">
            ${jobs.map(job => `
                <div class="job-card" data-job-id="${job.id}" onclick="window.__viewJob(${job.id})">
                    <div class="job-card-header">
                        <span class="job-card-topic">${escapeHtml(job.topic)}</span>
                        ${renderStatusBadge(job.status)}
                    </div>
                    <div class="job-card-meta">
                        ${ICONS.clock} ${formatDate(job.created_at)}
                    </div>
                    ${job.status === 'completed' && job.result_url 
                        ? (job.result_url.startsWith('[') 
                            ? `<div class="job-card-preview carousel-stack">${JSON.parse(job.result_url).slice(0,3).map((url, i) => `<img src="${url}" style="z-index:${3-i}; transform: translateX(${i*10}px) translateY(${i*10}px);">`).join('')}</div>`
                            : `<div class="job-card-preview"><img src="${job.result_url}" alt="${escapeHtml(job.topic)}" loading="lazy"></div>`
                          )
                        : `<div class="job-card-preview"><div class="job-card-preview-placeholder">
                            ${job.status === 'processing' || job.status === 'pending' 
                                ? '<div class="spinner" style="width:24px;height:24px;border:2px solid var(--border-default);border-top-color:var(--color-primary);border-radius:50%;animation:spin 0.8s linear infinite;"></div><span>Generating...</span>'
                                : job.status === 'failed' ? '<span>⚠️ Generation failed</span>' : '<span>Waiting...</span>'
                            }
                           </div></div>`
                    }
                    <div class="job-card-actions">
                        ${job.status === 'completed' && job.result_url 
                            ? (job.result_url.startsWith('[')
                                ? `<button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); window.__viewCarousel('${job.id}')">${ICONS.grid} View Carousel</button>`
                                : `<a href="${job.result_url}" download class="btn btn-sm btn-secondary" onclick="event.stopPropagation()">${ICONS.download} Download</a>
                                   <button class="btn btn-sm btn-ghost" onclick="event.stopPropagation(); window.__previewImage('${job.result_url}', '${escapeHtml(job.topic)}')">${ICONS.eye} Preview</button>`
                              )
                            : ''
                        }
                    </div>
                </div>
            `).join('')}
           </div>`;

    return `
    ${renderNavbar(true)}
    <div class="ambient-bg"></div>
    <div class="dashboard-page page-transition">
        <div class="container">
            <div class="dashboard-header animate-in">
                <h1 class="dashboard-welcome">Welcome back 👋</h1>
                <p class="dashboard-subtitle">Create, manage, and download your AI-generated infographics.</p>
            </div>

            <!-- Quick Generate -->
            <div class="quick-generate animate-in animate-in-delay-1">
                <h2>${ICONS.sparkles} Quick Generate</h2>
                <p>Enter any topic to create a new infographic</p>
                <div class="generate-input-row">
                    <input type="text" class="form-input form-input-lg" id="quick-topic-input" placeholder="e.g., Artificial Intelligence, Climate Change, Space Exploration..." autocomplete="off">
                    <button class="btn btn-primary btn-lg" id="quick-generate-btn" onclick="window.__quickGenerate()">
                        ${ICONS.zap} Generate
                    </button>
                </div>
            </div>

            <!-- Stats -->
            <div class="stats-row animate-in animate-in-delay-2">
                <div class="stat-card">
                    <div class="stat-card-icon" style="background: var(--color-primary-light); color: var(--color-primary);">${ICONS.image}</div>
                    <div>
                        <div class="stat-card-value">${jobs.length}</div>
                        <div class="stat-card-label">Total Jobs</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon" style="background: var(--color-success-light); color: var(--color-success);">${ICONS.check}</div>
                    <div>
                        <div class="stat-card-value">${completedCount}</div>
                        <div class="stat-card-label">Completed</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon" style="background: var(--color-warning-light); color: var(--color-warning);">${ICONS.zap}</div>
                    <div>
                        <div class="stat-card-value">${processingCount}</div>
                        <div class="stat-card-label">In Progress</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon" style="background: var(--color-error-light); color: var(--color-error);">${ICONS.x}</div>
                    <div>
                        <div class="stat-card-value">${failedCount}</div>
                        <div class="stat-card-label">Failed</div>
                    </div>
                </div>
            </div>

            <!-- Recent Jobs -->
            <div class="animate-in animate-in-delay-3">
                <div class="jobs-section-header">
                    <h2>Recent Creations</h2>
                    <a href="#/gallery" class="btn btn-ghost btn-sm">${ICONS.grid} View Gallery</a>
                </div>
                ${jobCardsHtml}
            </div>
        </div>
    </div>`;
}

// ============================================================
// GENERATE PAGE
// ============================================================
function renderGenerate() {
    const currentJob = store.state.currentJob;
    const isGenerating = currentJob && (currentJob.status === 'pending' || currentJob.status === 'processing');

    const suggestions = [
        'Artificial Intelligence', 'Climate Change', 'Blockchain Technology',
        'Space Exploration', 'Quantum Computing', 'Renewable Energy',
        'Cybersecurity', 'Machine Learning'
    ];

    let progressHtml = '';
    let previewHtml = `
        <div class="preview-placeholder">
            <div class="preview-placeholder-icon">${ICONS.image}</div>
            <h3>Your infographic will appear here</h3>
            <p>Enter a topic and click Generate to create your AI-powered infographic</p>
        </div>`;

    if (isGenerating) {
        const isPending = currentJob.status === 'pending';
        progressHtml = `
        <div class="generation-progress animate-in">
            <div class="progress-header">
                <h3>Generating your infographic...</h3>
                ${renderStatusBadge(currentJob.status)}
            </div>
            <div class="progress-bar-track">
                <div class="progress-bar-fill" style="width: ${isPending ? '33' : '66'}%"></div>
            </div>
            <div class="progress-steps">
                <div class="progress-step done">
                    <span class="progress-step-dot">${ICONS.check}</span>
                    <span>Job submitted</span>
                </div>
                <div class="progress-step ${isPending ? 'active' : 'done'}">
                    <span class="progress-step-dot">${isPending ? '' : ICONS.check}</span>
                    <span>AI analyzing topic & generating content</span>
                </div>
                <div class="progress-step ${!isPending ? 'active' : ''}">
                    <span class="progress-step-dot"></span>
                    <span>Rendering infographic image</span>
                </div>
            </div>
        </div>`;

        previewHtml = `
        <div class="preview-placeholder">
            <div class="spinner" style="width:48px;height:48px;border:3px solid var(--border-default);border-top-color:var(--color-primary);border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto var(--space-4);"></div>
            <h3>Creating your masterpiece...</h3>
            <p>This usually takes 15–30 seconds</p>
        </div>`;
    }

    if (currentJob && currentJob.status === 'completed' && currentJob.result_url) {
        const isCarousel = currentJob.result_url.startsWith('[');
        const imageUrls = isCarousel ? JSON.parse(currentJob.result_url) : [currentJob.result_url];
        
        progressHtml = `
        <div class="generation-progress animate-in">
            <div class="progress-header">
                <h3>🎉 ${isCarousel ? 'Carousel' : 'Infographic'} ready!</h3>
                ${renderStatusBadge('completed')}
            </div>
            <div class="progress-bar-track">
                <div class="progress-bar-fill" style="width: 100%"></div>
            </div>
            <div style="display: flex; gap: var(--space-2); margin-top: var(--space-4); flex-wrap: wrap;">
                ${!isCarousel ? `<a href="${imageUrls[0]}" download class="btn btn-primary btn-sm">${ICONS.download} Download PNG</a>` : ''}
                <button class="btn btn-secondary btn-sm" onclick="window.__previewImage('${imageUrls[0]}', '${escapeHtml(currentJob.topic)}')">${ICONS.eye} ${isCarousel ? 'View Slides' : 'Full Preview'}</button>
                <button class="btn btn-ghost btn-sm" onclick="window.__refineContent()">${ICONS.sparkles} Refine with AI</button>
            </div>
        </div>`;
        
        previewHtml = isCarousel 
            ? `<div class="carousel-preview-grid">
                ${imageUrls.map((url, i) => `
                    <div class="carousel-preview-item" data-index="${i+1}" onclick="window.__previewImage('${url}', '${escapeHtml(currentJob.topic)} Slide ${i+1}')">
                        <img src="${url}" alt="Slide ${i+1}">
                    </div>
                `).join('')}
               </div>`
            : `<img src="${imageUrls[0]}" alt="Generated infographic" style="width:100%;height:auto;">`;
    }

    if (currentJob && currentJob.status === 'failed') {
        progressHtml = `
        <div class="generation-progress animate-in">
            <div class="progress-header">
                <h3>Generation failed</h3>
                ${renderStatusBadge('failed')}
            </div>
            <p style="color: var(--color-error); font-size: var(--fs-sm); margin-top: var(--space-3);">${currentJob.error_message || 'An unexpected error occurred. Please try again.'}</p>
            <button class="btn btn-primary btn-sm" style="margin-top: var(--space-4);" onclick="store.setState({currentJob: null}); router.navigate('#/generate')">Try Again</button>
        </div>`;
    }

    return `
    ${renderNavbar(true)}
    <div class="ambient-bg"></div>
    <div class="generate-page page-transition">
        <div class="container" style="max-width: 1400px;">
            <div class="generate-workspace animate-in">
                <!-- Sidebar Control Panel -->
                <aside class="generate-panel">
                    <h2 style="margin-bottom: var(--space-6); font-size: var(--fs-2xl); font-weight: 800;">
                        Create <span class="gradient-text">Magic</span>
                    </h2>

                    <div class="mode-toggle" style="margin-bottom: var(--space-6);">
                        <button class="mode-toggle-btn active" id="mode-topic" onclick="window.__setMode('topic')">Topic</button>
                        <button class="mode-toggle-btn" id="mode-article" onclick="window.__setMode('article')">Article</button>
                    </div>

                    <div class="generate-options-stack">
                        <div style="margin-bottom: var(--space-4);">
                            <span class="selector-label">Target Audience</span>
                            <div class="selector-switch">
                                <button class="selector-btn ${store.state.audience === 'general' ? 'active' : ''}" onclick="window.__setAudience('general')">General</button>
                                <button class="selector-btn ${store.state.audience === 'creator' ? 'active' : ''}" onclick="window.__setAudience('creator')">Creator</button>
                                <button class="selector-btn ${store.state.audience === 'educator' ? 'active' : ''}" onclick="window.__setAudience('educator')">Educator</button>
                            </div>
                        </div>
                        <div style="margin-bottom: var(--space-4);">
                            <span class="selector-label">Tone</span>
                            <div class="selector-switch">
                                <button class="selector-btn ${store.state.tone === 'Educational' ? 'active' : ''}" onclick="window.__setTone('Educational')">Edu</button>
                                <button class="selector-btn ${store.state.tone === 'Provocative' ? 'active' : ''}" onclick="window.__setTone('Provocative')">Provo</button>
                                <button class="selector-btn ${store.state.tone === 'Empathetic' ? 'active' : ''}" onclick="window.__setTone('Empathetic')">Empathetic</button>
                                <button class="selector-btn ${store.state.tone === 'Sarcastic' ? 'active' : ''}" onclick="window.__setTone('Sarcastic')">Sarcastic</button>
                            </div>
                        </div>
                        <div style="margin-bottom: var(--space-6);">
                            <span class="selector-label">Format</span>
                            <div class="selector-switch">
                                <button class="selector-btn ${store.state.format === 'infographic' ? 'active' : ''}" onclick="window.__setFormat('infographic')">Infographic</button>
                                <button class="selector-btn ${store.state.format === 'carousel' ? 'active' : ''}" onclick="window.__setFormat('carousel')">Carousel</button>
                            </div>
                        </div>
                    </div>

                    <div style="margin-bottom: var(--space-6);">
                        <span class="selector-label">Main Topic</span>
                        <div class="topic-input-wrapper">
                            <input type="text" class="topic-input" id="gen-topic-input"
                                placeholder="${currentMode === 'topic' ? 'Enter a topic...' : 'Paste URL or text...'}" 
                                autocomplete="off" value="${currentJob ? currentJob.topic : ''}"
                                ${isGenerating ? 'disabled' : ''}>
                        </div>
                        <div class="topic-suggestions" id="topic-suggestions" style="margin-top: var(--space-3); font-size: var(--fs-xs);">
                            ${suggestions.slice(0, 4).map(s => `<button class="topic-chip" onclick="document.getElementById('gen-topic-input').value='${s}'">${s}</button>`).join('')}
                        </div>
                    </div>

                    <button class="btn btn-primary btn-lg w-full" id="gen-submit-btn" 
                        ${isGenerating ? 'disabled' : ''} onclick="window.__submitGenerate()">
                        ${isGenerating ? '<span class="spinner"></span> Generating...' : `${ICONS.sparkles} Generate ${store.state.format === 'carousel' ? 'Carousel' : 'Infographic'}`}
                    </button>

                    ${progressHtml ? `<div style="margin-top: var(--space-6);">${progressHtml}</div>` : ''}

                    ${currentJob && currentJob.status === 'completed' && currentJob.data ? `
                        <div class="json-editor-container animate-in">
                            <div class="json-editor-label">
                                <span><span class="dot" style="background:#10b981;"></span> Structured Content Data</span>
                                <button class="btn btn-ghost btn-sm" style="padding:2px 8px; font-size:9px;" onclick="window.__reRenderWithTuning()">
                                    ${ICONS.zap} Push to Visual
                                </button>
                            </div>
                            <textarea class="json-textarea" spellcheck="false" 
                                oninput="window.__updateStructuredData(this.value)"
                            >${typeof currentJob.data === 'string' ? JSON.stringify(JSON.parse(currentJob.data), null, 2) : JSON.stringify(currentJob.data, null, 2)}</textarea>
                            <p style="padding: var(--space-2) var(--space-4); font-size: 9px; color: var(--text-tertiary);">
                                Edit the values above and click "Push to Visual" to update the design in real-time.
                            </p>
                        </div>
                    ` : ''}
                </aside>

                <!-- Main Preview Panel -->
                <main class="preview-panel">
                    ${previewHtml}
                </main>
            </div>
        </div>
    </div>`;
}

// ============================================================
// GALLERY PAGE
// ============================================================
function renderGallery() {
    const completedJobs = store.state.jobs.filter(j => j.status === 'completed' && j.result_url);

    const galleryItems = completedJobs.length === 0
        ? `<div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-state-icon">${ICONS.palette}</div>
                <h3>Your gallery is empty</h3>
                <p>Generate your first infographic to see it here.</p>
                <a href="#/generate" class="btn btn-primary" id="gallery-empty-generate">${ICONS.sparkles} Create Infographic</a>
           </div>`
        : completedJobs.map(job => `
            <div class="gallery-item" onclick="window.__previewImage('${job.result_url}', '${escapeHtml(job.topic)}')">
                <img src="${job.result_url}" alt="${escapeHtml(job.topic)}" class="gallery-item-image" loading="lazy">
                <div class="gallery-item-info">
                    <div class="gallery-item-topic">${escapeHtml(job.topic)}</div>
                    <div class="gallery-item-date">${ICONS.clock} ${formatDate(job.created_at)}</div>
                </div>
                <div class="gallery-item-actions">
                    <a href="${job.result_url}" download class="btn btn-sm btn-primary" onclick="event.stopPropagation()">${ICONS.download} Download</a>
                    <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); window.__previewImage('${job.result_url}', '${escapeHtml(job.topic)}')">${ICONS.eye} Preview</button>
                </div>
            </div>
        `).join('');

    return `
    ${renderNavbar(true)}
    <div class="ambient-bg"></div>
    <div class="gallery-page page-transition">
        <div class="container">
            <div class="gallery-header animate-in">
                <h1>Your <span class="gradient-text">Gallery</span></h1>
                <div class="gallery-search">
                    <span class="gallery-search-icon">${ICONS.search}</span>
                    <input type="text" class="form-input" id="gallery-search-input" placeholder="Search by topic..." autocomplete="off">
                </div>
            </div>
            <div class="gallery-grid animate-in animate-in-delay-1">
                ${galleryItems}
            </div>
        </div>
    </div>`;
}


// ============================================================
// Image Preview Modal
// ============================================================
function showPreviewModal(imageUrl, title) {
    const existing = document.querySelector('.modal-backdrop');
    if (existing) existing.remove();
    const existingModal = document.querySelector('.modal');
    if (existingModal) existingModal.remove();

    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.onclick = closeModal;

    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:var(--space-4);">
            <h3 style="font-weight:700;">${title}</h3>
            <button class="btn btn-icon btn-ghost" onclick="window.__closeModal()">${ICONS.x}</button>
        </div>
        <img src="${imageUrl}" alt="${title}" class="preview-modal-img">
        <div class="preview-modal-actions">
            <a href="${imageUrl}" download class="btn btn-primary">${ICONS.download} Download PNG</a>
            <button class="btn btn-secondary" onclick="window.__closeModal()">Close</button>
        </div>
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(modal);
}

function closeModal() {
    const backdrop = document.querySelector('.modal-backdrop');
    const modal = document.querySelector('.modal');
    if (backdrop) backdrop.remove();
    if (modal) modal.remove();
}

// ============================================================
// Utility
// ============================================================
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

// ============================================================
// Event Handlers & Business Logic
// ============================================================
let currentMode = 'topic';
let pollingIntervals = {};

window.__logout = () => {
    api.logout();
    store.setState({ user: null, jobs: [], currentJob: null });
    showToast('Logged out successfully', 'info');
    router.navigate('#/');
};

window.__previewImage = (url, title) => showPreviewModal(url, title);
window.__closeModal = closeModal;

window.__setMode = (mode) => {
    currentMode = mode;
    document.getElementById('mode-topic')?.classList.toggle('active', mode === 'topic');
    document.getElementById('mode-article')?.classList.toggle('active', mode === 'article');
    const input = document.getElementById('gen-topic-input');
    if (input) {
        input.placeholder = mode === 'topic' 
            ? 'Enter your topic...'
            : 'Paste an article URL or text...';
    }
    // Show/hide suggestions
    const suggestions = document.getElementById('topic-suggestions');
    if (suggestions) suggestions.style.display = mode === 'topic' ? 'flex' : 'none';
};

window.__viewJob = (jobId) => {
    const job = store.getJob(jobId);
    if (job && job.status === 'completed' && job.result_url) {
        showPreviewModal(job.result_url, job.topic);
    }
};

window.__setAudience = (audience) => {
    store.setState({ audience });
    router._resolve();
};

window.__setFormat = (format) => {
    store.setState({ format });
    router._resolve();
};

window.__submitGenerate = () => {
    const input = document.getElementById('gen-topic-input');
    if (input) handleGenerate(input.value);
};

window.__quickGenerate = () => {
    const input = document.getElementById('quick-topic-input');
    if (input) handleGenerate(input.value);
};

window.__viewCarousel = (jobId) => {
    const job = store.getJob(jobId);
    if (job && job.status === 'completed' && job.result_url) {
        store.setState({ currentJob: job });
        router.navigate('#/generate');
    }
};

async function handleGenerate(topic) {
    if (!topic || !topic.trim()) {
        showToast('Please enter a topic', 'warning');
        return;
    }

    try {
        const { audience, format } = store.state;
        const fn = currentMode === 'article' ? api.articleToInfographic.bind(api) : api.generateInfographic.bind(api);
        const job = await fn(topic.trim(), audience, format);

        store.addJob(job);
        store.setState({ currentJob: job });

        showToast(`Job #${job.id} submitted! Generating ${format}...`, 'success');

        // Start polling
        startPolling(job.id);

        // If we're on the dashboard, navigate to generate page
        if (window.location.hash.includes('dashboard')) {
            router.navigate('#/generate');
        } else {
            // Re-render generate page
            router._resolve();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function startPolling(jobId) {
    if (pollingIntervals[jobId]) return;

    pollingIntervals[jobId] = setInterval(async () => {
        try {
            const status = await api.getJobStatus(jobId);
            store.updateJob(jobId, status);

            if (store.state.currentJob?.id === jobId) {
                store.setState({ currentJob: { ...store.state.currentJob, ...status } });
            }

            if (status.status === 'completed' || status.status === 'failed') {
                clearInterval(pollingIntervals[jobId]);
                delete pollingIntervals[jobId];

                if (status.status === 'completed') {
                    showToast('🎉 Infographic is ready!', 'success');
                } else {
                    showToast('Generation failed: ' + (status.error_message || 'Unknown error'), 'error');
                }

                // Re-render current page
                router._resolve();
            }
        } catch (err) {
            console.error('Polling error:', err);
        }
    }, 3000);
}

// ============================================================
// Event Delegation
// ============================================================
document.addEventListener('click', (e) => {
    // Scroll navbar effect
});

document.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Login form
    if (e.target.id === 'login-form') {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const btn = document.getElementById('login-submit');

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Logging in...';

        try {
            await api.login(email, password);
            showToast('Welcome back! 🎉', 'success');
            router.navigate('#/dashboard');
        } catch (err) {
            showToast(err.message, 'error');
            document.querySelector('.auth-form')?.classList.add('auth-error-shake');
            setTimeout(() => document.querySelector('.auth-form')?.classList.remove('auth-error-shake'), 500);
        } finally {
            btn.disabled = false;
            btn.innerHTML = 'Log In';
        }
    }

    // Register form
    if (e.target.id === 'register-form') {
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const btn = document.getElementById('register-submit');

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Creating account...';

        try {
            await api.register(email, password);
            showToast('Account created! Logging you in...', 'success');
            await api.login(email, password);
            router.navigate('#/dashboard');
        } catch (err) {
            showToast(err.message, 'error');
            document.querySelector('.auth-form')?.classList.add('auth-error-shake');
            setTimeout(() => document.querySelector('.auth-form')?.classList.remove('auth-error-shake'), 500);
        } finally {
            btn.disabled = false;
            btn.innerHTML = `${ICONS.sparkles} Create Account`;
        }
    }
});

// Quick generate & generate page buttons
document.addEventListener('click', (e) => {
    if (e.target.id === 'quick-generate-btn' || e.target.closest('#quick-generate-btn')) {
        const input = document.getElementById('quick-topic-input');
        if (input) handleGenerate(input.value);
    }

    if (e.target.id === 'gen-submit-btn' || e.target.closest('#gen-submit-btn')) {
        const input = document.getElementById('gen-topic-input');
        if (input) handleGenerate(input.value);
    }
});

// Enter key on inputs
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        if (e.target.id === 'quick-topic-input') {
            e.preventDefault();
            handleGenerate(e.target.value);
        }
        if (e.target.id === 'gen-topic-input') {
            e.preventDefault();
            handleGenerate(e.target.value);
        }
    }
});

// Password strength indicator
document.addEventListener('input', (e) => {
    if (e.target.id === 'register-password') {
        const val = e.target.value;
        const bars = [
            document.getElementById('pw-bar-1'),
            document.getElementById('pw-bar-2'),
            document.getElementById('pw-bar-3'),
            document.getElementById('pw-bar-4')
        ];

        let strength = 0;
        if (val.length >= 4) strength++;
        if (val.length >= 8) strength++;
        if (/[A-Z]/.test(val) && /[a-z]/.test(val)) strength++;
        if (/\d/.test(val) || /[^A-Za-z0-9]/.test(val)) strength++;

        const classes = ['', 'active-weak', 'active-medium', 'active-medium', 'active-strong'];
        bars.forEach((bar, i) => {
            if (bar) {
                bar.className = 'password-strength-bar';
                if (i < strength) bar.classList.add(classes[strength]);
            }
        });
    }

    // Gallery search filter
    if (e.target.id === 'gallery-search-input') {
        const query = e.target.value.toLowerCase();
        document.querySelectorAll('.gallery-item').forEach(item => {
            const topic = item.querySelector('.gallery-item-topic')?.textContent.toLowerCase() || '';
            item.style.display = topic.includes(query) ? '' : 'none';
        });
    }
});

// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        navbar.classList.toggle('scrolled', window.scrollY > 30);
    }
});

// ============================================================
// Router Setup & Boot
// ============================================================
router.register('/', () => renderLanding());
router.register('/login', () => renderLogin());
router.register('/register', () => renderRegister());
router.register('/dashboard', () => renderDashboard(), { requireAuth: true });
router.register('/generate', () => renderGenerate(), { requireAuth: true });
router.register('/gallery', () => renderGallery(), { requireAuth: true });
router.register('/settings', () => renderSettings(), { requireAuth: true });

// Start app
const appEl = document.getElementById('app');
if (api.isAuthenticated) {
    api.getProfile().then(user => {
        store.setState({ user, socialHandle: user.social_handle });
        router.start(appEl);
    }).catch(() => {
        router.start(appEl);
    });
} else {
    router.start(appEl);
}

// Resume polling for any in-progress jobs
store.state.jobs.forEach(job => {
    if (job.status === 'pending' || job.status === 'processing') {
        startPolling(job.id);
    }
});

console.log('%c✨ VibeGraphic Loaded', 'color: #8b5cf6; font-size: 16px; font-weight: bold;');

// ============================================================
// Viral Enhancement Handlers
// ============================================================

window.__setTone = (tone) => {
    store.setState({ tone });
};

window.__refineContent = async () => {
    const currentJob = store.state.currentJob;
    if (!currentJob || !currentJob.data) return;

    const instruction = prompt("Refinement Instruction (e.g. 'Make it more punchy', 'Add more statistics', 'Sarcastic tone'):", "Make it viral and high-impact");
    if (!instruction) return;

    showToast("Refining content with AI...", "info");
    
    try {
        const refinedData = await api.refineContent(
            typeof currentJob.data === 'string' ? JSON.parse(currentJob.data) : currentJob.data,
            instruction,
            store.state.format === 'carousel'
        );

        if (refinedData) {
            showToast("Content refined! Re-rendering visual...", "success");
            
            const renderJob = await api.renderContent(
                refinedData,
                store.state.format === 'carousel'
            );

            store.setState({ currentJob: renderJob });
            showToast("Visual updated! 🎉", "success");
            router._resolve();
            startPolling(renderJob.id);
        }
    } catch (err) {
        showToast("Refinement failed: " + err.message, "error");
    }
};

// ============================================================
// Branding & Real-time Preview Features
// ============================================================

window.__updateBranding = async () => {
    const handle = document.getElementById('setting-social-handle')?.value;
    if (!handle) return;

    showToast("Updating branding profile...", "info");
    try {
        const user = await api.put('/auth/me', { social_handle: handle });
        if (user) {
            store.setState({ user, socialHandle: user.social_handle });
            showToast("Settings saved!", "success");
        }
    } catch (err) {
        showToast("Update failed: " + err.message, "error");
    }
};

window.__toggleSettings = () => {
    const currentView = store.state.view;
    store.setState({ view: currentView === 'settings' ? 'home' : 'settings' });
};

window.__updateStructuredData = (val) => {
    try {
        const parsed = JSON.parse(val);
        const currentJob = store.state.currentJob;
        if (currentJob) {
            store.updateJob(currentJob.id, { data: JSON.stringify(parsed) });
        }
    } catch (e) {
        // Silent error for invalid JSON during typing
    }
};

window.__reRenderWithTuning = async () => {
    const currentJob = store.state.currentJob;
    if (!currentJob) return;

    const data = typeof currentJob.data === 'string' ? JSON.parse(currentJob.data) : currentJob.data;
    
    showToast("Re-rendering with your tweaks...", "info");
    try {
        const renderResponse = await api.post('/render', {
            data,
            is_carousel: store.state.format === 'carousel'
        });

        if (renderResponse) {
            const imageUrls = renderResponse.urls || [renderResponse.url];
            store.updateJob(currentJob.id, { 
                result_url: JSON.stringify(imageUrls)
            });
            showToast("Visual updated!", "success");
        }
    } catch (err) {
        showToast("Render failed: " + err.message, "error");
    }
};

// ============================================================
// SETTINGS PAGE
// ============================================================
function renderSettings() {
    const user = store.state.user;
    return `
    ${renderNavbar(true)}
    <div class="container page-transition">
        <div class="settings-view">
            <div class="settings-header">
                <div class="feature-icon feature-icon-violet">${ICONS.settings}</div>
                <div>
                    <h2 style="margin:0;">Branding & Profile</h2>
                    <p style="margin:0;color:var(--text-tertiary);font-size:var(--fs-sm);">Configure how your content is branded</p>
                </div>
            </div>

            <div class="settings-group">
                <label class="settings-label">Social Handle</label>
                <div class="input-group">
                    <span class="gallery-search-icon">@</span>
                    <input type="text" class="form-input" id="setting-social-handle" 
                           placeholder="YourHandle (e.g. janesmith)" 
                           value="${user?.social_handle || ''}">
                </div>
                <p style="margin-top:var(--space-2);font-size:var(--fs-xs);color:var(--text-tertiary);">
                    This handle will be automatically added to the footer of all your generated graphics.
                </p>
            </div>

            <div class="settings-group">
                <label class="settings-label">Brand Display Name</label>
                <input type="text" class="form-input" id="setting-full-name" 
                       placeholder="Full Name / Brand Name" 
                       value="${user?.full_name || ''}">
            </div>

            <div style="margin-top:var(--space-10); display:flex; gap:var(--space-4);">
                <button class="btn btn-primary" onclick="window.__updateBranding()">
                    ${ICONS.check} Save Changes
                </button>
                <a href="#/dashboard" class="btn btn-ghost">Cancel</a>
            </div>
        </div>
    </div>`;
}
