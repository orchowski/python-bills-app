import dataclasses

import humps
from flask import Blueprint, jsonify, make_response, request
from pydantic import ValidationError, BaseModel

from application.factory import ApplicationFactory
from model.commitments.commands.add_commitment import AddCommitment
from model.commitments.vo.commitment_id import CommitmentId
from model.commitments.vo.metadata import Metadata
from model.commons.vo.context import Context, WalletId
from model.commons.vo.user_id import UserId
from view.commitments.models.requests.post_commitment import CreateCommitment
from view.commitments.models.requests.put_commitment import UpdateCommitment
from view.helpers.request_helpers import parse_request_body, create_response
from model.commitments.commands.update_commitment import UpdateCommitment as UpdateCommitmentCommand

commitments_router = Blueprint('commitments', __name__)


def app() -> ApplicationFactory:
    return commitments_router.app


def context() -> Context:
    return Context(UserId("testuser"), WalletId())


# TODO: pagination
@commitments_router.route('/commitments', methods=['GET'])
def get_commitments_list():
    commitments = [vars(each) for each in app().commitment_integration_facade().get_all(context())]
    return create_response(commitments, 200)


@commitments_router.route('/commitments', methods=['POST'])
def add_commitment():
    try:
        create_commitment_request = parse_request_body(CreateCommitment, request)
    except ValidationError as e:
        return make_response(e.json(), 400)

    new_id, result = app().commitment_integration_facade().add_new_commitment(
        AddCommitment(
            create_commitment_request.amount,
            create_commitment_request.unit,
            context(),
            Metadata(create_commitment_request.title, create_commitment_request.description),
            create_commitment_request.start_date,
            create_commitment_request.repeat_period,
            create_commitment_request.every_period,
            create_commitment_request.active
        )
    )

    return create_response(
        {"commitment_id": repr(new_id)}, 201
    ) if result.succeded() else create_response(vars(result), 400)

@commitments_router.route('/commitments', methods=['PUT'])
def update_commitment():
    try:
        update_commitment_request = parse_request_body(UpdateCommitment, request)
    except ValidationError as e:
        return make_response(e.json(), 400)

    result = app().commitment_integration_facade().update_commitment(
        UpdateCommitmentCommand(
            id=CommitmentId(update_commitment_request.commitment_id),
            amount=update_commitment_request.amount,
            unit=update_commitment_request.unit,
            context=context(),
            metadata=Metadata(
                title=update_commitment_request.title,
                description=update_commitment_request.description
            ),
            start_date=update_commitment_request.start_date,
            repeat_period=update_commitment_request.repeat_period,
            every_period=update_commitment_request.every_period,
            active=update_commitment_request.active
        )
    )
    return create_response({}, 204) if result.succeded() else create_response({'message': result.details}, 400)
