// ============================================================
// VibeGraphic — API Client
// Handles all HTTP communication with the FastAPI backend
// ============================================================

const API_BASE = '/api/v1';

class ApiClient {
    constructor() {
        this._token = localStorage.getItem('vg_token') || null;
    }

    get token() {
        return this._token;
    }

    set token(value) {
        this._token = value;
        if (value) {
            localStorage.setItem('vg_token', value);
        } else {
            localStorage.removeItem('vg_token');
        }
    }

    get isAuthenticated() {
        return !!this._token;
    }

    async _request(method, path, body = null, isForm = false) {
        const headers = {};
        if (this._token) {
            headers['Authorization'] = `Bearer ${this._token}`;
        }

        let options = { method, headers };

        if (body) {
            if (isForm) {
                // OAuth2 form submission
                const formData = new URLSearchParams();
                for (const [key, val] of Object.entries(body)) {
                    formData.append(key, val);
                }
                options.body = formData;
                headers['Content-Type'] = 'application/x-www-form-urlencoded';
            } else {
                options.body = JSON.stringify(body);
                headers['Content-Type'] = 'application/json';
            }
        }

        const response = await fetch(`${API_BASE}${path}`, options);

        if (response.status === 401 || response.status === 403) {
            this.token = null;
            window.location.hash = '#/login';
            throw new Error('Session expired. Please log in again.');
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Request failed (${response.status})`);
        }

        return response.json();
    }

    // --- Auth ---
    async register(email, password) {
        return this._request('POST', '/auth/register', { email, password });
    }

    async login(email, password) {
        const data = await this._request('POST', '/auth/login', {
            username: email,
            password: password
        }, true);
        this.token = data.access_token;
        return data;
    }

    logout() {
        this.token = null;
    }

    // --- Infographics ---
    async generateInfographic(topic, audience = 'general', format = 'infographic') {
        return this._request('POST', '/infographics/generate', { 
            topic, 
            audience, 
            format 
        });
    }

    async renderContent(data, isCarousel = false) {
        return this._request('POST', '/infographics/render', { data, is_carousel: isCarousel });
    }

    async articleToInfographic(topic) {
        return this._request('POST', '/infographics/article-to-infographic', { topic });
    }

    async getJobStatus(jobId) {
        return this._request('GET', `/infographics/status/${jobId}`);
    }

    async getDownloadUrl(jobId) {
        return this._request('GET', `/infographics/download/${jobId}`);
    }

    async editInfographic(jobId, data) {
        return this._request('POST', `/infographics/${jobId}/edit`, data);
    }

    // --- Profile & Content Refinement ---
    async getProfile() {
        return this._request('GET', '/auth/me');
    }

    async updateProfile(data) {
        return this._request('PUT', '/auth/me', data);
    }

    async refineContent(data, instruction, isCarousel = false) {
        return this._request('POST', '/infographics/refine', { 
            data, 
            instruction, 
            is_carousel: isCarousel 
        });
    }
}

export const api = new ApiClient();
