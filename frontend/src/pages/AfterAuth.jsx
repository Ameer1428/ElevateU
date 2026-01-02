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
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
        const response = await fetch(`${API_BASE_URL}/api/users`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            clerkId: user.id,
            email: user.primaryEmailAddress?.emailAddress || null,
            name: fullName,
          }),
        });

        const userData = await response.json();

        // Check if user is admin (only from backend role - no fallbacks!)
        const isAdmin = userData.role === 'admin';

        // Conditional navigation based on user role
        if (isAdmin) {
          navigate("/admin");
        } else {
          navigate("/dashboard");
        }
      } catch (err) {
        console.error("Error syncing user:", err);
        navigate("/dashboard"); // fallback
      }
    })();
  }, [isLoaded, isSignedIn, user, getToken, navigate]);

  return null; // no UI — just redirects
}
