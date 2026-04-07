// ============================================================
// VibeGraphic — Simple Reactive Store
// ============================================================

class Store {
    constructor() {
        this._state = {
            user: null,
            jobs: [],
            currentJob: null,
            pollingJobs: new Set(),
            audience: 'general',
            format: 'infographic',
            tone: 'Educational',
            socialHandle: '',
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
}

export const store = new Store();
