import { Link } from 'react-router'

export default function NotFoundPage() {
  return (
    <section>
      <h1>404</h1>
      <p>Хуудас олдсонгүй.</p>
      <Link to="/">Нүүр хуудас руу буцах</Link>
    </section>
  )
}
