import { NextResponse } from "next/server";

export async function GET() {
  const base = process.env.BACKEND_URL!;
  const key  = process.env.SHARED_SECRET!;
  const r = await fetch(`${base}/digest/today`, { headers: { "x-api-key": key }, cache: "no-store" });
  const data = await r.json();
  return NextResponse.json(data);
}

export async function POST() {
  const base = process.env.BACKEND_URL!;
  const key  = process.env.SHARED_SECRET!;
  const r = await fetch(`${base}/run-digest`, { method:"POST", headers: { "x-api-key": key }, cache: "no-store" });
  const data = await r.json();
  return NextResponse.json(data);
}