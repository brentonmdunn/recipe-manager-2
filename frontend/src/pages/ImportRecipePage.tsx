import { useMutation } from "@tanstack/react-query";
import { Download, Loader2 } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { importRecipe } from "../api/recipes";
import { useAuth } from "../contexts/AuthContext";

export default function ImportRecipePage() {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const mutation = useMutation({
    mutationFn: (recipeUrl: string) => importRecipe(recipeUrl),
    onSuccess: (recipe) => {
      navigate(`/recipes/${recipe.slug}`);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  if (!isAuthenticated) {
    navigate("/login");
    return null;
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (url.trim()) {
      mutation.mutate(url.trim());
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Import Recipe</h1>
      <p className="text-gray-500 mb-6">
        Paste a URL from a recipe website and we'll import it automatically.
      </p>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
          Failed to import recipe. Make sure the URL is a valid recipe page.
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Recipe URL
          </label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.allrecipes.com/recipe/..."
            required
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
          <p className="text-xs text-gray-400 mt-2">
            Supports most popular recipe websites (AllRecipes, Food Network,
            BBC Good Food, etc.)
          </p>
        </div>

        <button
          type="submit"
          disabled={mutation.isPending || !url.trim()}
          className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-[var(--color-primary)] text-white rounded-lg font-medium hover:bg-[var(--color-primary-dark)] disabled:opacity-50 transition-colors"
        >
          {mutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Importing...
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              Import Recipe
            </>
          )}
        </button>
      </form>
    </div>
  );
}
