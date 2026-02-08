from datetime import datetime

class MockAgentService:
    @staticmethod
    def get_analysis():
        """
        Retourne des données mockées pour l'interface de démo.
        Structure: KPIs, Insights (Agents), Actions (Lean).
        """
        return {
            "kpis": {
                "productivity": {
                    "value": 85.0,
                    "target": 90.0,
                    "unit": "%",
                    "trend": "down",
                    "label": "Productivité Globale"
                },
                "inspection": {
                    "value": 120,
                    "target": 100,
                    "unit": "dossiers",
                    "trend": "up",
                    "label": "Dossiers Inspectés"
                },
                "llti": {
                    "value": 4.5,
                    "target": 3.0,
                    "unit": "jours",
                    "trend": "down",
                    "label": "LLTI Moyen"
                }
            },
            "insights": [
                {
                    "id": 1,
                    "agent": "PerformanceWatcher",
                    "type": "warning",
                    "message": "Baisse de productivité détectée sur l'équipe A le mardi après-midi.",
                    "details": "Analyse des données sur 4 semaines montrant un pattern récurrent."
                },
                {
                    "id": 2,
                    "agent": "QualityGuardian",
                    "type": "success",
                    "message": "Le taux d'inspection a dépassé l'objectif de 20% cette semaine.",
                    "details": "Excellente performance suite à la mise en place du nouveau process."
                },
                {
                    "id": 3,
                    "agent": "ProcessOptimizer",
                    "type": "info",
                    "message": "Potentiel goulot d'étranglement identifié à l'étape de validation.",
                    "details": "Le temps moyen de validation a augmenté de 15%."
                }
            ],
            "actions": [
                {
                    "id": 101,
                    "title": "Réorganiser les shifts du mardi",
                    "priority": "High",
                    "status": "Proposed",
                    "owner": "Manager Equipe A",
                    "description": "Décaler la pause de 15min pour éviter le creux de 15h."
                },
                {
                    "id": 102,
                    "title": "Formation express Inspection",
                    "priority": "Medium",
                    "status": "Proposed",
                    "owner": "Responsable Qualité",
                    "description": "Partager les bonnes pratiques de la semaine avec les autres équipes."
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "mode": "MOCK"
            }
        }
