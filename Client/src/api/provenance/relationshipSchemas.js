// Wire fields mirrored from the relationship property dataclasses and
// specification_registry in the FastAPI service. Values are JSON primitives;
// date fields use ISO date strings and Decimal fields use decimal strings.
export const relationshipPropertySchemas = {
  founded: ["founding_date: date", "founder_role: string", "founding_stage: enum"],
  leads: ["position: string", "start_date: date", "end_date: date", "is_current: boolean"],
  owns: ["ownership_percentage: decimal", "ownership_type: enum", "share_class: string", "start_date: date", "end_date: date", "is_current: boolean"],
  born_in: [],
  lives_in: ["start_date: date", "end_date: date", "is_current: boolean", "residence_type: string"],
  partnered_with: ["start_date: date", "end_date: date", "partnership_status: enum"],
  invested_in: ["investment_amount: decimal", "currency: string", "investment_date: date", "funding_round: enum", "pre_money_valuation: decimal", "post_money_valuation: decimal", "equity_percentage: decimal", "is_lead_investor: boolean"],
  acquired: ["acquisition_date: date", "acquisition_amount: decimal", "currency: string", "ownership_percentage_acquired: decimal", "acquisition_type: enum"],
  headquartered_in: ["headquarters_level: enum", "headquarters_function: enum", "start_date: date", "end_date: date", "is_current: boolean"],
  operates_in: ["entry_date: date", "exit_date: date", "is_current: boolean", "operating_status: enum"],
  operates_in_industry: ["start_date: date", "end_date: date", "is_primary_industry: boolean"],
  offers: ["launch_date: date", "discontinuation_date: date", "offering_status: enum"],
  develops: ["development_start_date: date", "release_date: date", "development_status: enum"],
  uses: ["adoption_date: date"],
  built_with: ["adoption_date: date", "is_core_technology: boolean"],
  available_in: ["launch_date: date", "discontinuation_date: date", "availability_status: enum"],
  located_in: [],
  part_of: [],
};
