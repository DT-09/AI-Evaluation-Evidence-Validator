const json = (payload, status = 200) => new Response(JSON.stringify(payload), {
  status,
  headers: {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "x-content-type-options": "nosniff",
  },
});

const clean = (value, max) => String(value ?? "").trim().slice(0, max);

export async function onRequestPost({ request, env }) {
  const requestUrl = new URL(request.url);
  const origin = request.headers.get("Origin");
  if (!origin || new URL(origin).origin !== requestUrl.origin) {
    return json({ error: "Request origin could not be verified." }, 403);
  }

  let rawBody;
  try {
    rawBody = await request.text();
  } catch {
    return json({ error: "Invalid inquiry format." }, 400);
  }
  if (new TextEncoder().encode(rawBody).byteLength > 8192) {
    return json({ error: "Inquiry is too large." }, 413);
  }

  let body;
  try {
    body = JSON.parse(rawBody);
  } catch {
    return json({ error: "Invalid inquiry format." }, 400);
  }

  // Quietly accept the honeypot to avoid giving simple bots a useful signal.
  if (clean(body.website, 120)) return json({ ok: true });

  const company = clean(body.company, 120);
  const name = clean(body.name, 100);
  const email = clean(body.email, 254);
  const workflow = clean(body.workflow, 120);
  const context = clean(body.context, 600);
  const acknowledged = body.acknowledged === true;

  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  if (!company || !name || !emailOk || !workflow || !acknowledged) {
    return json({ error: "Complete the required fields and confirm that no confidential information is included." }, 400);
  }

  if (!env.RESEND_API_KEY || !env.DEALTIE_FROM_EMAIL || !env.DEALTIE_INQUIRY_TO) {
    return json({ error: "The private inquiry channel is not configured yet. Please use the public product overview and try again later." }, 503);
  }

  const subject = ("DealTie pilot inquiry — " + company).replace(/[\r\n]/g, " ").slice(0, 180);
  const message = [
    "New non-confidential DealTie pilot inquiry",
    "",
    "Firm: " + company,
    "Name: " + name,
    "Business email: " + email,
    "Workflow: " + workflow,
    "",
    "High-level process description:",
    context || "(Not supplied)",
    "",
    "The sender confirmed that the inquiry contains no confidential transaction information.",
    "This is a non-binding request for discussion. Do not treat it as an engagement or data authorisation.",
  ].join("\n");

  let response;
  try {
    response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "authorization": "Bearer " + env.RESEND_API_KEY,
        "content-type": "application/json",
      },
      body: JSON.stringify({
        from: env.DEALTIE_FROM_EMAIL,
        to: [env.DEALTIE_INQUIRY_TO],
        reply_to: email,
        subject,
        text: message,
      }),
    });
  } catch {
    return json({ error: "The inquiry service is temporarily unavailable." }, 502);
  }

  if (!response.ok) return json({ error: "The inquiry could not be delivered. Please try again later." }, 502);
  return json({ ok: true });
}
