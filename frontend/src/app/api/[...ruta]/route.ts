import { NextRequest } from "next/server";

const allowed = /^[a-z0-9/_.-]+$/;
async function proxy(request: NextRequest, { params }: { params: Promise<{ ruta: string[] }> }) {
  const path = (await params).ruta.join("/");
  if (!allowed.test(path) || path.includes("..")) return Response.json({detail:"Ruta no válida."}, {status:400});
  if (request.method !== "GET") {
    const origin = request.headers.get("origin");
    if (origin && new URL(origin).host !== request.headers.get("host")) {
      return Response.json({detail:"Origen no permitido."}, {status:403});
    }
    if (!request.headers.get("content-type")?.includes("application/json")) {
      return Response.json({detail:"Se requiere contenido JSON."}, {status:415});
    }
  }
  try {
    const upstream = await fetch(`${process.env.API_ORIGIN || "http://127.0.0.1:8000"}/api/${path}${request.nextUrl.search}`, {
      method:request.method, cache:"no-store", signal:AbortSignal.timeout(120_000),
      headers:{"content-type":"application/json"},
      ...(request.method !== "GET" ? {body: await request.text()} : {}),
    });
    const headers = new Headers({"Cache-Control":"no-store"});
    for (const name of ["content-type", "content-disposition"]) {
      const value=upstream.headers.get(name); if(value) headers.set(name,value);
    }
    return new Response(upstream.body, {status:upstream.status, headers});
  } catch {
    return Response.json({detail:"No se puede conectar con el motor de cálculo. Comprueba Docker Desktop y reintenta."}, {status:503});
  }
}
export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
