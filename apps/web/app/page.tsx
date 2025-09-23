import React from "react";
import ReactMarkdown from "react-markdown";

export const dynamic = "force-dynamic";

async function fetchDigest() {
  const r = await fetch(`/api/digest`, { cache: "no-store" });
  return r.json();
}

async function triggerRun() {
  await fetch(`/api/digest`, { method: "POST" });
}

export default async function Home() {
  const data = await fetchDigest();
  async function run() {
    "use server";
    await triggerRun();
  }
  return (
    <main style={{ maxWidth: 760, margin: "2rem auto", padding: "1rem" }}>
      <h1 style={{ fontSize: 24, fontWeight: 700 }}>Parently — parent’s desk in your pocket</h1>
      <p style={{ color: "#555", marginTop: 8 }}>What parents need to know today</p>
      <form action={run} style={{ marginTop: 16 }}>
        <button style={{ padding: "8px 12px", border: "1px solid #ccc", borderRadius: 8 }}>Run digest now</button>
      </form>
      <article style={{ marginTop: 24 }}>
        {data?.ok ? (
          <ReactMarkdown>{data.markdown}</ReactMarkdown>
        ) : (
          <div>No digest yet. Click Run above.</div>
        )}
      </article>
      <footer style={{ marginTop: 40, color: "#777", fontSize: 12 }}>
        © {new Date().getFullYear()} Parently
      </footer>
    </main>
  );
}
