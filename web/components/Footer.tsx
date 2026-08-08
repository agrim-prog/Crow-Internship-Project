export default function Footer() {
  return (
    <footer className="border-t border-border bg-background">
      <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-10 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-16">
        <p>Crow Lease Abstractor — read once, flagged where it counts.</p>
        <a href="#top" className="text-muted-foreground transition-colors hover:text-foreground">
          Back to top ↑
        </a>
      </div>
    </footer>
  );
}
