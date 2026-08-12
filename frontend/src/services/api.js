const API_GATEWAY_URL = import.meta.env.VITE_API_GATEWAY_URL || '';

async function request(endpoint, options = {}) {
  const url = `${API_GATEWAY_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const token = localStorage.getItem('auth_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data.error || data.message || `HTTP ${response.status} Request Failed`;
    throw new Error(errorMsg);
  }

  return data;
}

export const api = {
  // Auth Service calls (via Gateway /api/auth)
  login: (credentials) => request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  }),

  register: (userData) => request('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  }),

  // Product Service calls (via Gateway /api/products)
  getProducts: () => request('/api/products'),
  getProductById: (id) => request(`/api/products/${id}`),

  // Payment Service calls (via Gateway /api/payments)
  createPayment: (paymentData) => request('/api/payments', {
    method: 'POST',
    body: JSON.stringify(paymentData),
  }),

  getPaymentById: (id) => request(`/api/payments/${id}`),
  getUserPayments: (userId) => request(`/api/payments/user/${userId}`),
};
