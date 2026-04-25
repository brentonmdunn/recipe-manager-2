import { Clock, Heart, Star } from "lucide-react";
import { Link } from "react-router-dom";
import type { RecipeListItem } from "../../api/types";

interface RecipeCardProps {
  recipe: RecipeListItem;
}

export default function RecipeCard({ recipe }: RecipeCardProps) {
  const computedTime =
    (recipe.prep_time_minutes ?? 0) + (recipe.cook_time_minutes ?? 0);
  const totalTime =
    recipe.total_time_minutes ?? (computedTime > 0 ? computedTime : null);

  return (
    <Link
      to={`/recipes/${recipe.slug}`}
      className="group block bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow"
    >
      <div className="aspect-video bg-gray-100 relative overflow-hidden">
        {recipe.primary_image ? (
          <img
            src={`/uploads/${recipe.primary_image.file_path}`}
            alt={recipe.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-300">
            <span className="text-4xl">🍳</span>
          </div>
        )}
        {recipe.is_favorite && (
          <div className="absolute top-2 right-2 bg-white/90 rounded-full p-1.5">
            <Heart className="w-4 h-4 fill-red-500 text-red-500" />
          </div>
        )}
      </div>

      <div className="p-4">
        <h3 className="font-semibold text-gray-900 group-hover:text-[var(--color-primary)] transition-colors line-clamp-1">
          {recipe.title}
        </h3>

        {recipe.description && (
          <p className="text-sm text-gray-500 mt-1 line-clamp-2">
            {recipe.description}
          </p>
        )}

        <div className="flex items-center gap-3 mt-3 text-sm text-gray-500">
          {totalTime && (
            <span className="inline-flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {totalTime}m
            </span>
          )}
          {recipe.rating && (
            <span className="inline-flex items-center gap-1">
              <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
              {recipe.rating}
            </span>
          )}
        </div>

        {recipe.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {recipe.tags.slice(0, 3).map((tag) => (
              <span
                key={tag.id}
                className="bg-orange-50 text-[var(--color-primary)] px-2 py-0.5 rounded text-xs"
              >
                {tag.name}
              </span>
            ))}
            {recipe.tags.length > 3 && (
              <span className="text-xs text-gray-400">
                +{recipe.tags.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </Link>
  );
}
