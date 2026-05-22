import { Routes, Route } from 'react-router-dom'
import CatalogoPage from './pages/catalogo/CatalogoPage'
import ProductDetailPage from './pages/catalogo/ProductDetailPage'
import ProfilePage from './pages/ProfilePage'
import OrderDetailPage from './pages/OrderDetailPage'
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
        <Route path="/producto/:id" element={<ProductDetailPage />} />
        <Route path="/contacto" element={<ContactoPage />} />

        {/* Usuario */}
        <Route path="/perfil" element={<ProfilePage />} />
        <Route path="/perfil/pedido/:id" element={<OrderDetailPage />} />
    </Routes>
    </>
  )
}