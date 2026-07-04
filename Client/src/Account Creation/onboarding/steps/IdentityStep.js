// IdentityStep.jsx
import "./IdentityStep.css";

export default function IdentityStep({ onNext, loading }) {
    const personas = [
        { key: "FOUNDER", label: "Startup Founder" },
        { key: "CUSTOMER", label: "Customer" },
        { key: "INVESTOR", label: "Investor" },
        { key: "EXPLORER", label: "Explorer" }
    ];

    return (
        <div className="identity-step step-section">
            <div className="identity-header">
                <h3>Who are you?</h3>
                <p>This helps us tailor your Ouranious experience</p>
            </div>

            <div className="persona-grid">
                {personas.map(p => (
                    <button
                        key={p.key}
                        className="persona-card"
                        disabled={loading}
                        onClick={() => onNext(p.key)}
                    >
                        <span className="persona-title">{p.label}</span>
                        <span className="persona-subtext">
                            {getPersonaDescription(p.key)}
                        </span>
                    </button>
                ))}
            </div>

            {loading && <p className="identity-loading">Saving...</p>}
        </div>
    );
}

function getPersonaDescription(type) {
    switch (type) {
        case "FOUNDER":
            return "Showcase and grow your startup";
        case "CUSTOMER":
            return "Discover and use innovative products";
        case "INVESTOR":
            return "Find startups to invest in";
        case "EXPLORER":
            return "Explore the startup ecosystem";
        default:
            return "";
    }
}