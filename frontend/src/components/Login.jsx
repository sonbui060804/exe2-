import React, { useState } from 'react';

function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('123456');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('token', data.token);
        onLoginSuccess();
      } else {
        setError(data.detail || 'Đăng nhập thất bại');
      }
    } catch (err) {
      setError('Lỗi kết nối đến Server');
    }
  };

  return (
    <div className="landing-container" style={{display: 'flex', background: 'linear-gradient(135deg, #10b981 0%, #047857 100%)'}}>
      <div style={{background: 'white', padding: '3rem', borderRadius: '12px', width: '400px', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)', textAlign: 'left'}}>
        <h2 style={{color: 'var(--primary)', marginBottom: '0.5rem'}}>Đăng Nhập</h2>
        <p style={{color: 'var(--text-muted)', marginBottom: '2rem'}}>Truy cập không gian làm việc AI-Invoice</p>
        
        {error && <div className="alert-box" style={{marginBottom: '1rem'}}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Tài khoản</label>
            <div className="input-wrapper">
              <input type="text" value={username} onChange={e => setUsername(e.target.value)} required />
            </div>
          </div>
          <div className="form-group">
            <label>Mật khẩu</label>
            <div className="input-wrapper">
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
            </div>
          </div>
          
          <button type="submit" className="btn-enter" style={{width: '100%', marginTop: '1.5rem'}}>
            Đăng Nhập
          </button>
        </form>
        <p style={{textAlign: 'center', marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-muted)'}}>
          Chưa có tài khoản? <a href="#" style={{color: 'var(--primary)', textDecoration: 'none'}}>Đăng ký gói Freemium</a>
        </p>
      </div>
    </div>
  );
}

export default Login;
