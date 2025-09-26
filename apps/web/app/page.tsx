import React from "react";
import ReactMarkdown from "react-markdown";
import { headers } from "next/headers";

export const dynamic = "force-dynamic";

// Build absolute base URL from incoming request headers (works on Vercel)
function getBaseUrl() {
  const h = headers();
  const proto = h.get("x-forwarded-proto") ?? "https";
  const host = h.get("host");
  if (!host) throw new Error("Missing host header");
  return `${proto}://${host}`;
}

async function fetchDigest() {
  const base = getBaseUrl();
  const r = await fetch(`${base}/api/digest`, { cache: "no-store" });
  return r.json();
}

export default async function Home() {
  const data = await fetchDigest();

  // Server Action to trigger the digest immediately
  async function runNow() {
    "use server";
    const base = getBaseUrl();
    await fetch(`${base}/api/digest`, { method: "POST" });
  }

  return (
    <main style={{ maxWidth: 760, margin: "2rem auto", padding: "1rem" }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>
        Parently — parent’s desk in your pocket
      </h1>
      <p style={{ color: "#555", marginTop: 8 }}>What parents need to know today</p>

      <form action={runNow} style={{ marginTop: 16 }}>
        <button style={{ padding: "8px 12px", border: "1px solid #ccc", borderRadius: 8 }}>
          Run digest now
        </button>
      </form>

      <article style={{ marginTop: 24 }}>
        {data?.ok ? (
          <ReactMarkdown>{data.markdown}</ReactMarkdown>
        ) : (
          <div style={{ background: "#fff3cd", border: "1px solid #ffeeba", padding: 12, borderRadius: 8 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>No digest yet or an error occurred.</div>
            <div style={{ fontFamily: "monospace", fontSize: 12 }}>
              {data?.error ? String(data.error) : "Click Run digest now, then refresh."}
            </div>
          </div>
        )}
      </article>

      <footer style={{ marginTop: 40, color: "#777", fontSize: 12 }}>
        © {new Date().getFullYear()} Parently
      </footer>
    </main>
  );
}
