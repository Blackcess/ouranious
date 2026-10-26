-- Keep fields that have no domain-level maximum from imposing an arbitrary
-- persistence limit. This is an additive, data-preserving schema adjustment.
ALTER TABLE identity_attribute_propositions
    MODIFY attribute_name TEXT NOT NULL;
ALTER TABLE relationship_property_propositions
    MODIFY property_name TEXT NOT NULL;
ALTER TABLE identity_proposal_propositions
    MODIFY canonical_name TEXT NOT NULL;
ALTER TABLE verification_assessments
    MODIFY assessed_by TEXT NOT NULL,
    MODIFY review_process TEXT NULL;
