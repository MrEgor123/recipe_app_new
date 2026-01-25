from fastapi import HTTPException


def not_found(entity: str, entity_id: int) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail=f"{entity} with id {entity_id} not found",
    )
