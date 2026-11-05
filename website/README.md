# DealTie public website

This directory contains the public marketing and private inquiry pages for DealTie Financial Evidence Reconciliation.

## Buyer journey

1. Read the product problem and supported workflow on `index.html`.
2. Inspect the synthetic sample and complete example report.
3. Review the exact paid pilot scope and product limitations.
4. Submit a non-confidential inquiry through `pilot.html`.
5. An authorised business representative scopes the paid engagement, fee, delivery schedule, contract and data route before work begins.

The website does not sell self-serve access or accept deal files. The current Streamlit workbench is an analyst prototype and must be used with synthetic or properly redacted/authorised data only.

## Cloudflare Pages

- Project root / output directory: `website`.
- Build command: none.
- Pages Functions directory: `website/functions`.
- Inquiry endpoint: `POST /api/pilot-inquiry`.

Configure encrypted Production environment variables as described in `commercial/deployment-checklist.md`. The endpoint sends limited inquiry details through Resend; it does not store inquiry contents or accept attachments.

## Release checks

- Verify the public homepage, pilot page and sample report.
- Test mobile navigation and sample filters.
- Submit a synthetic inquiry and verify delivery.
- Confirm missing environment variables produce an explicit error.
- Do not publish a form as operational until its email route has been tested.
- Configure rate limiting/WAF for the inquiry endpoint.
- Re-check product claims against the current application.

A GitHub commit does not deploy the Cloudflare Pages site. Verify the Pages project and live deployment separately.
