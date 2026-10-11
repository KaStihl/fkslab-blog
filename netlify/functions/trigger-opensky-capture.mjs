// Hourly trigger for the VIE/BTS tracker's OpenSky capture workflow.
//
// GitHub's own `schedule:` cron is best-effort (measured: ~1 run per 5 h), and OpenSky only returns
// the last ~hour of departures, so skipped runs lose data. This Netlify scheduled function calls
// `workflow_dispatch` on the minute the workflow expects (see docs/OPERATIONS.md in
// KaStihl/vie-bts-tracker).
//
// Needs one environment variable in Netlify (Site configuration -> Environment variables):
//   GH_DISPATCH_TOKEN  fine-grained PAT, only repo KaStihl/vie-bts-tracker, permission "Actions: Read and write"
// Never put the token in the repository.

const URL = "https://api.github.com/repos/KaStihl/vie-bts-tracker/actions/workflows/opensky-capture.yml/dispatches";

export default async () => {
  const token = Netlify.env.get("GH_DISPATCH_TOKEN");
  if (!token) {
    console.error("GH_DISPATCH_TOKEN is not set - nothing dispatched");
    return new Response("missing token", { status: 500 });
  }
  const res = await fetch(URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "fkslab-netlify-trigger",
    },
    body: JSON.stringify({ ref: "main" }),
  });
  // 204 = workflow started
  if (res.status !== 204) {
    console.error(`dispatch failed: HTTP ${res.status} ${await res.text()}`);
    return new Response("dispatch failed", { status: 502 });
  }
  console.log("opensky-capture dispatched");
  return new Response("ok");
};

export const config = { schedule: "7 * * * *" };
