"""
Mock data service for individual KPI details
Includes historical trends, AI insights, and corrective actions
"""

def get_kpi_detail(kpi_name: str):
    """Get detailed information for a specific KPI"""
    
    # Mock historical data (last 12 months)
    months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jui", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    
    # Base template
    detail = {
        "kpi_name": kpi_name,
        "current_value": 0,
        "target": 0,
        "unit": "",
        "trend": [],  # Historical data
        "insights": [],  # AI insights
        "actions": [],  # Corrective actions
        "forecast": []  # Predicted next 3 months
    }
    
    # Example for Parts Fill Rate
    if "Parts Fill Rate" in kpi_name:
        detail.update({
            "current_value": 93.2,
            "target": 95.0,
            "unit": "%",
            "trend": [
                {"month": m, "value": v} for m, v in zip(months, 
                [89.5, 90.2, 91.5, 92.1, 91.8, 92.5, 92.8, 93.1, 93.5, 93.2, 93.4, 93.2])
            ],
            "insights": [
                {
                    "type": "warning",
                    "priority": "HIGH",
                    "message": "Stagnation des performances",
                    "details": "Le taux de remplissage des pièces stagne autour de 93% depuis 3 mois, en dessous de l'objectif de 95%."
                },
                {
                    "type": "info",
                    "priority": "MEDIUM",
                    "message": "Corrélation identifiée",
                    "details": "Les périodes de baisse coïncident avec les pics de demande (T2 et T4)."
                }
            ],
            "actions": [
                {
                    "id": "PFR-001",
                    "title": "Optimiser le stock de sécurité",
                    "description": "Augmenter le stock de sécurité pour les pièces à rotation rapide de 15%.",
                    "priority": "HIGH",
                    "owner": "Supply Chain Manager",
                    "estimated_impact": "+1.5% Parts Fill Rate",
                    "timeline": "2 semaines",
                    "status": "suggested"
                },
                {
                    "id": "PFR-002",
                    "title": "Améliorer les prévisions de demande",
                    "description": "Implémenter un modèle ML pour prédire les pics saisonniers.",
                    "priority": "MEDIUM",
                    "owner": "Data Analytics Team",
                    "estimated_impact": "+0.8% Parts Fill Rate",
                    "timeline": "1 mois",
                    "status": "suggested"
                }
            ],
            "forecast": [
                {"month": "Jan 2026", "predicted": 93.5, "confidence": 0.85},
                {"month": "Fév 2026", "predicted": 94.2, "confidence": 0.78},
                {"month": "Mar 2026", "predicted": 94.8, "confidence": 0.72}
            ]
        })
    
    # Example for Equipment Uptime
    elif "Equipment Uptime" in kpi_name:
        detail.update({
            "current_value": 96.5,
            "target": 97.5,
            "unit": "%",
            "trend": [
                {"month": m, "value": v} for m, v in zip(months,
                [95.2, 95.8, 96.1, 96.3, 96.5, 96.2, 96.8, 97.1, 96.9, 96.7, 96.5, 96.5])
            ],
            "insights": [
                {
                    "type": "success",
                    "priority": "MEDIUM",
                    "message": "Performance stable",
                    "details": "Le temps de disponibilité des équipements se maintient au-dessus de 96% depuis 6 mois."
                },
                {
                    "type": "warning",
                    "priority": "HIGH",
                    "message": "Légère baisse en Q4",
                    "details": "Baisse de 0.2% par rapport au pic de juillet, potentiellement liée à l'usure saisonnière."
                }
            ],
            "actions": [
                {
                    "id": "EUT-001",
                    "title": "Maintenance préventive renforcée",
                    "description": "Augmenter la fréquence des inspections préventives de 10%.",
                    "priority": "MEDIUM",
                    "owner": "Maintenance Manager",
                    "estimated_impact": "+0.5% Uptime",
                    "timeline": "3 semaines",
                    "status": "suggested"
                }
            ],
            "forecast": [
                {"month": "Jan 2026", "predicted": 96.8, "confidence": 0.88},
                {"month": "Fév 2026", "predicted": 97.0, "confidence": 0.82},
                {"month": "Mar 2026", "predicted": 97.2, "confidence": 0.75}
            ]
        })
    
    # Generic fallback for other KPIs
    else:
        detail.update({
            "current_value": 85.0,
            "target": 90.0,
            "unit": "%",
            "trend": [
                {"month": m, "value": 80 + i * 0.5} for i, m in enumerate(months)
            ],
            "insights": [
                {
                    "type": "info",
                    "priority": "MEDIUM",
                    "message": "Tendance positive observée",
                    "details": f"Le KPI {kpi_name} montre une amélioration progressive sur les 12 derniers mois."
                }
            ],
            "actions": [
                {
                    "id": "GEN-001",
                    "title": "Analyser les facteurs de performance",
                    "description": "Identifier les leviers d'amélioration principaux.",
                    "priority": "MEDIUM",
                    "owner": "Process Improvement Team",
                    "estimated_impact": "TBD",
                    "timeline": "2 semaines",
                    "status": "suggested"
                }
            ],
            "forecast": [
                {"month": "Jan 2026", "predicted": 86.0, "confidence": 0.70},
                {"month": "Fév 2026", "predicted": 87.0, "confidence": 0.65},
                {"month": "Mar 2026", "predicted": 88.0, "confidence": 0.60}
            ]
        })
    
    return detail
