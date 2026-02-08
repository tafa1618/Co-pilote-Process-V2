import React from 'react';

function TestDashboard() {
    return (
        <div style={{ background: '#000', color: '#FFCD11', padding: '50px', minHeight: '100vh' }}>
            <h1 style={{ fontSize: '48px', marginBottom: '20px' }}>🏗️ NEEMBA CAT Test</h1>
            <p style={{ fontSize: '24px' }}>Si vous voyez ceci, React fonctionne !</p>
            <div style={{ marginTop: '30px', padding: '20px', background: '#FFCD11', color: '#000', borderRadius: '10px' }}>
                <p><strong>✅ Backend:</strong> http://localhost:8000</p>
                <p><strong>✅ Frontend:</strong> http://localhost:5174</p>
            </div>
        </div>
    );
}

export default TestDashboard;
