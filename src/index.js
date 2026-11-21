const VERSION = "1.0.0";

export default {
  fetch(request, env) {
    const { pathname } = new URL(request.url);

    if (pathname === "/health") {
      return Response.json({ estado: "ok", ambiente: env.AMBIENTE, version: VERSION });
    }

    if (pathname === "/error") {
      throw new Error("Error simulado para pruebas");
    }

    return Response.json({
      mensaje: "Hola desde Cloudflare Workers",
      ambiente: env.AMBIENTE,
      version: VERSION,
    });
  },
};
