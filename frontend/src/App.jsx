import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import Workspace from './components/Workspace'
import LandingPage from './components/LandingPage'
import Login from './components/Login'

function App() {
  const [showLanding, setShowLanding] = useState(true);
  const [showLogin, setShowLogin] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState(null);

  useEffect(() => {
    if (localStorage.getItem('token')) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setShowLanding(true);
  };

  if (showLanding) {
    return <LandingPage onLoginClick={() => { setShowLanding(false); setShowLogin(true); }} />;
  }

  if (showLogin && !isAuthenticated) {
    return <Login onLoginSuccess={() => { setIsAuthenticated(true); setShowLogin(false); }} />;
  }

  return (
    <div className="app-container">
      <nav className="navbar">
        <h1>AI-Invoice</h1>
        <div style={{marginLeft: 'auto'}}>
          <button className="btn-back" onClick={() => setShowLanding(true)}>Về Trang Chủ</button>
          <button className="btn-back" onClick={handleLogout} style={{color: 'red'}}>Đăng Xuất</button>
        </div>
      </nav>
      
      {selectedInvoiceId ? (
        <Workspace 
          invoiceId={selectedInvoiceId} 
          onBack={() => setSelectedInvoiceId(null)} 
        />
      ) : (
        <Dashboard onSelectInvoice={setSelectedInvoiceId} />
      )}
    </div>
  )
}

export default App
