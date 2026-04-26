import { BookOpen, LogIn, LogOut, Plus, Search, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export default function Header() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const urlSearch = location.pathname === "/" ? searchParams.get("search") ?? "" : "";
  const [search, setSearch] = useState(urlSearch);

  useEffect(() => {
    setSearch(urlSearch);
  }, [urlSearch]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = search.trim();
    navigate(trimmed ? `/?search=${encodeURIComponent(trimmed)}` : "/");
  };

  const clearSearch = () => {
    setSearch("");
    if (urlSearch) {
      navigate("/");
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 text-[var(--color-primary)] font-bold text-xl">
            <BookOpen className="w-6 h-6" />
            <span className="hidden sm:inline">Recipe Manager</span>
          </Link>

          <form onSubmit={handleSearch} className="flex-1 max-w-md mx-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search recipes by title, description, or tag..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-9 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
              />
              {search && (
                <button
                  type="button"
                  onClick={clearSearch}
                  aria-label="Clear search"
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </form>

          <nav className="flex items-center gap-2">
            {isAuthenticated ? (
              <>
                <Link
                  to="/recipes/new"
                  className="inline-flex items-center gap-1 px-3 py-2 bg-[var(--color-primary)] text-white rounded-lg text-sm font-medium hover:bg-[var(--color-primary-dark)] transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span className="hidden sm:inline">Add Recipe</span>
                </Link>
                <Link
                  to="/import"
                  className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Import
                </Link>
                <button
                  onClick={logout}
                  className="inline-flex items-center gap-1 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-1 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                <LogIn className="w-4 h-4" />
                Login
              </Link>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
