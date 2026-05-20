import { Routes, Route } from 'react-router-dom'
import CatalogoPage from './pages/catalogo/CatalogoPage'
import HomePage from './pages/HomePage'
import ContactoPage from './pages/ContactoPage'
import ScrollToTop from './components/ScrollToTop'

export default function App() {
  return (
    <>
      <ScrollToTop/>
      <Routes>
        {/* Ruta de inicio */}
        <Route path="/" element={<HomePage />} />
      
        {/* Catálogo */}
        <Route path="/catalogo" element={<CatalogoPage />} />
        <Route path="/contacto" element={<ContactoPage />} />
    </Routes>
    </>
  )
}