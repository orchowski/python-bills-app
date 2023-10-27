from typing import List, Optional

import infrastructure.logger as logger
from application.wallet.readmodel.main_dashboard import MainDashboardReadModel


class MainDashboardReadModelRepository:
    __dashboards: List[MainDashboardReadModel]

    def __init__(self):
        self.__dashboards = []

    def save(self, dashboard: MainDashboardReadModel):
        if self.get_by_wallet_id(dashboard.wallet_id):
            self.delete(
                self.get_by_wallet_id(dashboard.wallet_id).wallet_id
            )
        self.__dashboards.append(dashboard)

    def delete(self, wallet_id: str):
        dashboard_to_remove = self.get_by_wallet_id(wallet_id)
        if dashboard_to_remove is not None:
            self.__dashboards.remove(dashboard_to_remove)

    def get_by_wallet_id(self, wallet_id: str) -> Optional[MainDashboardReadModel]:
        hits = list(filter(lambda dashboard: dashboard.wallet_id == wallet_id, self.__dashboards))
        if len(hits) > 1:
            logger.error("for wallet %s more than one dashboard is available", wallet_id)
        if len(hits) == 0:
            return None
        return hits[0]
