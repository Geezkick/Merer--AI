from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Dataset, Project
from app.schemas.dataset import DatasetCreate, DatasetResponse

router = APIRouter(
    prefix="/organizations/{organization_id}/projects/{project_id}/datasets",
    tags=["Datasets"],
)


def get_project(
    organization_id: UUID,
    project_id: UUID,
    db: Session,
):
    statement = select(Project).where(
        Project.id == project_id,
        Project.organization_id == organization_id,
    )

    project = db.scalar(statement)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in this organization.",
        )

    return project


@router.post(
    "",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dataset(
    organization_id: UUID,
    project_id: UUID,
    payload: DatasetCreate,
    db: Session = Depends(get_db),
):
    get_project(organization_id, project_id, db)

    dataset = Dataset(
        project_id=project_id,
        name=payload.name,
        description=payload.description,
    )

    db.add(dataset)

    try:
        db.commit()
        db.refresh(dataset)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A dataset with this name already exists in this project.",
        )

    return dataset


@router.get("", response_model=list[DatasetResponse])
def list_datasets(
    organization_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
):
    get_project(organization_id, project_id, db)

    statement = (
        select(Dataset)
        .where(Dataset.project_id == project_id)
        .order_by(Dataset.created_at.desc())
    )

    return db.scalars(statement).all()
