export interface User {
  id: string;
  username: string;
  is_admin: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
}

export interface Ingredient {
  id: string;
  name: string;
  quantity: number | null;
  unit: string | null;
  notes: string | null;
  group_name: string | null;
  position: number;
}

export interface RecipeStep {
  id: string;
  step_number: number;
  instruction: string;
  image_id: string | null;
}

export interface RecipeImage {
  id: string;
  file_path: string;
  is_primary: boolean;
  alt_text: string | null;
  created_at: string;
}

export interface Recipe {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  prep_time_minutes: number | null;
  cook_time_minutes: number | null;
  total_time_minutes: number | null;
  servings: number | null;
  servings_unit: string | null;
  source_url: string | null;
  nutrition_info: string | null;
  is_public: boolean;
  is_favorite: boolean;
  rating: number | null;
  tags: Tag[];
  ingredients: Ingredient[];
  steps: RecipeStep[];
  images: RecipeImage[];
  created_at: string;
  updated_at: string;
}

export interface RecipeListItem {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  prep_time_minutes: number | null;
  cook_time_minutes: number | null;
  total_time_minutes: number | null;
  servings: number | null;
  is_public: boolean;
  is_favorite: boolean;
  rating: number | null;
  tags: Tag[];
  primary_image: RecipeImage | null;
  created_at: string;
}

export interface PaginatedResponse {
  items: RecipeListItem[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface ShareLink {
  id: string;
  token: string;
  recipe_id: string;
  created_at: string;
}

export interface RecipeCreateData {
  title: string;
  description?: string;
  prep_time_minutes?: number;
  cook_time_minutes?: number;
  total_time_minutes?: number;
  servings?: number;
  servings_unit?: string;
  source_url?: string;
  nutrition_info?: string;
  is_public?: boolean;
  tag_ids?: string[];
  ingredients?: {
    name: string;
    quantity?: number;
    unit?: string;
    notes?: string;
    group_name?: string;
    position: number;
  }[];
  steps?: {
    step_number: number;
    instruction: string;
  }[];
}
