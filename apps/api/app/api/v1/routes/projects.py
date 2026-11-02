from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Organization, Project
from app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter(
    prefix="/organizations/{organization_id}/projects",
    tags=["Projects"],
)


def get_existing_organization(
    organization_id: UUID,
    db: Session,
):
    organization = db.get(Organization, organization_id)

    if organization is None or not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active organization not found.",
        )

    return organization


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    organization_id: UUID,
    payload: ProjectCreate,
    db: Session = Depends(get_db),
):
    get_existing_organization(organization_id, db)

    project = Project(
        organization_id=organization_id,
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
    )

    db.add(project)

    try:
        db.commit()
        db.refresh(project)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A project with this slug already exists in this organization.",
        )

    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    get_existing_organization(organization_id, db)

    statement = (
        select(Project)
        .where(Project.organization_id == organization_id)
        .order_by(Project.created_at.desc())
    )

    return db.scalars(statement).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    organization_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
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
