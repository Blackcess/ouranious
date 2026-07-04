import "./PreferencesStep.css";
import { useState } from "react";

export default function PreferencesStep({ onNext, onBack, onSkip, loading }) {
    const [source, setSource] = useState("");
    const [region, setRegion] = useState("");

    return (
        <div className="preferences-step step-section">

            <div className="preferences-header">
                <h3>Optional Preferences</h3>
                <p>You can skip this step if you prefer</p>
            </div>

            <div className="preferences-form">

                <div className="form-group">
                    <label>Where did you hear about Ouranious?</label>
                    <input
                        type="text"
                        placeholder="e.g. LinkedIn, friend, Google"
                        value={source}
                        onChange={e => setSource(e.target.value)}
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label>Preferred content region</label>
                    <input
                        type="text"
                        placeholder="e.g. Africa, Europe, Global"
                        value={region}
                        onChange={e => setRegion(e.target.value)}
                        disabled={loading}
                    />
                </div>

            </div>

            <div className="preferences-footer">
                <button
                    className="secondary-btn"
                    onClick={onBack}
                    disabled={loading}
                >
                    Back
                </button>

                <div className="preferences-actions">
                    <button
                        className="ghost-btn"
                        onClick={onSkip}
                        disabled={loading}
                    >
                        Skip
                    </button>

                    <button
                        className="primary-btn"
                        onClick={() => onNext({
                            acquisition_source: source,
                            preferred_content_region: region
                        })}
                        disabled={loading}
                    >
                        {loading ? "Saving..." : "Save"}
                    </button>
                </div>
            </div>

        </div>
    );
}