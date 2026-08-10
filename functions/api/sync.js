export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const secret = url.searchParams.get("secret");
  
  if (!env.SYNC_SECRET || secret !== env.SYNC_SECRET) {
    return new Response("Unauthorized", { status: 401 });
  }
  
  if (!env.SCOUT_VOTES) {
      return new Response("KV Binding SCOUT_VOTES not found", { status: 500 });
  }
  
  try {
      const votes = [];
      const list = await env.SCOUT_VOTES.list({ prefix: "vote_" });
      
      for (const key of list.keys) {
        const value = await env.SCOUT_VOTES.get(key.name);
        if (value) {
          votes.push(JSON.parse(value));
          // Delete after reading to prevent duplicate processing
          await env.SCOUT_VOTES.delete(key.name);
        }
      }
      
      return new Response(JSON.stringify({ votes }), {
        headers: { "Content-Type": "application/json" }
      });
  } catch (error) {
      return new Response(`Error: ${error.message}`, { status: 500 });
  }
}
