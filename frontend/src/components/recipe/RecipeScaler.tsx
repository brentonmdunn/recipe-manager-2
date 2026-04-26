import { Minus, Plus } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface RecipeScalerProps {
  originalServings: number;
  currentServings: number;
  onChange: (servings: number) => void;
  unit?: string;
}

function formatServings(value: number): string {
  return Number.isInteger(value) ? String(value) : String(Number(value.toFixed(2)));
}

export default function RecipeScaler({
  originalServings,
  currentServings,
  onChange,
  unit,
}: RecipeScalerProps) {
  const [draft, setDraft] = useState(formatServings(currentServings));
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (document.activeElement !== inputRef.current) {
      setDraft(formatServings(currentServings));
    }
  }, [currentServings]);

  const commit = () => {
    const parsed = parseFloat(draft);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      setDraft(formatServings(currentServings));
      return;
    }
    if (parsed !== currentServings) {
      onChange(parsed);
    } else {
      setDraft(formatServings(currentServings));
    }
  };

  return (
    <div className="inline-flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-1.5">
      <button
        onClick={() => onChange(Math.max(1, currentServings - 1))}
        className="p-1 rounded hover:bg-gray-200 transition-colors"
        aria-label="Decrease servings"
      >
        <Minus className="w-3.5 h-3.5" />
      </button>
      <label className="flex items-center gap-1 text-sm font-medium">
        <input
          ref={inputRef}
          type="number"
          inputMode="decimal"
          min="0"
          step="any"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={commit}
          onFocus={(e) => e.target.select()}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              (e.target as HTMLInputElement).blur();
            } else if (e.key === "Escape") {
              setDraft(formatServings(currentServings));
              (e.target as HTMLInputElement).blur();
            }
          }}
          aria-label="Servings"
          className="w-12 bg-transparent text-center rounded focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
        />
        <span>{unit ?? "servings"}</span>
      </label>
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
