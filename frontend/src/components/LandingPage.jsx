import React from 'react';

function LandingPage({ onLoginClick }) {
  return (
    <div className="landing-container" style={{display: 'block', padding: '2rem 1rem'}}>
      <div className="navbar" style={{background: 'transparent', border: 'none', padding: '0 2rem'}}>
        <h1 style={{color: 'white', fontSize: '1.5rem'}}>AI-INVOICE</h1>
        <button className="btn-enter" onClick={onLoginClick} style={{marginLeft: 'auto', background: 'white', color: 'var(--primary)', padding: '0.5rem 1.5rem'}}>Đăng Nhập / Đăng Ký</button>
      </div>

      <div className="hero-section" style={{margin: '0 auto', marginTop: '4rem', maxWidth: '1000px'}}>
        <h1 className="hero-title" style={{fontSize: '3.5rem'}}>AI-INVOICE AUTOMATION</h1>
        <p className="hero-subtitle">Giải pháp bóc tách hóa đơn Local AI - Nhanh, Chính xác, Bảo mật Tuyệt đối</p>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🚀</div>
            <h3>Xử Lý Hàng Loạt</h3>
            <p>Tải lên 500 - 1.000 hóa đơn cùng lúc. AI xử lý ngầm và xuất ra Excel chỉ trong vài phút.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3>AI Hiểu Ngữ Cảnh</h3>
            <p>LLM Qwen 2.5 đọc hiểu mọi form hóa đơn (VAT, bán lẻ, vé xe...) không lo lệch dòng.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3>Bảo Mật Local 100%</h3>
            <p>Chạy Offline trên máy chủ nội bộ. Hoàn toàn không rò rỉ dữ liệu tài chính.</p>
          </div>
        </div>

        <div className="comparison-table" style={{background: 'white', color: '#333', borderRadius: '12px', padding: '2rem', marginBottom: '3rem', textAlign: 'left', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)'}}>
          <h2 style={{textAlign: 'center', marginBottom: '1.5rem', color: 'var(--primary)'}}>So Sánh Tính Năng</h2>
          <table style={{width: '100%', borderCollapse: 'collapse'}}>
            <thead>
              <tr style={{background: '#f9fafb', borderBottom: '2px solid #e5e7eb'}}>
                <th style={{padding: '1rem'}}>Tiêu chí</th>
                <th style={{padding: '1rem', color: '#6b7280'}}>Bizzi (Cloud SaaS)</th>
                <th style={{padding: '1rem', color: '#6b7280'}}>FPT.AI (API)</th>
                <th style={{padding: '1rem', color: 'var(--primary)', fontSize: '1.1rem'}}>AI-Invoice (Local)</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{borderBottom: '1px solid #e5e7eb'}}>
                <td style={{padding: '1rem', fontWeight: 'bold'}}>Công nghệ đọc</td>
                <td style={{padding: '1rem'}}>AI Cloud</td>
                <td style={{padding: '1rem'}}>AI Cloud</td>
                <td style={{padding: '1rem', fontWeight: 'bold', color: 'var(--primary)'}}>AI Local (Qwen 2.5)</td>
              </tr>
              <tr style={{borderBottom: '1px solid #e5e7eb'}}>
                <td style={{padding: '1rem', fontWeight: 'bold'}}>Xử lý hàng loạt</td>
                <td style={{padding: '1rem'}}>Có</td>
                <td style={{padding: '1rem'}}>Không (Gọi API từng tờ)</td>
                <td style={{padding: '1rem', fontWeight: 'bold', color: 'var(--primary)'}}>Có (Kéo thả ReactJS)</td>
              </tr>
              <tr style={{borderBottom: '1px solid #e5e7eb'}}>
                <td style={{padding: '1rem', fontWeight: 'bold'}}>Bảo mật dữ liệu</td>
                <td style={{padding: '1rem', color: '#d97706'}}>Trung bình (Internet)</td>
                <td style={{padding: '1rem', color: '#d97706'}}>Trung bình (Internet)</td>
                <td style={{padding: '1rem', fontWeight: 'bold', color: 'var(--primary)'}}>Tuyệt đối 100% (Offline)</td>
              </tr>
              <tr>
                <td style={{padding: '1rem', fontWeight: 'bold'}}>Chi phí triển khai</td>
                <td style={{padding: '1rem'}}>Thuê bao khá đắt</td>
                <td style={{padding: '1rem'}}>Tính tiền theo lượt quét</td>
                <td style={{padding: '1rem', fontWeight: 'bold', color: 'var(--primary)'}}>Cực rẻ (On-Premise)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="action-section" style={{display: 'inline-block'}}>
          <p className="freemium-text">Đăng ký Gói Trải Nghiệm (Freemium) - Miễn phí 50 Hóa đơn</p>
          <button className="btn-enter" onClick={onLoginClick}>
            Đăng Nhập Ngay Để Trải Nghiệm
          </button>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
