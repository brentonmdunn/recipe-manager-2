import ky from "ky";

const api = ky.create({
  prefix: "/api/v1",
  hooks: {
    beforeRequest: [
      ({ request }) => {
        const token = localStorage.getItem("access_token");
        if (token) {
          request.headers.set("Authorization", `Bearer ${token}`);
        }
      },
    ],
    afterResponse: [
      async ({ response }) => {
        if (response.status === 401) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          if (!window.location.pathname.startsWith("/login")) {
            window.location.href = "/login";
          }
        }
      },
    ],
  },
});

export default api;
