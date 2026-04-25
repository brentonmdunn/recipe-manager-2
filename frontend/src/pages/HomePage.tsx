import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Filter, Pencil, Plus, X } from "lucide-react";
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { createTag, deleteTag, listRecipes, listTags } from "../api/recipes";
import RecipeCard from "../components/recipe/RecipeCard";
import { useAuth } from "../contexts/AuthContext";

export default function HomePage() {
  const [searchParams] = useSearchParams();
  const search = searchParams.get("search") ?? undefined;
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const isAdmin = user?.is_admin ?? false;
  const [page, setPage] = useState(1);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showFavorites, setShowFavorites] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [editTags, setEditTags] = useState(false);
  const [newTagName, setNewTagName] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");

  const { data, isLoading } = useQuery({
    queryKey: [
      "recipes",
      page,
      search,
      selectedTags,
      showFavorites,
      sortBy,
      sortOrder,
    ],
    queryFn: () =>
      listRecipes({
        page,
        search,
        tag_ids: selectedTags.length > 0 ? selectedTags : undefined,
        is_favorite: showFavorites ? true : undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      }),
  });

  const { data: tags } = useQuery({
    queryKey: ["tags"],
    queryFn: listTags,
  });

  const toggleTag = (tagId: string) => {
    setSelectedTags((prev) =>
      prev.includes(tagId) ? prev.filter((t) => t !== tagId) : [...prev, tagId]
    );
    setPage(1);
  };

  const clearFilters = () => {
    setSelectedTags([]);
    setShowFavorites(false);
    setPage(1);
  };

  const handleCreateTag = async () => {
    const name = newTagName.trim();
    if (!name) return;
    await createTag(name);
    setNewTagName("");
    queryClient.invalidateQueries({ queryKey: ["tags"] });
  };

  const handleDeleteTag = async (tagId: string, tagName: string) => {
    if (!window.confirm(`Delete tag "${tagName}"? This will remove it from all recipes.`)) {
      return;
    }
    await deleteTag(tagId);
    setSelectedTags((prev) => prev.filter((t) => t !== tagId));
    queryClient.invalidateQueries({ queryKey: ["tags"] });
    queryClient.invalidateQueries({ queryKey: ["recipes"] });
  };

  const hasFilters = selectedTags.length > 0 || showFavorites;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          {search ? `Results for "${search}"` : "Recipes"}
        </h1>
        <div className="flex items-center gap-2">
          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [by, order] = e.target.value.split("-");
              setSortBy(by);
              setSortOrder(order);
            }}
            className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="created_at-desc">Newest</option>
            <option value="created_at-asc">Oldest</option>
            <option value="title-asc">A–Z</option>
            <option value="title-desc">Z–A</option>
            <option value="rating-desc">Highest Rated</option>
            <option value="cook_time_minutes-asc">Quickest</option>
          </select>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center gap-1 px-3 py-2 border rounded-lg text-sm transition-colors ${
              showFilters || hasFilters
                ? "border-[var(--color-primary)] text-[var(--color-primary)] bg-orange-50"
                : "border-gray-300 text-gray-600 hover:bg-gray-50"
            }`}
          >
            <Filter className="w-4 h-4" />
            Filters
            {hasFilters && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  clearFilters();
                }}
                className="ml-1"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </button>
        </div>
      </div>

      {((tags && tags.length > 0) || isAdmin) && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Tags</span>
            {isAdmin && (
              <button
                type="button"
                onClick={() => setEditTags((prev) => !prev)}
                className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded ${
                  editTags
                    ? "bg-[var(--color-primary)] text-white"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Pencil className="w-3 h-3" />
                {editTags ? "Done" : "Edit tags"}
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {tags?.map((tag) =>
              editTags && isAdmin ? (
                <div
                  key={tag.id}
                  className="inline-flex items-center gap-1 bg-gray-100 rounded-full"
                >
                  <span className="pl-3 pr-1 py-1 text-sm text-gray-700">
                    {tag.name}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleDeleteTag(tag.id, tag.name)}
                    className="pr-2 pl-1 py-1 text-gray-400 hover:text-red-600"
                    title={`Delete "${tag.name}" tag`}
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ) : (
                <button
                  key={tag.id}
                  onClick={() => toggleTag(tag.id)}
                  className={`px-3 py-1 rounded-full text-sm ${
                    selectedTags.includes(tag.id)
                      ? "bg-[var(--color-primary)] text-white"
                      : "bg-orange-50 text-[var(--color-primary)] hover:bg-orange-100"
                  }`}
                >
                  {tag.name}
                </button>
              )
            )}
          </div>
          {editTags && isAdmin && (
            <div className="flex gap-2 mt-3">
              <input
                type="text"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleCreateTag();
                  }
                }}
                placeholder="New tag name..."
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
              <button
                type="button"
                onClick={handleCreateTag}
                disabled={!newTagName.trim()}
                className="inline-flex items-center gap-1 px-3 py-2 bg-[var(--color-primary)] text-white rounded-lg text-sm hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Plus className="w-4 h-4" /> Add
              </button>
            </div>
          )}
        </div>
      )}

      {showFilters && (
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6 space-y-4">
          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showFavorites}
                onChange={(e) => {
                  setShowFavorites(e.target.checked);
                  setPage(1);
                }}
                className="rounded border-gray-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
              />
              <span className="text-sm text-gray-700">Favorites only</span>
            </label>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="bg-white rounded-xl border border-gray-100 overflow-hidden animate-pulse"
            >
              <div className="aspect-video bg-gray-200" />
              <div className="p-4 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4" />
                <div className="h-3 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.items.map((recipe) => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>

          {data.pages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              {Array.from({ length: data.pages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`px-3 py-1 rounded text-sm ${
                    p === page
                      ? "bg-[var(--color-primary)] text-white"
                      : "bg-white border border-gray-300 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-16">
          <p className="text-4xl mb-4">🍽️</p>
          <p className="text-gray-500 text-lg">No recipes found</p>
          <p className="text-gray-400 text-sm mt-1">
            {search
              ? "Try a different search term"
              : "Add your first recipe to get started"}
          </p>
        </div>
      )}
    </div>
  );
}
