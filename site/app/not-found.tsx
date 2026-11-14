import Link from "next/link";

export default function NotFound() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-20 text-center">
      <h1 className="text-3xl font-bold mb-3">Page introuvable</h1>
      <p className="text-[color:var(--muted)] mb-6">
        Ce hackathon n&apos;existe pas (ou plus).
      </p>
      <Link
        href="/"
        className="inline-block px-4 py-2 rounded border border-[color:var(--border)] hover:border-[color:var(--accent)]"
      >
        Retour à l&apos;accueil
      </Link>
    </div>
  );
}
