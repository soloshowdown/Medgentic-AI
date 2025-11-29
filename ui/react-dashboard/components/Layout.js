import Link from "next/link";
import { useRouter } from "next/router";

const links = [
  { href: "/", label: "Home" },
  { href: "/forecast", label: "Forecast" },
  { href: "/resources", label: "Resources" },
];

export default function Layout({ children }) {
  const router = useRouter();

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>Hospital Surge Predictor</h1>
          <p className="subtitle">India-wide agentic forecasting dashboard</p>
        </div>
        <nav>
          <ul className="nav-list">
            {links.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className={router.pathname === link.href ? "active" : ""}
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </header>
      <main className="app-main">{children}</main>
    </div>
  );
}

