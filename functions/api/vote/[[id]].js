export async function onRequestPost(context) {
  const { request, env, params } = context;
  const id = params.id; // from [[id]].js
  
  if (!env.SCOUT_VOTES) {
      return new Response("KV Binding SCOUT_VOTES not found", { status: 500 });
  }
  
  try {
      const formData = await request.formData();
      const voteValue = formData.get('vote');
      
      if (!id || !voteValue) {
        return new Response("Missing parameters", { status: 400 });
      }
      
      const key = `vote_${id}_${Date.now()}`;
      const data = JSON.stringify({
        opportunity_id: parseInt(id[0]),
        vote: parseInt(voteValue),
        timestamp: new Date().toISOString()
      });
      
      // Store in KV
      await env.SCOUT_VOTES.put(key, data);
      
      return new Response(JSON.stringify({ status: "success" }), {
        headers: { "Content-Type": "application/json" }
      });
  } catch (error) {
      return new Response(`Error: ${error.message}`, { status: 500 });
  }
}
