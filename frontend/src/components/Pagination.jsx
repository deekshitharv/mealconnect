import Button from "./Button";

export default function Pagination({ page, totalPages, onChange }) {
  if (totalPages <= 1) return null;
  return (
    <nav className="pagination" aria-label="Pagination">
      <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => onChange(page - 1)}>
        Previous
      </Button>
      <span className="muted">Page {page} of {totalPages}</span>
      <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => onChange(page + 1)}>
        Next
      </Button>
    </nav>
  );
}