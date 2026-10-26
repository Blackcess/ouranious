# Database schema scripts

This repository does not currently have a migration runner or an initial schema
script. The numbered SQL files here are the provenance schema additions. Apply
them in numeric order to the configured MySQL database using the project's
existing database credentials:

1. `001_provenance.sql` creates the provenance tables and their initial
   foreign keys and indexes.
2. `002_provenance_text_capacity.sql` removes persistence length limits from
   fields that have no corresponding domain limit.
3. `003_claim_materialisations.sql` adds the append-only, one-per-Claim link to
   a canonical identity or relationship, including duplicate-override audit
   data.

Both scripts are additive and preserve existing rows. `001` uses
`CREATE TABLE IF NOT EXISTS`; `002` changes only the declared column capacities.
Do not use these files as a replacement for future schema migration tooling.
