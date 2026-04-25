import { Minus, Plus } from "lucide-react";

interface RecipeScalerProps {
  originalServings: number;
  currentServings: number;
  onChange: (servings: number) => void;
  unit?: string;
}

export default function RecipeScaler({
  originalServings,
  currentServings,
  onChange,
  unit,
}: RecipeScalerProps) {
  return (
    <div className="inline-flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-1.5">
      <button
        onClick={() => onChange(Math.max(1, currentServings - 1))}
        className="p-1 rounded hover:bg-gray-200 transition-colors"
        aria-label="Decrease servings"
      >
        <Minus className="w-3.5 h-3.5" />
      </button>
      <span className="text-sm font-medium min-w-[3rem] text-center">
        {currentServings} {unit ?? "servings"}
      </span>
      <button
        onClick={() => onChange(currentServings + 1)}
        className="p-1 rounded hover:bg-gray-200 transition-colors"
        aria-label="Increase servings"
      >
        <Plus className="w-3.5 h-3.5" />
      </button>
      {currentServings !== originalServings && (
        <button
          onClick={() => onChange(originalServings)}
          className="text-xs text-[var(--color-primary)] hover:underline ml-1"
        >
          Reset
        </button>
      )}
    </div>
  );
}
