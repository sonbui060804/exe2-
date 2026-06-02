import { useState, useEffect } from 'react';

function Workspace({ invoiceId, onBack }) {
  const [data, setData] = useState(null);
  const [vendorStatus, setVendorStatus] = useState(null); // 'matched' | 'new'

  useEffect(() => {
    fetch(`http://localhost:8000/api/invoices/${invoiceId}`)
      .then(res => res.json())
      .then(resData => {
        if(resData.invoice) {
          setData(resData.invoice);
          // Fake check Vendor against Master DB
          if (resData.invoice.seller_info?.tax_code === "0307120868" || resData.invoice.seller_info?.tax_code === "0305479144") {
            setVendorStatus('matched');
          } else {
            setVendorStatus('new');
          }
        }
      })
      .catch(err => console.error(err));
  }, [invoiceId]);

  const handleApprove = () => {
    fetch(`http://localhost:8000/api/invoices/${invoiceId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data })
    })
    .then(res => res.json())
    .then(() => {
      alert("Đã duyệt thành công! Hóa đơn được chuyển sang Hàng đợi Đã Duyệt.");
      onBack();
    });
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...(data.items || [])];
    newItems[index] = { ...newItems[index], [field]: value };
    setData({ ...data, items: newItems });
  };

  if (!data) return <div>Loading...</div>;

  return (
    <div className="workspace-container">
      {/* Cột trái: Document Viewer */}
      <div className="viewer-pane">
        <img 
          src={`http://localhost:8000/static/${invoiceId}.png`} 
          alt="Invoice Original" 
          onError={(e) => { e.target.src = 'https://via.placeholder.com/600x800?text=Invoice+Image' }}
        />
      </div>

      {/* Cột phải: Data Form */}
      <div className="form-pane">
        <div className="form-header">
          <h2>Duyệt Hóa Đơn & Mã Hóa Kế Toán</h2>
          <div>
            <button className="btn-back" onClick={onBack}>Trở lại</button>
            <button className="btn-approve" onClick={handleApprove}>Phê Duyệt</button>
          </div>
        </div>

        <div className="form-body">
          <div className="section">
            <div className="section-title">Thông tin chung</div>
            <div className="form-group">
              <label>Số Hóa Đơn</label>
              <div className="input-wrapper">
                <div className="conf-indicator conf-high"></div>
                <input 
                  type="text" 
                  value={data.invoice_info?.invoice_no || ''} 
                  onChange={e => setData({...data, invoice_info: {...data.invoice_info, invoice_no: e.target.value}})}
                />
              </div>
            </div>
            <div className="form-group">
              <label>Ngày Lập</label>
              <div className="input-wrapper">
                <div className="conf-indicator conf-high"></div>
                <input 
                  type="text" 
                  value={data.invoice_info?.issue_date || ''} 
                  onChange={e => setData({...data, invoice_info: {...data.invoice_info, issue_date: e.target.value}})}
                />
              </div>
            </div>
          </div>

          <div className="section">
            <div className="section-title" style={{display: 'flex', justifyContent: 'space-between'}}>
              <span>Người Bán (Vendor)</span>
              {vendorStatus === 'matched' ? (
                <span style={{color: 'green', fontSize: '0.8rem'}}>✅ Có trong danh mục ERP</span>
              ) : (
                <span style={{color: '#d97706', fontSize: '0.8rem'}}>⚠️ Khách hàng mới (Cần tạo mã)</span>
              )}
            </div>
            <div className="form-group">
              <label>Mã Số Thuế</label>
              <div className="input-wrapper">
                <div className="conf-indicator conf-high"></div>
                <input type="text" value={data.seller_info?.tax_code || ''} readOnly style={{background: '#f9fafb'}} />
              </div>
            </div>
            <div className="form-group">
              <label>Tên Công Ty</label>
              <div className="input-wrapper">
                <div className="conf-indicator conf-high"></div>
                <input type="text" value={data.seller_info?.legal_name || ''} readOnly style={{background: '#f9fafb'}} />
              </div>
            </div>
          </div>
          
          <div className="section">
            <div className="section-title">Hàng Hóa Dịch Vụ & Mã Tài Khoản (GL Coding)</div>
            <table className="items-table" style={{width: '100%', fontSize: '0.8rem'}}>
              <thead>
                <tr>
                  <th>Tên Hàng Hóa</th>
                  <th style={{width: '60px'}}>TK Nợ</th>
                  <th style={{width: '60px'}}>TK Có</th>
                  <th style={{width: '100px'}}>Thành Tiền</th>
                </tr>
              </thead>
              <tbody>
                {(data.items || []).map((item, idx) => (
                  <tr key={idx}>
                    <td>
                      <input 
                        value={item.item_name || ''} 
                        onChange={e => handleItemChange(idx, 'item_name', e.target.value)}
                      />
                    </td>
                    <td>
                      <input 
                        placeholder="156"
                        value={item.debit_account || ''} 
                        onChange={e => handleItemChange(idx, 'debit_account', e.target.value)}
                      />
                    </td>
                    <td>
                      <input 
                        placeholder="331"
                        value={item.credit_account || ''} 
                        onChange={e => handleItemChange(idx, 'credit_account', e.target.value)}
                      />
                    </td>
                    <td>
                      <input 
                        value={item.amount_before_tax || ''} 
                        onChange={e => handleItemChange(idx, 'amount_before_tax', e.target.value)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="section">
            <div className="section-title">Tổng Cộng & Kiểm Tra Thuế (VAT)</div>
            <div style={{display: 'flex', gap: '10px'}}>
              <div className="form-group" style={{flex: 1}}>
                <label>Tiền Hàng</label>
                <div className="input-wrapper">
                  <input type="text" value={data.totals?.total_amount_before_tax || 0} readOnly style={{background: '#f9fafb'}} />
                </div>
              </div>
              <div className="form-group" style={{flex: 1}}>
                <label>Tiền Thuế (VAT)</label>
                <div className="input-wrapper">
                  <input type="text" value={data.totals?.total_tax_amount || 0} readOnly style={{background: '#f9fafb'}} />
                </div>
              </div>
            </div>
            <div className="form-group">
              <label>Tổng Tiền Thanh Toán</label>
              <div className="input-wrapper">
                <div className="conf-indicator conf-high"></div>
                <input type="text" value={data.totals?.total_amount_after_tax || 0} readOnly style={{background: '#f9fafb'}} />
              </div>
            </div>
            {/* Lỗi chênh lệch thuế (Mockup logic) */}
            {data.totals?.total_amount_before_tax + data.totals?.total_tax_amount !== data.totals?.total_amount_after_tax && (
              <div style={{color: 'red', fontSize: '0.8rem', marginTop: '5px'}}>
                ⚠️ Cảnh báo: Tiền hàng + Thuế không khớp với Tổng thanh toán!
              </div>
            )}
          </div>
          
        </div>
      </div>
    </div>
  );
}

export default Workspace;
