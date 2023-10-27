from typing import List, Optional

from application.resource.resource import Resource
from application.resource.resource_store import ResourceStore
from model.commons.aggregate_root import AggregateId
from model.commons.result import Result, Success, Fail
from model.commons.vo.context import Context


class ResourceRepository(ResourceStore):
    __resources: List[Resource]

    def __init__(self):
        self.__resources = []

    def save(self, resource: Resource) -> Result:
        super().save(resource)
        existing_resource_with_the_same_id = next((i for i in self.__resources if i.id == resource.id), None)
        if existing_resource_with_the_same_id is not None:
            # TODO: add update action support.
            return Fail(f"resource with given id({resource.id}) already exists!")

        self.__resources.append(resource)
        return Success()

    def get_by(self, resource_id: AggregateId, context: Context) -> Optional[Resource]:
        results = [resource for resource in self.__resources
                    if resource.id == resource_id
                    and (resource.wallet_id == context.wallet
                         or resource.creator == context.user)
                    ]
        return results[0] if results else None


