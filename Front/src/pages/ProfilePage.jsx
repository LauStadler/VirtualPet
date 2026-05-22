import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { User, Package, Clock, CheckCircle, ChevronLeft } from 'lucide-react'
import useAuthStore from '../store/authStore'
import api from '../services/api'

const ProfilePage = () => {
  const { user } = useAuthStore()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await api.get('/orders')
        setOrders(response.data)
      } catch (error) {
        console.error('Error fetching orders:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchOrders()
  }, [])

  // Agrupación de pedidos (por ahora todo lo que no sea 'entregado' es 'En curso')
  // Nota: 'entregado' no existe aún en el backend, se prepara para el futuro.
  const inProgressOrders = orders.filter(o => o.estado !== 'entregado')
  const receivedOrders = orders.filter(o => o.estado === 'entregado')

  const OrderCard = ({ order }) => (
    <div className="bg-white border border-surface-200 rounded-2xl p-5 mb-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <span className="text-xs font-bold text-brand-500 uppercase tracking-wider">Pedido #{order.id}</span>
          <p className="text-sm text-gray-500 mt-1">
            {new Date(order.created_at).toLocaleDateString('es-AR', {
              day: 'numeric',
              month: 'long',
              year: 'numeric'
            })}
          </p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-gray-900">${order.total.toLocaleString('es-AR')}</p>
        </div>
      </div>
      <Link 
        to={`/perfil/pedido/${order.id}`}
        className="text-sm font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
      >
        Ver detalles
      </Link>
    </div>
  )

  return (
    <div className="min-h-screen bg-surface-50 font-body pb-20">
      {/* Header / Nav */}
      <div className="bg-white border-b border-surface-200 sticky top-0 z-10">
        <div className="max-w-screen-md mx-auto px-6 h-16 flex items-center gap-4">
          <Link to="/" className="p-2 -ml-2 hover:bg-surface-100 rounded-xl transition-colors text-gray-600">
            <ChevronLeft size={20} />
          </Link>
          <h1 className="font-display text-xl font-bold text-gray-900">Mi Perfil</h1>
        </div>
      </div>

      <div className="max-w-screen-md mx-auto px-6 py-8">
        {/* Información del Usuario */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-brand-500 rounded-xl flex items-center justify-center text-white">
              <User size={20} />
            </div>
            <h2 className="font-display text-2xl font-bold text-gray-900">Mis Datos</h2>
          </div>
          
          <div className="bg-white border border-surface-200 rounded-3xl p-8 shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Nombre y Apellido</label>
                <p className="text-lg font-semibold text-gray-900">{user?.nombre} {user?.apellido}</p>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Email</label>
                <p className="text-lg font-semibold text-gray-900">{user?.email}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Historial de Pedidos */}
        <section>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-brand-100 rounded-xl flex items-center justify-center text-brand-600">
              <Package size={20} />
            </div>
            <h2 className="font-display text-2xl font-bold text-gray-900">Mis Pedidos</h2>
          </div>

          {loading ? (
            <div className="flex flex-col items-center py-12 text-gray-400">
              <div className="w-8 h-8 border-4 border-brand-500/20 border-t-brand-500 rounded-full animate-spin mb-4"></div>
              <p>Cargando historial...</p>
            </div>
          ) : (
            <div className="space-y-10">
              {/* Pedidos en curso */}
              <div>
                <div className="flex items-center gap-2 mb-4 text-brand-600">
                  <Clock size={18} />
                  <h3 className="font-bold uppercase tracking-widest text-xs">Pedidos en curso</h3>
                </div>
                
                {inProgressOrders.length > 0 ? (
                  inProgressOrders.map(order => <OrderCard key={order.id} order={order} />)
                ) : (
                  <div className="bg-surface-100 border border-dashed border-surface-300 rounded-2xl p-8 text-center">
                    <p className="text-gray-500 text-sm">No tienes pedidos en curso actualmente.</p>
                    <Link to="/catalogo" className="inline-block mt-4 text-brand-600 font-bold text-sm hover:underline">
                      Ir al catálogo
                    </Link>
                  </div>
                )}
              </div>

              {/* Pedidos recibidos */}
              <div>
                <div className="flex items-center gap-2 mb-4 text-green-600">
                  <CheckCircle size={18} />
                  <h3 className="font-bold uppercase tracking-widest text-xs">Pedidos recibidos</h3>
                </div>
                
                {receivedOrders.length > 0 ? (
                  receivedOrders.map(order => <OrderCard key={order.id} order={order} />)
                ) : (
                  <div className="bg-surface-100 border border-dashed border-surface-300 rounded-2xl p-8 text-center text-gray-500">
                    <p className="text-sm">Aún no tienes pedidos marcados como recibidos.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

export default ProfilePage
