// steps/CompletionStep.jsx
import "./CompletionStep.css";

export default function CompletionStep({ onComplete }) {
    return (
        <div className="completion-step">

            <div className="completion-icon">
                ✓
            </div>

            <h3 className="completion-title">
                You're all set 🎉
            </h3>

            <p className="completion-subtext">
                Your personalized startup experience is ready.
            </p>

            <button
                className="completion-btn primary-btn"
                onClick={onComplete}
            >
                Go to Home
            </button>

        </div>
    );
}