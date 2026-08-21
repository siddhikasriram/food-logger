import { NavLink, Outlet } from "react-router-dom";

import { useUser } from "../context/UserContext";

export function Layout() {
  const { user } = useUser();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <div>
            <p className="brand-kicker">Daily protein</p>
            <h1>Food Logger</h1>
          </div>
        </div>
        <nav className="nav">
          <NavLink to="/" end>
            Today
          </NavLink>
          <NavLink to="/chat">Chat</NavLink>
          <NavLink to="/recipes">Recipes</NavLink>
          <NavLink to="/ingredients">Ingredients</NavLink>
          <NavLink to="/profile">Profile</NavLink>
        </nav>
        {user ? <p className="whoami">{user.name}</p> : null}
      </header>
      <main className="page">
        <Outlet />
      </main>
    </div>
  );
}
