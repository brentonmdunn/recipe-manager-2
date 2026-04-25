import { useQuery } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getSetupStatus, register } from "../api/auth";
import { useAuth } from "../contexts/AuthContext";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const { data: setupStatus, isLoading: isCheckingSetup } = useQuery({
    queryKey: ["setup-status"],
    queryFn: getSetupStatus,
  });

  const needsSetup = setupStatus?.needs_setup ?? false;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (needsSetup) {
      if (password !== confirmPassword) {
        setError("Passwords do not match");
        return;
      }
      if (password.length < 8) {
        setError("Password must be at least 8 characters");
        return;
      }
    }

    setIsLoading(true);

    try {
      if (needsSetup) {
        await register(username, password);
      }
      await login(username, password);
      navigate("/");
    } catch {
      setError(
        needsSetup
          ? "Failed to create account"
          : "Invalid username or password"
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (isCheckingSetup) {
    return (
      <div className="flex justify-center mt-16">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="max-w-sm mx-auto mt-16">
      <h1 className="text-2xl font-bold text-center mb-2">
        {needsSetup ? "Create Admin Account" : "Login"}
      </h1>
      {needsSetup && (
        <p className="text-center text-sm text-gray-500 mb-6">
          Set up your admin account to get started.
        </p>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-xl border border-gray-200 p-6 space-y-4"
      >
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoFocus
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
        </div>

        {needsSetup && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confirm Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2 bg-[var(--color-primary)] text-white rounded-lg font-medium hover:bg-[var(--color-primary-dark)] disabled:opacity-50 transition-colors"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin mx-auto" />
          ) : needsSetup ? (
            "Create Account"
          ) : (
            "Sign In"
          )}
        </button>
      </form>
    </div>
  );
}
