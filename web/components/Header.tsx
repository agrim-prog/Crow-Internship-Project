import Image from "next/image";

export default function Header() {
  return (
    <header className="fixed top-0 z-50 w-full bg-transparent">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-8 lg:px-16">
        <nav className="flex items-center gap-8">
          <a
            href="#top"
            className="text-sm font-semibold tracking-tight text-foreground"
          >
            Crow AI — Lease Abstractor
          </a>
          <a
            href="#workbench"
            className="hidden text-sm text-muted-foreground transition-colors hover:text-foreground sm:inline"
          >
            Abstractor
          </a>
        </nav>
        <a href="#top" aria-label="Crow" className="shrink-0">
          <Image
            src="/crow-logo.png"
            alt="Crow"
            width={28}
            height={28}
            className="h-7 w-7"
            priority
          />
        </a>
      </div>
    </header>
  );
}
