import { Link, Outlet } from 'react-router'

// Shared page frame: header on top, the current page below.
export default function Layout() {
  return (
    <>
      <header className="site-header">
        <Link to="/" className="brand">
          LMS
        </Link>
      </header>
      <main className="page">
        <Outlet />
      </main>
    </>
  )
}
