import { Routes, Route } from 'react-router-dom'
import CatalogoPage from './pages/catalogo/CatalogoPage'
import HomePage from './pages/HomePage'
import ContactoPage from './pages/ContactoPage'

export default function App() {
  return (
    <Routes>
      {/* Ruta de inicio */}
      <Route path="/" element={<HomePage />} />
      
      {/* Catálogo */}
      <Route path="/catalogo" element={<CatalogoPage />} />
      <Route path="/contacto" element={<ContactoPage />} />
    </Routes>
  )
}