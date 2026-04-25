import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  createRecipe,
  getRecipe,
  listCategories,
  listTags,
  updateRecipe,
  uploadImage,
} from "../api/recipes";
import type { RecipeCreateData } from "../api/types";
import { useAuth } from "../contexts/AuthContext";

interface IngredientForm {
  name: string;
  quantity: string;
  unit: string;
  notes: string;
  group_name: string;
}

interface StepForm {
  instruction: string;
}

export default function RecipeEditPage() {
  const { id } = useParams<{ id: string }>();
  const isEditing = !!id;
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [prepTime, setPrepTime] = useState("");
  const [cookTime, setCookTime] = useState("");
  const [servings, setServings] = useState("");
  const [servingsUnit, setServingsUnit] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [isPublic, setIsPublic] = useState(true);
  const [categoryId, setCategoryId] = useState("");
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>([]);
  const [ingredients, setIngredients] = useState<IngredientForm[]>([
    { name: "", quantity: "", unit: "", notes: "", group_name: "" },
  ]);
  const [steps, setSteps] = useState<StepForm[]>([{ instruction: "" }]);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [error, setError] = useState("");

  const { data: existingRecipe } = useQuery({
    queryKey: ["recipe-edit", id],
    queryFn: () => getRecipe(id!),
    enabled: isEditing,
  });

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: listCategories,
  });

  const { data: tags } = useQuery({
    queryKey: ["tags"],
    queryFn: listTags,
  });

  useEffect(() => {
    if (existingRecipe) {
      setTitle(existingRecipe.title);
      setDescription(existingRecipe.description ?? "");
      setPrepTime(existingRecipe.prep_time_minutes?.toString() ?? "");
      setCookTime(existingRecipe.cook_time_minutes?.toString() ?? "");
      setServings(existingRecipe.servings?.toString() ?? "");
      setServingsUnit(existingRecipe.servings_unit ?? "");
      setSourceUrl(existingRecipe.source_url ?? "");
      setIsPublic(existingRecipe.is_public);
      setCategoryId(existingRecipe.category?.id ?? "");
      setSelectedTagIds(existingRecipe.tags.map((t) => t.id));
      setIngredients(
        existingRecipe.ingredients.length > 0
          ? existingRecipe.ingredients.map((ing) => ({
              name: ing.name,
              quantity: ing.quantity?.toString() ?? "",
              unit: ing.unit ?? "",
              notes: ing.notes ?? "",
              group_name: ing.group_name ?? "",
            }))
          : [{ name: "", quantity: "", unit: "", notes: "", group_name: "" }]
      );
      setSteps(
        existingRecipe.steps.length > 0
          ? existingRecipe.steps.map((s) => ({ instruction: s.instruction }))
          : [{ instruction: "" }]
      );
    }
  }, [existingRecipe]);

  const mutation = useMutation({
    mutationFn: async (data: RecipeCreateData) => {
      let recipe;
      if (isEditing) {
        recipe = await updateRecipe(id!, data);
      } else {
        recipe = await createRecipe(data);
      }
      if (imageFile) {
        await uploadImage(recipe.id, imageFile, true);
      }
      return recipe;
    },
    onSuccess: (recipe) => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      queryClient.invalidateQueries({ queryKey: ["recipe", recipe.slug] });
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

    const filteredIngredients = ingredients
      .filter((i) => i.name.trim())
      .map((i, idx) => ({
        name: i.name.trim(),
        quantity: i.quantity ? parseFloat(i.quantity) : undefined,
        unit: i.unit || undefined,
        notes: i.notes || undefined,
        group_name: i.group_name || undefined,
        position: idx,
      }));

    const filteredSteps = steps
      .filter((s) => s.instruction.trim())
      .map((s, idx) => ({
        step_number: idx + 1,
        instruction: s.instruction.trim(),
      }));

    mutation.mutate({
      title,
      description: description || undefined,
      prep_time_minutes: prepTime ? parseInt(prepTime) : undefined,
      cook_time_minutes: cookTime ? parseInt(cookTime) : undefined,
      servings: servings ? parseInt(servings) : undefined,
      servings_unit: servingsUnit || undefined,
      source_url: sourceUrl || undefined,
      is_public: isPublic,
      category_id: categoryId || undefined,
      tag_ids: selectedTagIds,
      ingredients: filteredIngredients,
      steps: filteredSteps,
    });
  };

  const addIngredient = () => {
    setIngredients([
      ...ingredients,
      { name: "", quantity: "", unit: "", notes: "", group_name: "" },
    ]);
  };

  const removeIngredient = (idx: number) => {
    setIngredients(ingredients.filter((_, i) => i !== idx));
  };

  const updateIngredient = (
    idx: number,
    field: keyof IngredientForm,
    value: string
  ) => {
    const updated = [...ingredients];
    updated[idx] = { ...updated[idx], [field]: value };
    setIngredients(updated);
  };

  const addStep = () => {
    setSteps([...steps, { instruction: "" }]);
  };

  const removeStep = (idx: number) => {
    setSteps(steps.filter((_, i) => i !== idx));
  };

  const toggleTag = (tagId: string) => {
    setSelectedTagIds((prev) =>
      prev.includes(tagId) ? prev.filter((t) => t !== tagId) : [...prev, tagId]
    );
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">
        {isEditing ? "Edit Recipe" : "New Recipe"}
      </h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Basic Info</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prep (min)
              </label>
              <input
                type="number"
                value={prepTime}
                onChange={(e) => setPrepTime(e.target.value)}
                min="0"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cook (min)
              </label>
              <input
                type="number"
                value={cookTime}
                onChange={(e) => setCookTime(e.target.value)}
                min="0"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Servings
              </label>
              <input
                type="number"
                value={servings}
                onChange={(e) => setServings(e.target.value)}
                min="1"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unit
              </label>
              <input
                type="text"
                value={servingsUnit}
                onChange={(e) => setServingsUnit(e.target.value)}
                placeholder="servings"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Source URL
            </label>
            <input
              type="url"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Image
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setImageFile(e.target.files?.[0] ?? null)}
              className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-orange-50 file:text-[var(--color-primary)] hover:file:bg-orange-100"
            />
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isPublic}
                onChange={(e) => setIsPublic(e.target.checked)}
                className="rounded border-gray-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
              />
              <span className="text-sm text-gray-700">Public recipe</span>
            </label>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Category & Tags</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              <option value="">None</option>
              {categories?.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          {tags && tags.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags
              </label>
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() => toggleTag(tag.id)}
                    className={`px-3 py-1 rounded-full text-sm ${
                      selectedTagIds.includes(tag.id)
                        ? "bg-[var(--color-primary)] text-white"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                  >
                    {tag.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Ingredients</h2>
            <button
              type="button"
              onClick={addIngredient}
              className="inline-flex items-center gap-1 text-sm text-[var(--color-primary)] hover:underline"
            >
              <Plus className="w-4 h-4" /> Add
            </button>
          </div>

          {ingredients.map((ing, idx) => (
            <div key={idx} className="flex gap-2 items-start">
              <input
                type="text"
                placeholder="Qty"
                value={ing.quantity}
                onChange={(e) => updateIngredient(idx, "quantity", e.target.value)}
                className="w-16 border border-gray-300 rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
              <input
                type="text"
                placeholder="Unit"
                value={ing.unit}
                onChange={(e) => updateIngredient(idx, "unit", e.target.value)}
                className="w-20 border border-gray-300 rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
              <input
                type="text"
                placeholder="Ingredient name"
                value={ing.name}
                onChange={(e) => updateIngredient(idx, "name", e.target.value)}
                className="flex-1 border border-gray-300 rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
              <input
                type="text"
                placeholder="Notes"
                value={ing.notes}
                onChange={(e) => updateIngredient(idx, "notes", e.target.value)}
                className="w-28 border border-gray-300 rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
              {ingredients.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeIngredient(idx)}
                  className="p-2 text-gray-400 hover:text-red-500"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Instructions</h2>
            <button
              type="button"
              onClick={addStep}
              className="inline-flex items-center gap-1 text-sm text-[var(--color-primary)] hover:underline"
            >
              <Plus className="w-4 h-4" /> Add Step
            </button>
          </div>

          {steps.map((step, idx) => (
            <div key={idx} className="flex gap-3 items-start">
              <span className="flex-shrink-0 w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center text-sm font-medium text-gray-500 mt-1">
                {idx + 1}
              </span>
              <textarea
                value={step.instruction}
                onChange={(e) => {
                  const updated = [...steps];
                  updated[idx] = { instruction: e.target.value };
                  setSteps(updated);
                }}
                rows={2}
                placeholder={`Step ${idx + 1}`}
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
              {steps.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeStep(idx)}
                  className="p-2 text-gray-400 hover:text-red-500"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={mutation.isPending || !title.trim()}
            className="px-6 py-2 bg-[var(--color-primary)] text-white rounded-lg text-sm font-medium hover:bg-[var(--color-primary-dark)] disabled:opacity-50 transition-colors"
          >
            {mutation.isPending
              ? "Saving..."
              : isEditing
                ? "Update Recipe"
                : "Create Recipe"}
          </button>
        </div>
      </form>
    </div>
  );
}
