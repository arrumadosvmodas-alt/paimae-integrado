from fastapi import APIRouter, status

from app.api.v1.endpoints.study_plan import (
    create_interaction,
    create_interaction_response,
    delete_interaction,
    get_interaction,
    list_interaction_responses,
    list_interactions,
    update_interaction,
    update_interaction_response,
)
from app.schemas.study_plan import InteractionRead, InteractionResponseRead

router = APIRouter()

router.add_api_route("", create_interaction, methods=["POST"], response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
router.add_api_route("", list_interactions, methods=["GET"], response_model=list[InteractionRead])
router.add_api_route("/{interaction_id}", get_interaction, methods=["GET"], response_model=InteractionRead)
router.add_api_route("/{interaction_id}", update_interaction, methods=["PUT"], response_model=InteractionRead)
router.add_api_route("/{interaction_id}", delete_interaction, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT)
router.add_api_route("/{interaction_id}/responses", create_interaction_response, methods=["POST"], response_model=InteractionResponseRead, status_code=status.HTTP_201_CREATED)
router.add_api_route("/{interaction_id}/responses", list_interaction_responses, methods=["GET"], response_model=list[InteractionResponseRead])
router.add_api_route("/responses/{response_id}", update_interaction_response, methods=["PUT"], response_model=InteractionResponseRead)