import { NavLink } from 'react-router-dom'

function Navbar() {
  return (
    <header className="navbar">
      <NavLink to="/" className="brand logo-brand">
        <img
          src="/images/healthcoach-logo.png"
          alt="HealthCoach"
          className="navbar-logo"
        />
      </NavLink>

      <nav>
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            isActive ? 'nav-link active' : 'nav-link'
          }
        >
          Beranda
        </NavLink>

        <NavLink
          to="/analysis"
          className={({ isActive }) =>
            isActive ? 'nav-link active' : 'nav-link'
          }
        >
          Analisis Makanan
        </NavLink>

        <NavLink
          to="/about"
          className={({ isActive }) =>
            isActive ? 'nav-link active' : 'nav-link'
          }
        >
          Tentang
        </NavLink>
      </nav>
    </header>
  )
}

export default Navbar
