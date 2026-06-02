import { useState, useEffect } from 'react';

function Dashboard({ onSelectInvoice }) {
  const [invoices, setInvoices] = useState([]);
  const [quota, setQuota] = useState({ used: 0, limit: 50 });
  const [activeTab, setActiveTab] = useState('pending'); // 'pending' | 'approved'
  
  // Fake upload state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = () => {
    fetch('http://localhost:8000/api/invoices')
      .then(res => res.json())
      .then(data => {
        if(data.invoices) {
            setInvoices(data.invoices);
            setQuota(q => ({...q, used: data.invoices.length}));
        }
      })
      .catch(err => console.error(err));
  };

  const handleUpload = () => {
    if (quota.used >= quota.limit) {
      alert("Bạn đã dùng hết gói Freemium (50/50). Vui lòng nâng cấp gói Cloud SaaS hoặc On-Premise để upload tiếp!");
      return;
    }
    
    // Simulate batch upload & processing
    setIsUploading(true);
    setUploadProgress(0);
    
    const interval = setInterval(() => {
      setUploadProgress(p => {
        if (p >= 100) {
          clearInterval(interval);
          setIsUploading(false);
          alert("Mô phỏng Upload thành công! AI đang xử lý ngầm.");
          return 100;
        }
        return p + 10;
      });
    }, 300);
  };

  const progressPercent = Math.min((quota.used / quota.limit) * 100, 100);
  const isWarning = quota.used >= quota.limit * 0.8;

  const filteredInvoices = invoices.filter(inv => {
    const status = inv.workflow?.status || 'PENDING_REVIEW';
    if (activeTab === 'pending') return status === 'PENDING_REVIEW';
    return status === 'APPROVED';
  });

  return (
    <div className="dashboard-container">
      {/* 1. QUOTA WIDGET */}
      <div className="quota-widget" style={{display: 'flex', gap: '2rem'}}>
        <div style={{flex: 1}}>
          <h3>Dung lượng xử lý AI</h3>
          <p>Gói Miễn Phí (Freemium): {quota.used} / {quota.limit} Hóa Đơn</p>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{width: `${progressPercent}%`, background: isWarning ? '#ef4444' : 'var(--primary)'}}>
            </div>
          </div>
          {quota.used >= quota.limit && (
              <div className="alert-box">
                  ⚠️ Đã hết lượt quét miễn phí. Hệ thống đã khóa chức năng Upload. Vui lòng liên hệ nâng cấp gói!
              </div>
          )}
        </div>
        
        <div style={{flex: 1, borderLeft: '1px solid #e5e7eb', paddingLeft: '2rem'}}>
          <h3>Xuất Dữ Liệu Hàng Loạt (Export)</h3>
          <p style={{marginBottom: '1rem', color: 'var(--text-muted)'}}>Sau khi duyệt xong, tải file về máy để nạp vào ERP.</p>
          <div style={{display: 'flex', gap: '10px'}}>
            <button className="btn-back" style={{borderColor: 'green', color: 'green'}}>Tải Excel</button>
            <button className="btn-back" style={{borderColor: 'blue', color: 'blue'}}>Tải XML MISA</button>
            <button className="btn-back" style={{borderColor: 'orange', color: 'orange'}}>Tải CSV FAST</button>
          </div>
        </div>
      </div>

      {/* 2. BATCH UPLOAD ZONE */}
      <div className="card" style={{padding: '2rem', textAlign: 'center', marginBottom: '2rem', border: '2px dashed var(--border-color)'}}>
        <div style={{fontSize: '3rem', marginBottom: '1rem'}}>📥</div>
        <h3>Tải Lên Hàng Loạt (Batch Upload)</h3>
        <p style={{color: 'var(--text-muted)', marginBottom: '1.5rem'}}>Kéo thả tối đa 500 - 1.000 hóa đơn vào đây để AI tự động xử lý.</p>
        
        {isUploading ? (
          <div style={{maxWidth: '400px', margin: '0 auto'}}>
            <p>Đang tải lên và xử lý... {uploadProgress}%</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{width: `${uploadProgress}%`}}></div>
            </div>
          </div>
        ) : (
          <button className="btn-enter" onClick={handleUpload} disabled={quota.used >= quota.limit} style={{opacity: quota.used >= quota.limit ? 0.5 : 1}}>
            Chọn File (Từ máy tính)
          </button>
        )}
      </div>

      {/* 3. INVOICE QUEUES */}
      <div className="card">
        <div style={{display: 'flex', borderBottom: '1px solid var(--border-color)', background: '#f9fafb'}}>
          <button 
            style={{flex: 1, padding: '1rem', background: activeTab === 'pending' ? 'white' : 'transparent', border: 'none', borderBottom: activeTab === 'pending' ? '2px solid var(--primary)' : 'none', fontWeight: 'bold', cursor: 'pointer'}}
            onClick={() => setActiveTab('pending')}
          >
            Hàng đợi: CẦN DUYỆT (To Review)
          </button>
          <button 
            style={{flex: 1, padding: '1rem', background: activeTab === 'approved' ? 'white' : 'transparent', border: 'none', borderBottom: activeTab === 'approved' ? '2px solid var(--primary)' : 'none', fontWeight: 'bold', cursor: 'pointer'}}
            onClick={() => setActiveTab('approved')}
          >
            Hàng đợi: ĐÃ DUYỆT (Approved)
          </button>
        </div>

        <table>
          <thead>
            <tr>
              <th>ID Tài liệu</th>
              <th>Số Hóa Đơn</th>
              <th>Người Bán</th>
              <th>Tổng Tiền</th>
              <th>Trạng Thái</th>
            </tr>
          </thead>
          <tbody>
            {filteredInvoices.map(inv => (
              <tr key={inv.document_id} onClick={() => onSelectInvoice(inv.document_id)}>
                <td>{inv.document_id}</td>
                <td>{inv.invoice_info?.invoice_no || 'N/A'}</td>
                <td>{inv.seller_info?.legal_name || 'N/A'}</td>
                <td>{inv.totals?.total_amount_after_tax ? inv.totals.total_amount_after_tax.toLocaleString() : 'N/A'}</td>
                <td>
                  <span className={`badge ${inv.workflow?.status?.toLowerCase() || 'pending_review'}`}>
                    {inv.workflow?.status || 'PENDING'}
                  </span>
                </td>
              </tr>
            ))}
            {filteredInvoices.length === 0 && (
              <tr>
                <td colSpan="5" style={{textAlign: 'center', padding: '2rem', color: 'var(--text-muted)'}}>
                  Không có hóa đơn nào trong hàng đợi này.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;
