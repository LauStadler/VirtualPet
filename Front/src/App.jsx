import { Routes, Route } from 'react-router-dom'
import CatalogoPage from './pages/catalogo/CatalogoPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<CatalogoPage />} />
    </Routes>
  )
}
