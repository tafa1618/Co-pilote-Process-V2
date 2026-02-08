"""
Mock SEP Data Service
Provides mocked data for the 12 SEP KPIs (2025 Program)
"""
from datetime import datetime
from typing import Dict, Any, List

class MockSEPDataService:
    """Service to generate mock SEP KPI data"""
    
    @staticmethod
    def get_sep_kpis() -> Dict[str, Any]:
        """
        Returns mocked SEP KPIs for Q1 2026
        Includes all 12 official SEP metrics with realistic values
        """
        return {
            "period": "Q1 2026",
            "overall_score": 72,
            "performance_level": "SILVER",
            "categories": {
                "foundation_ops": {
                    "score": 68,
                    "weight": 40,
                    "performance_level": "SILVER",
                    "kpis": {
                        "service_rif": {
                            "name": "Service RIF",
                            "value": 0.8,
                            "target_excellent": 0.5,
                            "target_advanced": 0.8,
                            "target_emerging": 1.3,
                            "unit": "",
                            "performance": "ADVANCED",
                            "weight": 12,
                            "time_period": "YTD",
                            "data_source": "Self-Reported",
                            "mode": "manual",  # Fourni directement
                            "description": "Recordable Injury Frequency"
                        },
                        "tech_productivity": {
                            "name": "Technician Productivity",
                            "value": 82,
                            "target_excellent": 85,
                            "target_advanced": 82,
                            "target_emerging": 78,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 6,
                            "time_period": "R-12",
                            "data_source": "Self-Reported",
                            "mode": "calculated",
                            "description": "Billable Hours / Total Hours"
                        },
                        "tech_capacity": {
                            "name": "Technician Capacity (Tech Plan)",
                            "value": 96,
                            "target_excellent": 98,
                            "target_advanced": 96,
                            "target_emerging": 94,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 6,
                            "time_period": "YTD",
                            "data_source": "TAP Tool",
                            "mode": "calculated",
                            "description": "Actual Techs / Planned Techs"
                        },
                        "llti": {
                            "name": "Last Labor to Invoice",
                            "value": 12,
                            "target_excellent": 7,
                            "target_advanced": 12,
                            "target_emerging": 17,
                            "unit": "days",
                            "performance": "ADVANCED",
                            "weight": 5,
                            "time_period": "Quarterly",
                            "data_source": "CDDW",
                            "mode": "calculated",
                            "description": "Avg(Invoice Date - Last Labor Date)"
                        },
                        "tech_capability": {
                            "name": "Technician Capability (TCDPA)",
                            "value": 85,
                            "target_excellent": 95,
                            "target_advanced": 85,
                            "target_emerging": 60,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 6,
                            "time_period": "Quarterly",
                            "data_source": "TCDPA SharePoint",
                            "mode": "manual",  # Fourni directement
                            "description": "TCDPA Points / Total Points"
                        },
                        "data_quality": {
                            "name": "Service Data Quality",
                            "value": 90,
                            "target_excellent": 95,
                            "target_advanced": 90,
                            "target_emerging": 85,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 5,
                            "time_period": "Quarterly",
                            "data_source": "CDDW",
                            "mode": "calculated",
                            "description": "Valid Records / Total Records"
                        }
                    }
                },
                "services_growth": {
                    "score": 74,
                    "weight": 60,
                    "performance_level": "SILVER",
                    "kpis": {
                        "service_response": {
                            "name": "Service Response (Started by 2nd Day)",
                            "value": 75,
                            "target_excellent": 85,
                            "target_advanced": 75,
                            "target_emerging": 65,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 10,
                            "time_period": "Quarterly",
                            "data_source": "Self-Reported",
                            "mode": "manual",  # Fourni directement
                            "description": "Started by 2nd Day / Total Unplanned (Group 1)"
                        },
                        "remote_flash": {
                            "name": "Remote Service (Flash)",
                            "value": 45,
                            "target_excellent": 60,
                            "target_advanced": 50,
                            "target_emerging": 40,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 4,
                            "time_period": "YTD",
                            "data_source": "Automated",
                            "mode": "calculated",
                            "description": "Successful Flashes / Opportunities"
                        },
                        "remote_troubleshoot": {
                            "name": "Remote Service (Troubleshoot)",
                            "value": 25,
                            "target_excellent": 40,
                            "target_advanced": 30,
                            "target_emerging": 20,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 4,
                            "time_period": "YTD",
                            "data_source": "Automated",
                            "mode": "calculated",
                            "description": "Successful Sessions / Opportunities"
                        },
                        "cva_fulfillment": {
                            "name": "CVA Fulfillment",
                            "value": 75,
                            "target_excellent": 80,
                            "target_advanced": 70,
                            "target_emerging": 60,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 12,
                            "time_period": "R-12",
                            "data_source": "Automated",
                            "mode": "calculated",
                            "description": "(SOS% + Inspection% + Connectivity%) / 3"
                        },
                        "cva_pm_accuracy": {
                            "name": "CVA PM Accuracy",
                            "value": 82,
                            "target_excellent": 85,
                            "target_advanced": 82,
                            "target_emerging": 78,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 10,
                            "time_period": "Quarterly",
                            "data_source": "CDDW",
                            "mode": "calculated",
                            "description": "PM Events ±50hrs / Total PM Events"
                        },
                        "inspection_rate": {
                            "name": "Inspection Rate",
                            "value": 55,
                            "target_excellent": 65,
                            "target_advanced": 50,
                            "target_emerging": 40,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 12,
                            "time_period": "Quarterly",
                            "data_source": "CDDW",
                            "mode": "calculated",
                            "description": "Inspections / Expected Inspections"
                        },
                        "cma_recommendation": {
                            "name": "CMA Recommendation Coverage",
                            "value": 6.5,
                            "target_excellent": 10.0,
                            "target_advanced": 5.0,
                            "target_emerging": 2.5,
                            "unit": "%",
                            "performance": "ADVANCED",
                            "weight": 8,
                            "time_period": "YTD",
                            "data_source": "Automated",
                            "mode": "manual",  # Fourni directement
                            "description": "OLGA $ with CMA / Total OLGA $"
                        }
                    }
                }
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "mode": "MOCK",
                "version": "SEP 2025"
            }
        }
    
    @staticmethod
    def get_custom_kpis() -> List[Dict[str, Any]]:
        """Returns mocked custom internal KPIs"""
        return [
            {
                "id": "custom_1",
                "name": "Taux de Rotation Personnel",
                "value": 4.2,
                "target": 5.0,
                "unit": "%",
                "performance": "EXCELLENT",
                "time_period": "Quarterly",
                "mode": "calculated"
            },
            {
                "id": "custom_2",
                "name": "Coût Moyen par Intervention",
                "value": 1250,
                "target": 1500,
                "unit": "€",
                "performance": "EXCELLENT",
                "time_period": "Monthly",
                "mode": "calculated"
            }
        ]
    
    @staticmethod
    def get_agent_insights() -> Dict[str, Any]:
        """Returns mocked agent insights and recommendations"""
        return {
            "insights": [
                {
                    "id": 1,
                    "agent": "PerformanceWatcher",
                    "type": "warning",
                    "priority": "HIGH",
                    "message": "Baisse de productivité détectée sur l'équipe A le mardi après-midi",
                    "details": "Analyse des données sur 4 semaines montrant un pattern récurrent. Productivité moyenne: 68% vs 82% habituel.",
                    "affected_kpis": ["tech_productivity"],
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "agent": "QualityGuardian",
                    "type": "success",
                    "priority": "MEDIUM",
                    "message": "Le taux d'inspection a dépassé l'objectif de 20% cette semaine",
                    "details": "Excellente performance suite à la mise en place du nouveau process d'inspection systématique.",
                    "affected_kpis": ["inspection_rate"],
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": 3,
                    "agent": "ProcessOptimizer",
                    "type": "info",
                    "priority": "MEDIUM",
                    "message": "Potentiel goulot d'étranglement identifié à l'étape de validation",
                    "details": "Le temps moyen de validation a augmenté de 15% sur les 2 dernières semaines. Impact sur LLTI.",
                    "affected_kpis": ["llti"],
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": 4,
                    "agent": "DataHarmonizer",
                    "type": "warning",
                    "priority": "LOW",
                    "message": "Incohérences détectées dans les codes M pour 23 enregistrements",
                    "details": "OR de type 'text' vs 'number' sur fichiers ERP. Normalisation automatique appliquée.",
                    "affected_kpis": ["data_quality"],
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "actions": [
                {
                    "id": 101,
                    "title": "Réorganiser les shifts du mardi",
                    "priority": "HIGH",
                    "status": "PROPOSED",
                    "owner": "Manager Equipe A",
                    "description": "Décaler la pause de 15min pour éviter le creux de productivité à 15h.",
                    "estimated_impact": "+5% productivité",
                    "related_insights": [1]
                },
                {
                    "id": 102,
                    "title": "Formation express Inspection",
                    "priority": "MEDIUM",
                    "status": "PROPOSED",
                    "owner": "Responsable Qualité",
                    "description": "Partager les bonnes pratiques de la semaine avec les autres équipes.",
                    "estimated_impact": "+10% inspection rate globale",
                    "related_insights": [2]
                },
                {
                    "id": 103,
                    "title": "Optimiser le workflow de validation",
                    "priority": "MEDIUM",
                    "status": "IN_PROGRESS",
                    "owner": "Chef d'Atelier",
                    "description": "Automatiser les validations simples pour réduire le temps de traitement.",
                    "estimated_impact": "-3 jours LLTI moyen",
                    "related_insights": [3]
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_insights": 4,
                "total_actions": 3
            }
        }
