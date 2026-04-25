import type { Ingredient } from "../../api/types";

interface IngredientListProps {
  ingredients: Ingredient[];
  scaleFactor: number;
}

function formatQuantity(qty: number): string {
  if (qty === Math.floor(qty)) return String(qty);

  const fractions: [number, string][] = [
    [0.125, "⅛"],
    [0.25, "¼"],
    [0.333, "⅓"],
    [0.5, "½"],
    [0.667, "⅔"],
    [0.75, "¾"],
  ];

  const whole = Math.floor(qty);
  const frac = qty - whole;

  for (const [val, symbol] of fractions) {
    if (Math.abs(frac - val) < 0.05) {
      return whole > 0 ? `${whole} ${symbol}` : symbol;
    }
  }

  return qty.toFixed(1).replace(/\.0$/, "");
}

export default function IngredientList({
  ingredients,
  scaleFactor,
}: IngredientListProps) {
  const groups = new Map<string, Ingredient[]>();
  for (const ing of ingredients) {
    const key = ing.group_name ?? "";
    const list = groups.get(key) ?? [];
    list.push(ing);
    groups.set(key, list);
  }

  return (
    <div className="space-y-4">
      {Array.from(groups.entries()).map(([group, items]) => (
        <div key={group}>
          {group && (
            <h4 className="font-medium text-gray-700 mb-2">{group}</h4>
          )}
          <ul className="space-y-1.5">
            {items.map((ing) => (
              <li key={ing.id} className="flex items-start gap-2 text-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)] mt-1.5 flex-shrink-0" />
                <span>
                  {ing.quantity && (
                    <span className="font-medium">
                      {formatQuantity(ing.quantity * scaleFactor)}
                    </span>
                  )}{" "}
                  {ing.unit && <span>{ing.unit}</span>} {ing.name}
                  {ing.notes && (
                    <span className="text-gray-400"> ({ing.notes})</span>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
