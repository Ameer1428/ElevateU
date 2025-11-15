// AfterAuth.jsx
import { useEffect } from "react";
import { useUser, useAuth } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";

export default function AfterAuth() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { getToken } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;

    (async () => {
      const token = await getToken().catch(() => null);

      const fullName =
        user.fullName ||
        `${user.firstName ?? ""} ${user.lastName ?? ""}`.trim();

      try {
        // Create/sync user in backend
        await fetch("http://localhost:5000/api/users", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            id: user.id,
            email: user.primaryEmailAddress?.emailAddress || null,
            name: fullName,
          }),
        });

        // Normalize name for comparison
        const normalizedName = (fullName || "").toLowerCase();

        // Conditional navigation
        if (normalizedName === "admin") {
          navigate("/admin");
        } else {
          navigate("/browse");
        }
      } catch (err) {
        console.error("Error syncing user:", err);
        navigate("/browse"); // fallback
      }
    })();
  }, [isLoaded, isSignedIn, user, getToken, navigate]);

  return null; // no UI — just redirects
}
