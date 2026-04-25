import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  Clock,
  Edit,
  ExternalLink,
  Heart,
  Star,
  Trash2,
  Users,
} from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  deleteRecipe,
  getRecipe,
  setRating,
  toggleFavorite,
} from "../api/recipes";
import IngredientList from "../components/recipe/IngredientList";
import RecipeScaler from "../components/recipe/RecipeScaler";
import { useAuth } from "../contexts/AuthContext";

export default function RecipeDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: recipe, isLoading } = useQuery({
    queryKey: ["recipe", slug],
    queryFn: () => getRecipe(slug!),
    enabled: !!slug,
  });

  const [currentServings, setCurrentServings] = useState<number | null>(null);

  const favMutation = useMutation({
    mutationFn: () => toggleFavorite(recipe!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recipe", slug] });
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
    },
  });

  const ratingMutation = useMutation({
    mutationFn: (rating: number | null) => setRating(recipe!.id, rating),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recipe", slug] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteRecipe(recipe!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      navigate("/");
    },
  });

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/3" />
        <div className="h-64 bg-gray-200 rounded" />
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="text-center py-16">
        <p className="text-4xl mb-4">😕</p>
        <p className="text-gray-500 text-lg">Recipe not found</p>
        <Link to="/" className="text-[var(--color-primary)] hover:underline mt-2 inline-block">
          Back to recipes
        </Link>
      </div>
    );
  }

  const servings = recipe.servings ?? 1;
  const activeServings = currentServings ?? servings;
  const scaleFactor = activeServings / servings;

  const computedTime =
    (recipe.prep_time_minutes ?? 0) + (recipe.cook_time_minutes ?? 0);
  const totalTime =
    recipe.total_time_minutes ?? (computedTime > 0 ? computedTime : null);

  const primaryImage = recipe.images.find((i) => i.is_primary) ?? recipe.images[0];

  return (
    <div>
      <Link
        to="/"
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to recipes
      </Link>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {primaryImage && (
          <div className="aspect-video max-h-96 overflow-hidden">
            <img
              src={`/uploads/${primaryImage.file_path}`}
              alt={recipe.title}
              className="w-full h-full object-cover"
            />
          </div>
        )}

        <div className="p-6 lg:p-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {recipe.title}
              </h1>
              {recipe.description && (
                <p className="text-gray-600 mt-2">{recipe.description}</p>
              )}
            </div>

            {isAuthenticated && (
              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  onClick={() => favMutation.mutate()}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                  title="Toggle favorite"
                >
                  <Heart
                    className={`w-5 h-5 ${
                      recipe.is_favorite
                        ? "fill-red-500 text-red-500"
                        : "text-gray-400"
                    }`}
                  />
                </button>
                <Link
                  to={`/recipes/${recipe.slug}/edit`}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                  title="Edit recipe"
                >
                  <Edit className="w-5 h-5 text-gray-400" />
                </Link>
                <button
                  onClick={() => {
                    if (confirm("Delete this recipe?")) {
                      deleteMutation.mutate();
                    }
                  }}
                  className="p-2 rounded-lg hover:bg-red-50 transition-colors"
                  title="Delete recipe"
                >
                  <Trash2 className="w-5 h-5 text-gray-400 hover:text-red-500" />
                </button>
              </div>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-4 mt-4 text-sm text-gray-500">
            {recipe.prep_time_minutes && (
              <span className="inline-flex items-center gap-1">
                <Clock className="w-4 h-4" />
                Prep: {recipe.prep_time_minutes}m
              </span>
            )}
            {recipe.cook_time_minutes && (
              <span className="inline-flex items-center gap-1">
                <Clock className="w-4 h-4" />
                Cook: {recipe.cook_time_minutes}m
              </span>
            )}
            {totalTime && (
              <span className="inline-flex items-center gap-1 font-medium text-gray-700">
                <Clock className="w-4 h-4" />
                Total: {totalTime}m
              </span>
            )}
            {recipe.servings && (
              <span className="inline-flex items-center gap-1">
                <Users className="w-4 h-4" />
                {recipe.servings} {recipe.servings_unit ?? "servings"}
              </span>
            )}
            {recipe.source_url && (
              <a
                href={recipe.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-[var(--color-primary)] hover:underline"
              >
                <ExternalLink className="w-4 h-4" />
                Source
              </a>
            )}
          </div>

          {isAuthenticated && (
            <div className="flex items-center gap-1 mt-3">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() =>
                    ratingMutation.mutate(
                      recipe.rating === star ? null : star
                    )
                  }
                  className="p-0.5"
                >
                  <Star
                    className={`w-5 h-5 ${
                      star <= (recipe.rating ?? 0)
                        ? "fill-amber-400 text-amber-400"
                        : "text-gray-300"
                    }`}
                  />
                </button>
              ))}
            </div>
          )}

          {recipe.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-4">
              {recipe.tags.map((tag) => (
                <span
                  key={tag.id}
                  className="bg-orange-50 text-[var(--color-primary)] px-3 py-1 rounded-full text-sm"
                >
                  {tag.name}
                </span>
              ))}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
            <div className="lg:col-span-1">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Ingredients</h2>
              </div>
              <div className="mb-4">
                <RecipeScaler
                  originalServings={servings}
                  currentServings={activeServings}
                  onChange={setCurrentServings}
                  unit={recipe.servings_unit ?? (recipe.servings ? "servings" : "×")}
                />
              </div>
              <IngredientList
                ingredients={recipe.ingredients}
                scaleFactor={scaleFactor}
              />
            </div>

            <div className="lg:col-span-2">
              <h2 className="text-xl font-semibold mb-4">Instructions</h2>
              <ol className="space-y-4">
                {recipe.steps.map((step) => (
                  <li key={step.id} className="flex gap-4">
                    <span className="flex-shrink-0 w-7 h-7 bg-[var(--color-primary)] text-white rounded-full flex items-center justify-center text-sm font-medium">
                      {step.step_number}
                    </span>
                    <p className="text-gray-700 leading-relaxed pt-0.5">
                      {step.instruction}
                    </p>
                  </li>
                ))}
              </ol>
            </div>
          </div>

          {recipe.nutrition_info && (() => {
            let parsed: Record<string, string> | null = null;
            try {
              parsed = JSON.parse(recipe.nutrition_info);
            } catch {
              // not valid JSON
            }
            if (!parsed || typeof parsed !== "object") {
              return (
                <div className="mt-8 pt-6 border-t border-gray-200">
                  <h2 className="text-xl font-semibold mb-3">Nutrition</h2>
                  <p className="text-sm text-gray-600">{recipe.nutrition_info}</p>
                </div>
              );
            }
            const labelMap: Record<string, string> = {
              calories: "Calories",
              fatContent: "Fat",
              saturatedFatContent: "Saturated Fat",
              transFatContent: "Trans Fat",
              unsaturatedFatContent: "Unsaturated Fat",
              cholesterolContent: "Cholesterol",
              sodiumContent: "Sodium",
              carbohydrateContent: "Carbohydrates",
              fiberContent: "Fiber",
              sugarContent: "Sugar",
              proteinContent: "Protein",
              servingSize: "Serving Size",
            };
            const entries = Object.entries(parsed).filter(([, v]) => v);
            if (entries.length === 0) return null;
            return (
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h2 className="text-xl font-semibold mb-3">Nutrition</h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {entries.map(([key, value]) => (
                    <div
                      key={key}
                      className="bg-gray-50 rounded-lg p-3 text-center"
                    >
                      <p className="text-sm text-gray-500">
                        {labelMap[key] ?? key.replace(/Content$/i, "").replace(/([A-Z])/g, " $1").trim()}
                      </p>
                      <p className="text-base font-medium text-gray-800">
                        {value}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            );
          })()}
        </div>
      </div>
    </div>
  );
}
