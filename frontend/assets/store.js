// ============================================================
// VibeGraphic — Simple Reactive Store
// ============================================================

class Store {
    constructor() {
        const persistedBrandKit = this._readJson('vg_brand_kit', {
            brand_name: '',
            social_handle: '',
            primary_color: '#3b82f6',
            accent_color: '#8b5cf6',
            cta_text: 'Follow for more creator-ready visuals',
            logo_url: '',
        });
        const persistedAnalytics = this._readJson('vg_analytics', {
            events: [],
            counters: {},
            last_active_at: null,
        });
        this._state = {
            user: null,
            jobs: [],
            currentJob: null,
            pollingJobs: new Set(),
            audience: 'general',
            format: 'carousel',
            tone: 'Educational',
            socialHandle: '',
            exportPreset: 'instagram_carousel',
            templateKey: 'tips',
            generationMode: 'creative',
            brandKit: persistedBrandKit,
            analytics: persistedAnalytics,
            draftTopic: '',
        };
        this._listeners = [];
    }

    get state() {
        return this._state;
    }

    setState(partial) {
        this._state = { ...this._state, ...partial };
        this._notify();
    }

    subscribe(listener) {
        this._listeners.push(listener);
        return () => {
            this._listeners = this._listeners.filter(l => l !== listener);
        };
    }

    _notify() {
        this._listeners.forEach(fn => fn(this._state));
    }

    // Convenience
    addJob(job) {
        const jobs = [job, ...this._state.jobs.filter(j => j.id !== job.id)];
        this.setState({ jobs });
    }

    updateJob(jobId, updates) {
        const jobs = this._state.jobs.map(j =>
            j.id === jobId ? { ...j, ...updates } : j
        );
        this.setState({ jobs });
    }

    getJob(jobId) {
        return this._state.jobs.find(j => j.id === jobId);
    }

    _readJson(key, fallback) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : fallback;
        } catch {
            return fallback;
        }
    }
}

export const store = new Store();
