from typing import Annotated

from fastapi import Depends, Request

from src.infra.container import Container


def get_container(request: Request) -> Container:
    return request.app.state.container


ContainerDep = Annotated[Container, Depends(get_container)]
