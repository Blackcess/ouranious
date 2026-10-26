-- Initial Provenance persistence schema. UUID columns match the canonical
-- graph's BINARY(16) UUID storage. Apply once to the configured database.

CREATE TABLE IF NOT EXISTS sources (
    source_id BINARY(16) NOT NULL,
    title TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    publisher TEXT NULL,
    url TEXT NULL,
    publication_date DATE NULL,
    retrieved_at DATETIME(6) NOT NULL,
    PRIMARY KEY (source_id),
    INDEX idx_sources_type (source_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS claims (
    claim_id BINARY(16) NOT NULL,
    status VARCHAR(30) NOT NULL,
    research_notes TEXT NOT NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (claim_id),
    INDEX idx_claims_status_created (status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS claim_sources (
    claim_id BINARY(16) NOT NULL,
    source_id BINARY(16) NOT NULL,
    PRIMARY KEY (claim_id, source_id),
    CONSTRAINT fk_claim_sources_claim FOREIGN KEY (claim_id)
        REFERENCES claims (claim_id),
    CONSTRAINT fk_claim_sources_source FOREIGN KEY (source_id)
        REFERENCES sources (source_id),
    INDEX idx_claim_sources_source (source_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS claim_propositions (
    claim_id BINARY(16) NOT NULL,
    proposition_type VARCHAR(40) NOT NULL,
    PRIMARY KEY (claim_id),
    CONSTRAINT fk_claim_propositions_claim FOREIGN KEY (claim_id)
        REFERENCES claims (claim_id),
    INDEX idx_claim_propositions_type (proposition_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS identity_attribute_propositions (
    claim_id BINARY(16) NOT NULL,
    identity_id BINARY(16) NOT NULL,
    attribute_name VARCHAR(255) NOT NULL,
    proposed_value JSON NOT NULL,
    PRIMARY KEY (claim_id),
    CONSTRAINT fk_identity_attribute_propositions_proposition
        FOREIGN KEY (claim_id) REFERENCES claim_propositions (claim_id),
    CONSTRAINT fk_identity_attribute_propositions_identity
        FOREIGN KEY (identity_id) REFERENCES identities (identity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS relationship_propositions (
    claim_id BINARY(16) NOT NULL,
    source_identity_id BINARY(16) NOT NULL,
    target_identity_id BINARY(16) NOT NULL,
    relationship_type VARCHAR(50) NOT NULL,
    existing_relationship_id BINARY(16) NULL,
    properties JSON NULL,
    PRIMARY KEY (claim_id),
    CONSTRAINT fk_relationship_propositions_proposition
        FOREIGN KEY (claim_id) REFERENCES claim_propositions (claim_id),
    CONSTRAINT fk_relationship_propositions_source_identity
        FOREIGN KEY (source_identity_id) REFERENCES identities (identity_id),
    CONSTRAINT fk_relationship_propositions_target_identity
        FOREIGN KEY (target_identity_id) REFERENCES identities (identity_id),
    CONSTRAINT fk_relationship_propositions_existing_relationship
        FOREIGN KEY (existing_relationship_id) REFERENCES relationships (relationship_id),
    INDEX idx_relationship_propositions_endpoints
        (source_identity_id, target_identity_id, relationship_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS relationship_property_propositions (
    claim_id BINARY(16) NOT NULL,
    relationship_id BINARY(16) NOT NULL,
    property_name VARCHAR(255) NOT NULL,
    proposed_value JSON NOT NULL,
    PRIMARY KEY (claim_id),
    CONSTRAINT fk_relationship_property_propositions_proposition
        FOREIGN KEY (claim_id) REFERENCES claim_propositions (claim_id),
    CONSTRAINT fk_relationship_property_propositions_relationship
        FOREIGN KEY (relationship_id) REFERENCES relationships (relationship_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS identity_proposal_propositions (
    claim_id BINARY(16) NOT NULL,
    identity_kind VARCHAR(30) NOT NULL,
    canonical_name VARCHAR(255) NOT NULL,
    aliases JSON NOT NULL,
    attributes JSON NOT NULL,
    PRIMARY KEY (claim_id),
    CONSTRAINT fk_identity_proposal_propositions_proposition
        FOREIGN KEY (claim_id) REFERENCES claim_propositions (claim_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS verification_assessments (
    assessment_id BINARY(16) NOT NULL,
    claim_id BINARY(16) NOT NULL,
    outcome VARCHAR(40) NOT NULL,
    rationale TEXT NOT NULL,
    assessed_by VARCHAR(255) NOT NULL,
    assessed_at DATETIME(6) NOT NULL,
    review_process VARCHAR(255) NULL,
    PRIMARY KEY (assessment_id),
    CONSTRAINT fk_verification_assessments_claim FOREIGN KEY (claim_id)
        REFERENCES claims (claim_id),
    INDEX idx_assessments_claim_time (claim_id, assessed_at, assessment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
