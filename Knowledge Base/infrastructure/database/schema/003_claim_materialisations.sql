-- One canonical materialisation per Claim. The nullable canonical target
-- columns enforce real foreign keys for both supported target kinds.
CREATE TABLE IF NOT EXISTS claim_materialisations (
    materialisation_id BINARY(16) NOT NULL,
    claim_id BINARY(16) NOT NULL,
    target_kind VARCHAR(20) NOT NULL,
    canonical_identity_id BINARY(16) NULL,
    canonical_relationship_id BINARY(16) NULL,
    resolution_outcome VARCHAR(30) NOT NULL,
    action VARCHAR(20) NOT NULL,
    override_applied BOOLEAN NOT NULL DEFAULT FALSE,
    materialised_at DATETIME(6) NOT NULL,
    PRIMARY KEY (materialisation_id),
    UNIQUE KEY uq_claim_materialisations_claim (claim_id),
    CONSTRAINT fk_claim_materialisations_claim FOREIGN KEY (claim_id)
        REFERENCES claims (claim_id),
    CONSTRAINT fk_claim_materialisations_identity FOREIGN KEY (canonical_identity_id)
        REFERENCES identities (identity_id),
    CONSTRAINT fk_claim_materialisations_relationship FOREIGN KEY (canonical_relationship_id)
        REFERENCES relationships (relationship_id),
    CONSTRAINT chk_claim_materialisations_target CHECK (
        (target_kind = 'identity'
            AND canonical_identity_id IS NOT NULL
            AND canonical_relationship_id IS NULL)
        OR
        (target_kind = 'relationship'
            AND canonical_identity_id IS NULL
            AND canonical_relationship_id IS NOT NULL)
    ),
    CONSTRAINT chk_claim_materialisations_action CHECK (
        (action = 'linked' AND resolution_outcome = 'exact_match'
            AND override_applied = FALSE)
        OR
        (action = 'created' AND resolution_outcome = 'no_match'
            AND override_applied = FALSE)
        OR
        (action = 'created' AND resolution_outcome = 'possible_duplicate'
            AND override_applied = TRUE)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
