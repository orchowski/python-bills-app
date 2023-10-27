from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from application.resource.resource import Resource
from model.commons.aggregate_root import AggregateId
from model.commons.result import Result, Success, Fail
from model.commons.vo.context import Context


class ResourceStore(ABC):

    @abstractmethod
    def save(self, resource: Resource) -> Result:
        """
        Saves resource, use super() to check typings            
        """
        if not isinstance(resource, Resource):
            return Fail("resource should be type of Resource")
        return Success()

    @abstractmethod
    def get_by(self, resource_id: AggregateId, context: Context) -> Optional[Resource]:
        return NotImplementedError("implement get by")