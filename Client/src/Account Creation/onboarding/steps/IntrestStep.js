// steps/InterestsStep.jsx
import { useState } from "react";
import "./IntrestStep.css";

const ALL_INTERESTS = [
    { key: "STARTUP_NEWS", label: "Startup News" },
    { key: "MARKETPLACE", label: "Marketplace" },
    { key: "DISCOVER_STARTUPS", label: "Discover Startups" },
    { key: "SHOWCASE", label: "Showcase Your Startup" },
    { key: "ENTREPRENEURSHIP", label: "Entrepreneurship Insights" },
    { key: "INVESTING", label: "Investing in Startups" },
    { key: "CONNECT_FOUNDERS", label: "Connect with Founders" }
];

export default function InterestsStep({ onNext, onBack, loading }) {
    const [selected, setSelected] = useState([]);

    function toggle(item) {
        setSelected(prev =>
            prev.includes(item)
                ? prev.filter(i => i !== item)
                : [...prev, item]
        );
    }

    return (
        <div className="interests-step step-section">

            <div className="interests-header">
                <h3>Select your interests</h3>
                <p>Pick at least one to personalize your feed</p>
            </div>

            <div className="interest-grid">
                {ALL_INTERESTS.map(i => (
                    <button
                        key={i.key}
                        className={`interest-chip ${selected.includes(i.key) ? "active" : ""}`}
                        onClick={() => toggle(i.key)}
                        disabled={loading}
                    >
                        {i.label}
                    </button>
                ))}
            </div>

            <div className="interests-footer">
                <button className="secondary-btn" onClick={onBack} disabled={loading}>
                    Back
                </button>

                <button
                    className="primary-btn"
                    disabled={selected.length === 0 || loading}
                    onClick={() => onNext(selected)}
                >
                    {loading ? "Saving..." : "Next"}
                </button>
            </div>

        </div>
    );
}