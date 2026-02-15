"""
Standalone Flask server for SEP mock data
Bypasses FastAPI/Pydantic issues
"""
from flask import Flask, jsonify
from flask_cors import CORS
import sys
sys.path.append('backend')
from services.mock_sep_data import MockSEPDataService

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

@app.route('/api/sep/kpis', methods=['GET'])
def get_sep_kpis():
    """Get all SEP KPIs (12 official metrics)"""
    return jsonify(MockSEPDataService.get_sep_kpis())

@app.route('/api/sep/custom-kpis', methods=['GET'])
def get_custom_kpis():
    """Get custom internal KPIs"""
    return jsonify(MockSEPDataService.get_custom_kpis())

@app.route('/api/sep/insights', methods=['GET'])
def get_agent_insights():
    """Get agent insights and recommendations"""
    from services.mock_sep_data import MockSEPDataService
    return jsonify(MockSEPDataService.get_agent_insights())

@app.route('/api/sep/kpi/<kpi_name>/details', methods=['GET'])
def get_kpi_details(kpi_name):
    """Get detailed information for a specific KPI"""
    from services.kpi_detail_service import get_kpi_detail
    return jsonify(get_kpi_detail(kpi_name))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("SEP Mock Server starting on http://localhost:8000")
    print("Endpoints:")
    print("   - GET /api/sep/kpis")
    print("   - GET /api/sep/custom-kpis")
    print("   - GET /api/sep/insights")
    app.run(host='0.0.0.0', port=8000, debug=True)
