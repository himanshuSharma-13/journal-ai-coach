# Analytics Layer

This dbt project demonstrates the data-engineering path of the product.

- Bronze: immutable application events from `journal_events`.
- Silver: validated journal entries with normalized dates.
- Gold: weekly activity mart powering consistency analytics.

Copy `profiles.yml.example` to your dbt profiles directory, then run `dbt run` and `dbt test`. The app stays operational even if analytics is not configured.
