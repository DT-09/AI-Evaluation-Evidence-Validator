# DealTie deployment and private inquiry setup

## Cloudflare Pages

- Project root / output directory: `website`.
- Build command: none (static HTML plus Pages Functions).
- The Pages Functions directory is `website/functions`.
- Deploy the latest `main` branch only after the repository tests pass.

## Private pilot inquiry endpoint

The website form posts to `/api/pilot-inquiry`. The Pages Function sends a plain-text email through Resend. It does not write inquiry contents to a database or accept attachments.

Configure these as Cloudflare Pages **encrypted environment variables** for Production (and Preview only if intentionally testing with a separate recipient):

| Variable | Purpose |
|---|---|
| `RESEND_API_KEY` | Resend API credential |
| `DEALTIE_FROM_EMAIL` | Sender address on a domain verified with Resend |
| `DEALTIE_INQUIRY_TO` | Business inbox controlled by the authorised adult/business representative |

Never commit credentials, API keys or private inbox addresses to the repository. The authorised adult/business representative must control the inbox, email provider, domain and any resulting commercial engagement.

### Setup sequence

1. An authorised adult/business representative creates and controls the Resend account and verifies a sending domain.
2. Add the three environment variables in Cloudflare Pages.
3. Deploy the site and submit a test inquiry containing synthetic, non-confidential information.
4. Confirm the message arrives, the reply-to address is correct, and no data is written to an application database.
5. Configure Cloudflare WAF/rate limiting for `POST /api/pilot-inquiry` before promoting the form broadly.
6. Test malformed JSON, missing fields, oversized requests, invalid origin and an unconfigured environment.

If the variables are missing, the endpoint returns a configuration error and does not claim that an inquiry was delivered.

## Streamlit workbench

Deploy `dealtie/app.py` as the Streamlit app with `dealtie/requirements.txt` as the dependency file. Use synthetic data for public demos. The current prototype is not approved for confidential transaction materials.

## Release verification

- Run `PYTHONPATH=. python -m unittest discover -s dealtie/tests -v`.
- Run `python -m compileall -q dealtie`.
- Open the public website and the pilot page.
- Submit a synthetic inquiry and verify delivery.
- Load the synthetic workbench case, run reconciliation and download JSON, CSV and HTML outputs.
- Confirm the four synthetic metrics and their statuses agree between the workbench and public sample report.

A successful GitHub commit or build does not prove that the deployed website or email configuration works.
