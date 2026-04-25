import api from "./client";
import type {
  PaginatedResponse,
  Recipe,
  RecipeCreateData,
  Tag,
} from "./types";

interface ListRecipesParams {
  page?: number;
  per_page?: number;
  search?: string;
  tag_ids?: string[];
  is_favorite?: boolean;
  min_rating?: number;
  max_cook_time?: number;
  sort_by?: string;
  sort_order?: string;
}

export async function listRecipes(
  params: ListRecipesParams = {}
): Promise<PaginatedResponse> {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set("page", String(params.page));
  if (params.per_page) searchParams.set("per_page", String(params.per_page));
  if (params.search) searchParams.set("search", params.search);
  if (params.is_favorite !== undefined)
    searchParams.set("is_favorite", String(params.is_favorite));
  if (params.min_rating) searchParams.set("min_rating", String(params.min_rating));
  if (params.max_cook_time)
    searchParams.set("max_cook_time", String(params.max_cook_time));
  if (params.sort_by) searchParams.set("sort_by", params.sort_by);
  if (params.sort_order) searchParams.set("sort_order", params.sort_order);
  if (params.tag_ids) {
    params.tag_ids.forEach((id) => searchParams.append("tag_ids", id));
  }

  return api.get("recipes", { searchParams }).json();
}

export async function getRecipe(slug: string): Promise<Recipe> {
  return api.get(`recipes/${slug}`).json();
}

export async function createRecipe(data: RecipeCreateData): Promise<Recipe> {
  return api.post("recipes", { json: data }).json();
}

export async function updateRecipe(
  id: string,
  data: Partial<RecipeCreateData>
): Promise<Recipe> {
  return api.put(`recipes/${id}`, { json: data }).json();
}

export async function deleteRecipe(id: string): Promise<void> {
  await api.delete(`recipes/${id}`);
}

export async function importRecipe(url: string): Promise<Recipe> {
  return api.post("recipes/import", { json: { url } }).json();
}

export async function toggleFavorite(id: string): Promise<Recipe> {
  return api.patch(`recipes/${id}/favorite`).json();
}

export async function setRating(
  id: string,
  rating: number | null
): Promise<Recipe> {
  const searchParams = rating !== null ? { rating: String(rating) } : {};
  return api.patch(`recipes/${id}/rating`, { searchParams }).json();
}

export async function listTags(): Promise<Tag[]> {
  return api.get("tags").json();
}

export async function createTag(name: string): Promise<Tag> {
  return api.post("tags", { json: { name } }).json();
}

export async function deleteTag(id: string): Promise<void> {
  await api.delete(`tags/${id}`);
}

export async function uploadImage(
  recipeId: string,
  file: File,
  isPrimary: boolean = false
): Promise<void> {
  const formData = new FormData();
  formData.append("file", file);
  await api.post(`recipes/${recipeId}/images`, {
    body: formData,
    searchParams: { is_primary: String(isPrimary) },
  });
}
