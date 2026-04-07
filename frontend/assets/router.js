// ============================================================
// VibeGraphic — SPA Router
// Hash-based routing with route guards and transitions
// ============================================================

import { api } from './api.js';

class Router {
    constructor() {
        this.routes = {};
        this.currentPage = null;
        this.appEl = null;
    }

    register(path, handler, { requireAuth = false } = {}) {
        this.routes[path] = { handler, requireAuth };
    }

    start(appElement) {
        this.appEl = appElement;
        window.addEventListener('hashchange', () => this._resolve());
        this._resolve();
    }

    navigate(path) {
        window.location.hash = path;
    }

    _resolve() {
        const hash = window.location.hash || '#/';
        const path = hash.replace('#', '') || '/';

        // Find matching route
        let route = this.routes[path];

        if (!route) {
            // Try pattern matching for route params (e.g., /job/:id)
            for (const [pattern, r] of Object.entries(this.routes)) {
                const regex = new RegExp('^' + pattern.replace(/:\w+/g, '([\\w-]+)') + '$');
                const match = path.match(regex);
                if (match) {
                    route = { ...r, params: match.slice(1) };
                    break;
                }
            }
        }

        if (!route) {
            route = this.routes['/'] || Object.values(this.routes)[0];
        }

        // Auth guard
        if (route.requireAuth && !api.isAuthenticated) {
            window.location.hash = '#/login';
            return;
        }

        // If authenticated and trying to access login/register, redirect to dashboard
        if (api.isAuthenticated && (path === '/login' || path === '/register')) {
            window.location.hash = '#/dashboard';
            return;
        }

        this._render(route);
    }

    _render(route) {
        if (!this.appEl) return;

        // Page transition
        this.appEl.style.opacity = '0';
        this.appEl.style.transform = 'translateY(10px)';

        setTimeout(() => {
            this.appEl.innerHTML = '';
            const content = route.handler(route.params || []);

            if (typeof content === 'string') {
                this.appEl.innerHTML = content;
            } else if (content instanceof HTMLElement) {
                this.appEl.appendChild(content);
            }

            // Trigger transition
            requestAnimationFrame(() => {
                this.appEl.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
                this.appEl.style.opacity = '1';
                this.appEl.style.transform = 'translateY(0)';
            });
        }, 100);
    }
}

export const router = new Router();
