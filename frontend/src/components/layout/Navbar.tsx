import { NavLink } from 'react-router-dom'
import Container from './Container'

const navLink =
  'px-3 py-2 rounded-lg text-sm font-medium transition hover:bg-slate-100'
const navLinkActive = 'bg-slate-100 text-slate-900'
const navLinkIdle = 'text-slate-600'

function LinkItem({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `${navLink} ${isActive ? navLinkActive : navLinkIdle}`
      }
      end={to === '/'}
    >
      {label}
    </NavLink>
  )
}

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur">
      <Container>
        <div className="flex items-center justify-between py-3">
          <NavLink to="/" className="flex items-center gap-2 font-semibold">
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-white">
              SXI
            </span>
            <span>SketchLogic X IRis</span>
          </NavLink>

          <nav className="flex items-center gap-1">
            <LinkItem to="/" label="Home" />
            <LinkItem to="/try" label="Try SKELO" />
            <LinkItem to="/downloads" label="Downloads" />
            <LinkItem to="/about" label="About" />
          </nav>
        </div>
      </Container>
    </header>
  )
}
