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
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-semibold text-gray-900">Parently — parent's desk in your pocket</h1>
      <p className="text-gray-500 mt-1">What parents need to know today</p>
      
      <div className="mt-4 flex gap-3">
        <form action={run}>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Run digest now
          </button>
        </form>
        <a 
          href="/auth/google/start" 
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Authorize Gmail
        </a>
      </div>
      
      <article className="prose prose-neutral mt-6 max-w-none">
        {data?.ok ? (
          <ReactMarkdown>{data.markdown}</ReactMarkdown>
        ) : (
          <div className="text-gray-500 italic">No digest yet. Click "Run digest now" above.</div>
        )}
      </article>
      
      <footer className="mt-8 pt-4 border-t border-gray-200 text-sm text-gray-500">
        © {new Date().getFullYear()} Parently
      </footer>
    </main>
  );
}
