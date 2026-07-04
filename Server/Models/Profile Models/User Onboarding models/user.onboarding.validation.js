// onboarding.validation.js
import { DomainError } from "../../../Domain Errors/domainErrors.js";

const ALLOWED_PERSONAS = ["FOUNDER", "CUSTOMER", "INVESTOR", "EXPLORER"];

export function validateIdentity(req, res, next) {
    const { persona } = req.body;

    if (!persona) {
        throw DomainError.invalid("Persona is required");
    }

    if (!ALLOWED_PERSONAS.includes(persona)) {
        throw DomainError.invalid("Invalid persona value");
    }

    next();
}

//intrest validator
const ALLOWED_INTEREST_CODES = [
    "STARTUP_NEWS",
    "MARKETPLACE",
    "DISCOVER_STARTUPS",
    "SHOWCASE",
    "ENTREPRENEURSHIP",
    "INVESTING",
    "CONNECT_FOUNDERS"
];

export function validateInterests(req, res, next) {
    const { interests } = req.body;

    if (!Array.isArray(interests) || interests.length === 0) {
        throw DomainError.invalid("Interests must be a non-empty array");
    }

    const invalid = interests.filter(
        i => !ALLOWED_INTEREST_CODES.includes(i)
    );

    if (invalid.length > 0) {
        throw DomainError.invalid("Invalid interest values");   
    }
    
    next();
}

//prefernces validator
const ALLOWED_SOURCES = [
    "TWITTER",
    "LINKEDIN",
    "FRIEND",
    "GOOGLE",
    "OTHER"
];

export function validatePreferences(req, res, next) {
    const { acquisition_source, preferred_content_region } = req.body;

    if (acquisition_source && !ALLOWED_SOURCES.includes(acquisition_source)) {
        throw DomainError.invalid("Invalid acquisition_source");
    }

    if (preferred_content_region && preferred_content_region.length > 100) {
        throw DomainError.invalid("preferred_content_region too long"); 
    }

    next();
}