import "./MainSteppperWrapper.css";
import { useState, useEffect, useReducer } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { 
    getOnboarding,
    saveIntrests,
    saveIdentity,
    savePreferences,
    completeOnboarding
 } from "../../../APIs/createAccountAPIs";
 import CompletionStep from "../CompletionStep";
 import IdentityStep from "../IdentityStep";
 import InterestsStep from "../IntrestStep";
 import PreferencesStep from "../PreferencesStep";


const initialState = {
    status: "LOADING_PROFILE",
    data: {
        persona: null,
        interests: [],
        acquisition_source: null,
        preferred_content_region: null
    },
    loading: false,
    error: null
};

function deriveInitialStep(profile) {
    if (!profile.persona) return "IDENTITY_STEP";
    if (!profile.interests || profile.interests.length === 0) return "INTERESTS_STEP";
    if (!profile.onboarding_completed) return "PREFERENCES_STEP";
    return "COMPLETED";
}

function reducer(state, action) {
    switch (action.type) {

        case "PROFILE_LOADED":
            return {
                ...state,
                status: deriveInitialStep(action.payload),
                data: action.payload,
                loading: false
            };

        case "SET_LOADING":
            return { ...state, loading: true, error: null };

        case "ERROR":
            return { ...state, loading: false, error: action.payload };

        case "SAVE_IDENTITY_SUCCESS":
            return {
                ...state,
                status: "INTERESTS_STEP",
                data: { ...state.data, persona: action.payload },
                loading: false
            };

        case "SAVE_INTERESTS_SUCCESS":
            return {
                ...state,
                status: "PREFERENCES_STEP",
                data: { ...state.data, interests: action.payload },
                loading: false
            };

        case "SAVE_PREFERENCES_SUCCESS":
            return {
                ...state,
                status: "READY_TO_COMPLETE",
                loading: false
            };

        case "COMPLETE_SUCCESS":
            return {
                ...state,
                status: "COMPLETED",
                loading: false
            };

        case "BACK":
            if (state.status === "INTERESTS_STEP") return { ...state, status: "IDENTITY_STEP" };
            if (state.status === "PREFERENCES_STEP") return { ...state, status: "INTERESTS_STEP" };
            return state;

        default:
            return state;
    }
}

export default function OnboardingStepper() {
    const [state, dispatch] = useReducer(reducer, initialState);
    const navigation = useNavigate();
    useEffect(() => {
    if (state.status === "COMPLETED") {
        navigation("/home");
    }
}, [state.status]);

    // 🔹 load profile on mount
    useEffect(() => {
        async function load() {
            try {
                const res = await getOnboarding();
                // console.log("This data is onboarding loading data",res)
                dispatch({ type: "PROFILE_LOADED", payload: res});
            } catch (err) {
                dispatch({ type: "ERROR", payload: err.message });
            }
        }
        load();
    }, []);

    // 🔹 handlers

    async function handlePersonaSelect(persona) {
        dispatch({ type: "SET_LOADING" });
        try {
            await saveIdentity(persona);
            dispatch({ type: "SAVE_IDENTITY_SUCCESS", payload: persona });
        } catch (err) {
            dispatch({ type: "ERROR", payload: err.message });
        }
    }

    async function handleInterestsSave(interests) {
        dispatch({ type: "SET_LOADING" });
        try {
            await saveIntrests(interests);
            dispatch({ type: "SAVE_INTERESTS_SUCCESS", payload: interests });
        } catch (err) {
            dispatch({ type: "ERROR", payload: err.message });
        }
    }

    async function handlePreferencesSave(payload) {
        dispatch({ type: "SET_LOADING" });
        try {
            console.log("Saving preferences with payload:", payload); // log the payload being sent to the API
            const { acquisition_source, preferred_content_region } = payload;
            await savePreferences(acquisition_source, preferred_content_region);
            dispatch({ type: "SAVE_PREFERENCES_SUCCESS" });
        } catch (err) {
            dispatch({ type: "ERROR", payload: err.message });
        }
    }

    async function handleComplete() {
        dispatch({ type: "SET_LOADING" });
        try {
            await completeOnboarding();
            dispatch({ type: "COMPLETE_SUCCESS" });
            navigation("/home");
        } catch (err) {
            dispatch({ type: "ERROR", payload: err.message });
        }
    }

    // 🔹 render step

    function renderStep() {
        switch (state.status) {
            case "IDENTITY_STEP":
                return (
                    <IdentityStep
                        onNext={handlePersonaSelect}
                        loading={state.loading}
                    />
                );

            case "INTERESTS_STEP":
                return (
                    <InterestsStep
                        onNext={handleInterestsSave}
                        onBack={() => dispatch({ type: "BACK" })}
                        loading={state.loading}
                    />
                );

            case "PREFERENCES_STEP":
                return (
                    <PreferencesStep
                        onNext={handlePreferencesSave}
                        onBack={() => dispatch({ type: "BACK" })}
                        onSkip={() => dispatch({ type: "SAVE_PREFERENCES_SUCCESS" })}
                        loading={state.loading}
                    />
                );

            case "READY_TO_COMPLETE":
                return (
                    <CompletionStep onComplete={handleComplete} />
                );

            case "COMPLETED":
                // navigation("/home");
                return <p>Onboarding completed. Redirecting...</p>;

            default:
                return <p>Loading...</p>;
        }
    }

    return (
    <div className="onboarding-page">
        <div className="onboarding-card">

            <div className="onboarding-header">
                <h2>Setup your Ouranious profile</h2>
                <p>Let’s personalize your experience</p>
            </div>

            <ProgressIndicator status={state.status} />

            {state.error && (
                <div className="error-banner">{state.error}</div>
            )}

            <div className="onboarding-content">
                {renderStep()}
            </div>

        </div>
    </div>
);
}


function ProgressIndicator({ status }) {

    const steps = [
        { key: "IDENTITY_STEP", label: "Identity" },
        { key: "INTERESTS_STEP", label: "Interests" },
        { key: "PREFERENCES_STEP", label: "Preferences" },
        { key: "READY_TO_COMPLETE", label: "Finish" }
    ];

    const currentIndex = steps.findIndex(s => s.key === status);

    return (
        <div className="progress-indicator">
            {steps.map((step, index) => (
                <div
                    key={step.key}
                    className={`step-item 
                        ${index < currentIndex ? "completed" : ""}
                        ${index === currentIndex ? "active" : ""}
                    `}
                >
                    <div className="step-circle">{index + 1}</div>
                    <span className="step-label">{step.label}</span>
                </div>
            ))}
        </div>
    );
}