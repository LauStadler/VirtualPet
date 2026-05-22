import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, Package, MapPin, Calendar, CreditCard } from 'lucide-react'
import api from '../services/api'

const OrderDetailPage = () => {
  const { id } = useParams()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const response = await api.get(`/orders/${id}`)
        setOrder(response.data)
      } catch (error) {
        console.error('Error fetching order detail:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchOrder()
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-50 flex items-center justify-center font-body">
        <div className="w-8 h-8 border-4 border-brand-500/20 border-t-brand-500 rounded-full animate-spin"></div>
      </div>
    )
  }

  if (!order) {
    return (
      <div className="min-h-screen bg-surface-50 flex flex-col items-center justify-center font-body p-6 text-center">
        <p className="text-gray-500 mb-4">No se pudo encontrar la información del pedido.</p>
        <Link to="/perfil" className="text-brand-600 font-bold hover:underline">Volver a mi perfil</Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface-50 font-body pb-20">
      <div className="bg-white border-b border-surface-200 sticky top-0 z-10">
        <div className="max-w-screen-md mx-auto px-6 h-16 flex items-center gap-4">
          <Link to="/perfil" className="p-2 -ml-2 hover:bg-surface-100 rounded-xl transition-colors text-gray-600">
            <ChevronLeft size={20} />
          </Link>
          <h1 className="font-display text-xl font-bold text-gray-900">Detalle del Pedido #{order.id}</h1>
        </div>
      </div>

      <div className="max-w-screen-md mx-auto px-6 py-8 space-y-6">
        {/* Resumen General */}
        <div className="bg-white border border-surface-200 rounded-3xl p-6 shadow-sm grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-start gap-3">
            <Calendar className="text-brand-500 shrink-0 mt-1" size={18} />
            <div>
              <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Fecha de compra</p>
              <p className="font-semibold text-gray-900">
                {new Date(order.created_at).toLocaleDateString('es-AR', {
                  day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
                })}
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <MapPin className="text-brand-500 shrink-0 mt-1" size={18} />
            <div>
              <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Dirección de entrega</p>
              <p className="font-semibold text-gray-900">{order.direccion_entrega}</p>
            </div>
          </div>
        </div>

        {/* Items del pedido */}
        <div className="bg-white border border-surface-200 rounded-3xl shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-surface-100 bg-surface-50/50 flex items-center gap-2">
            <Package size={18} className="text-brand-600" />
            <h2 className="font-display font-bold text-gray-900">Productos</h2>
          </div>
          <div className="divide-y divide-surface-100">
            {order.items.map((item, idx) => (
              <div key={idx} className="p-6 flex justify-between items-center">
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">{item.producto_nombre || `Producto #${item.product_id}`}</p>
                  <p className="text-sm text-gray-500 mt-0.5">Cantidad: {item.cantidad} x ${item.precio_unitario.toLocaleString('es-AR')}</p>
                </div>
                <p className="font-bold text-gray-900 ml-4">${item.subtotal.toLocaleString('es-AR')}</p>
              </div>
            ))}
          </div>
          <div className="px-6 py-6 bg-surface-50/30 flex justify-between items-center border-t border-surface-100">
            <div className="flex items-center gap-2 text-gray-600">
              <CreditCard size={18} />
              <span className="text-sm font-semibold">Total pagado</span>
            </div>
            <p className="text-2xl font-display font-black text-brand-600">${order.total.toLocaleString('es-AR')}</p>
          </div>
        </div>

        <div className="bg-brand-50 border border-brand-100 rounded-2xl p-4 text-center">
          <p className="text-brand-700 text-sm font-medium">
            Si tienes alguna duda con tu pedido, contáctanos mencionando el ID #{order.id}
          </p>
        </div>
      </div>
    </div>
  )
}

export default OrderDetailPage
