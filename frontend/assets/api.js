// ============================================================
// VibeGraphic — API Client
// Handles all HTTP communication with the FastAPI backend
// ============================================================

const API_BASE = '/api/v1';

function normalizeJob(job) {
    if (!job || typeof job !== 'object') {
        return job;
    }

    let resultUrls = [];
    const rawResult = job.result_url;

    if (Array.isArray(rawResult)) {
        resultUrls = rawResult.filter(Boolean);
    } else if (typeof rawResult === 'string' && rawResult.trim()) {
        try {
            const parsed = JSON.parse(rawResult);
            resultUrls = Array.isArray(parsed) ? parsed.filter(Boolean) : [rawResult];
        } catch {
            resultUrls = [rawResult];
        }
    }

    return {
        ...job,
        data: job.data ?? job.metadata_json?.structured_content ?? job.metadata_json ?? null,
        result_url: resultUrls[0] ?? null,
        result_urls: resultUrls,
    };
}

function normalizeResponse(data) {
    if (Array.isArray(data)) {
        return data.map(normalizeJob);
    }

    if (data && typeof data === 'object' && 'id' in data && 'status' in data) {
        return normalizeJob(data);
    }

    return data;
}

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

        const data = await response.json();
        return normalizeResponse(data);
    }

    async get(path) {
        return this._request('GET', path);
    }

    async post(path, body = null) {
        return this._request('POST', path, body);
    }

    async put(path, body = null) {
        return this._request('PUT', path, body);
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
    async generateInfographic(topic, audience = 'general', format = 'infographic', tone = 'Educational', options = {}) {
        return this._request('POST', '/infographics/generate', { 
            topic, 
            audience, 
            format,
            tone,
            template_key: options.templateKey || null,
            export_preset: options.exportPreset || null,
            source_job_id: options.sourceJobId || null,
            brand_kit: options.brandKit || null,
            generation_mode: options.generationMode || 'creative',
        });
    }

    async renderContent(data, isCarousel = false, exportPreset = null, generationMode = 'creative') {
        return this._request('POST', '/infographics/render', {
            data,
            is_carousel: isCarousel,
            export_preset: exportPreset,
            generation_mode: generationMode,
        });
    }

    async articleToInfographic(topic, audience = 'general', format = 'infographic', tone = 'Educational', options = {}) {
        return this._request('POST', '/infographics/generate', {
            topic,
            audience,
            format,
            tone,
            template_key: options.templateKey || null,
            export_preset: options.exportPreset || null,
            source_job_id: options.sourceJobId || null,
            brand_kit: options.brandKit || null,
            generation_mode: options.generationMode || 'creative',
        });
    }

    async getJobStatus(jobId) {
        return this._request('GET', `/infographics/status/${jobId}`);
    }

    async getDownloadUrl(jobId) {
        return this._request('GET', `/infographics/download/${jobId}`);
    }

    async getExportPackage(jobId) {
        return this._request('GET', `/infographics/export/${jobId}`);
    }

    async getGallery() {
        return this._request('GET', '/infographics/gallery');
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
