import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="text-center py-16">
      <p className="text-6xl mb-4">404</p>
      <p className="text-gray-500 text-lg mb-4">Page not found</p>
      <Link
        to="/"
        className="text-[var(--color-primary)] hover:underline"
      >
        Back to recipes
      </Link>
    </div>
  );
}
