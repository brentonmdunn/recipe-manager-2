import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Copy, Link, Trash2 } from "lucide-react";
import { useState } from "react";
import { createShareLink, deleteShareLink, listShareLinks } from "../../api/recipes";

interface SharePanelProps {
  recipeId: string;
}

export default function SharePanel({ recipeId }: SharePanelProps) {
  const queryClient = useQueryClient();
  const [copiedToken, setCopiedToken] = useState<string | null>(null);

  const { data: shareLinks = [] } = useQuery({
    queryKey: ["shareLinks", recipeId],
    queryFn: () => listShareLinks(recipeId),
  });

  const createMutation = useMutation({
    mutationFn: () => createShareLink(recipeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["shareLinks", recipeId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteShareLink(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["shareLinks", recipeId] });
    },
  });

  const getShareUrl = (token: string) => {
    return `${window.location.origin}/shared/${token}`;
  };

  const copyToClipboard = async (token: string) => {
    await navigator.clipboard.writeText(getShareUrl(token));
    setCopiedToken(token);
    setTimeout(() => setCopiedToken(null), 2000);
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 mt-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
          <Link className="w-4 h-4" />
          Share Links
        </h3>
        <button
          onClick={() => createMutation.mutate()}
          disabled={createMutation.isPending}
          className="text-sm px-3 py-1 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          {createMutation.isPending ? "Creating..." : "Create Link"}
        </button>
      </div>

      {shareLinks.length === 0 ? (
        <p className="text-sm text-gray-400">
          No share links yet. Create one to share this recipe with friends.
        </p>
      ) : (
        <ul className="space-y-2">
          {shareLinks.map((link) => (
            <li
              key={link.id}
              className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2 text-sm"
            >
              <span className="truncate flex-1 text-gray-600 font-mono text-xs">
                {getShareUrl(link.token)}
              </span>
              <button
                onClick={() => copyToClipboard(link.token)}
                className="p-1.5 rounded hover:bg-gray-200 transition-colors flex-shrink-0"
                title="Copy link"
              >
                {copiedToken === link.token ? (
                  <Check className="w-4 h-4 text-green-500" />
                ) : (
                  <Copy className="w-4 h-4 text-gray-400" />
                )}
              </button>
              <button
                onClick={() => deleteMutation.mutate(link.id)}
                disabled={deleteMutation.isPending}
                className="p-1.5 rounded hover:bg-red-50 transition-colors flex-shrink-0"
                title="Delete link"
              >
                <Trash2 className="w-4 h-4 text-gray-400 hover:text-red-500" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
