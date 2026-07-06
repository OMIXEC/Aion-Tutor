import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import postgres from "https://deno.land/x/postgresjs@v3.4.5/mod.js";

// Initialize Postgres client with the connection string built into the Edge Runtime
const sql = postgres(Deno.env.get("SUPABASE_DB_URL")!);

Deno.serve(async (req) => {
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }
  
  let payload;
  try {
    payload = await req.json();
  } catch (e) {
    return new Response('Invalid JSON payload', { status: 400 });
  }

  const { id, content } = payload.record || {};
  
  if (!id || !content) {
    return new Response('Invalid payload: missing id or content', { status: 400 });
  }

  // Generate embedding using Google Gemini API
  const apiKey = Deno.env.get("GEMINI_API_KEY");
  if (!apiKey) {
    console.error("Server configuration error: GEMINI_API_KEY missing");
    return new Response('Configuration error', { status: 500 });
  }

  try {
    console.log(`Generating embedding for message ${id}...`);
    const geminiRes = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "models/text-embedding-004",
          content: { parts: [{ text: content }] },
        })
      }
    );

    if (!geminiRes.ok) {
      const errText = await geminiRes.text();
      console.error("Gemini API error:", errText);
      return new Response(`Gemini API error`, { status: 502 });
    }

    const { embedding } = await geminiRes.json();
    if (!embedding || !embedding.values) {
      console.error("Invalid embedding structure returned from Gemini");
      return new Response('Invalid embedding returned', { status: 502 });
    }
    
    // Store in database
    await sql`
      update public.messages
      set embedding = ${JSON.stringify(embedding.values)}
      where id = ${id}
    `;

    console.log(`Successfully updated embedding for message ${id}`);
    return new Response(JSON.stringify({ success: true, id }), { 
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (err: any) {
    console.error("Execution error:", err);
    return new Response(`Internal Edge Function Error: ${err.message}`, { status: 500 });
  }
});
