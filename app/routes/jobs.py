from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app import models, schemas


router = APIRouter(
    tags=["Jobs"]
)


@router.post("/jobs/", status_code=status.HTTP_200_OK)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    try:
        new_job = models.Job(
            customer_name=job.customer_name,
            location=job.location,
            issue=job.issue,
            priority=job.priority,
            status="pending",
            is_deleted=False,
            is_saved=False
        )

        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        return {
            "message": "Job created successfully",
            "job_id": new_job.id,
            "job": {
                "id": new_job.id,
                "customer_name": new_job.customer_name,
                "location": new_job.location,
                "issue": new_job.issue,
                "priority": new_job.priority,
                "status": new_job.status,
                "is_deleted": new_job.is_deleted,
                "is_saved": new_job.is_saved,
                "created_at": new_job.created_at,
                "updated_at": new_job.updated_at,
            },
        }

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating job"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.get("/jobs/")
def get_all_jobs(db: Session = Depends(get_db)):
    try:
        jobs = (
            db.query(models.Job)
            .filter(models.Job.is_deleted == False, models.Job.status != "cancelled")
            .order_by(models.Job.id.desc())
            .all()
        )

        return {
            "message": "Active jobs fetched successfully",
            "count": len(jobs),
            "jobs": jobs,
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching jobs"
        )


@router.get("/jobs/saved")
def get_saved_jobs(db: Session = Depends(get_db)):
    try:
        jobs = (
            db.query(models.Job)
            .filter(
                models.Job.is_deleted == False,
                models.Job.is_saved == True,
                models.Job.status != "cancelled"
            )
            .order_by(models.Job.id.desc())
            .all()
        )

        return {
            "message": "Saved jobs fetched successfully",
            "count": len(jobs),
            "jobs": jobs,
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching saved jobs"
        )


@router.get("/jobs/{job_id}")
def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    try:
        job = (
            db.query(models.Job)
            .filter(models.Job.id == job_id, models.Job.is_deleted == False)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        return {
            "message": "Job fetched successfully",
            "job": job,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching job"
        )


@router.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    job_data: schemas.JobUpdate,
    db: Session = Depends(get_db)
):
    try:
        job = (
            db.query(models.Job)
            .filter(models.Job.id == job_id, models.Job.is_deleted == False)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        job.customer_name = job_data.customer_name
        job.location = job_data.location
        job.issue = job_data.issue
        job.priority = job_data.priority
        job.status = job_data.status

        db.commit()
        db.refresh(job)

        return {
            "message": "Job updated successfully",
            "job_id": job.id,
            "job": {
                "id": job.id,
                "customer_name": job.customer_name,
                "location": job.location,
                "issue": job.issue,
                "priority": job.priority,
                "status": job.status,
                "is_deleted": job.is_deleted,
                "is_saved": job.is_saved,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
            },
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating job"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating job"
        )


@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """
    Soft delete job.

    This will not permanently delete the job from PostgreSQL.
    It only changes is_deleted from False to True.
    """

    try:
        job = (
            db.query(models.Job)
            .filter(models.Job.id == job_id, models.Job.is_deleted == False)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        job.is_deleted = True

        db.commit()
        db.refresh(job)

        return {
            "message": "Job removed from active dashboard successfully",
            "deleted_job_id": job.id,
            "job": {
                "id": job.id,
                "customer_name": job.customer_name,
                "location": job.location,
                "issue": job.issue,
                "priority": job.priority,
                "status": job.status,
                "is_deleted": job.is_deleted,
                "is_saved": job.is_saved,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
            },
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while deleting job"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while deleting job"
        )


@router.put("/jobs/{job_id}/cancel")
def cancel_job(job_id: int, db: Session = Depends(get_db)):
    try:
        job = (
            db.query(models.Job)
            .filter(models.Job.id == job_id, models.Job.is_deleted == False)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        job.status = "cancelled"
        db.commit()
        db.refresh(job)

        return {
            "message": "Job cancelled successfully",
            "job_id": job.id,
            "job": {
                "id": job.id,
                "customer_name": job.customer_name,
                "location": job.location,
                "issue": job.issue,
                "priority": job.priority,
                "status": job.status,
                "is_deleted": job.is_deleted,
                "is_saved": job.is_saved,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
            },
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while cancelling job"
        )


@router.put("/jobs/{job_id}/save")
def save_job(job_id: int, db: Session = Depends(get_db)):
    try:
        job = (
            db.query(models.Job)
            .filter(models.Job.id == job_id, models.Job.is_deleted == False)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        if job.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cancelled job cannot be saved"
            )

        job.is_saved = True
        db.commit()
        db.refresh(job)

        return {
            "message": "Job saved successfully",
            "job_id": job.id,
            "job": {
                "id": job.id,
                "customer_name": job.customer_name,
                "location": job.location,
                "issue": job.issue,
                "priority": job.priority,
                "status": job.status,
                "is_deleted": job.is_deleted,
                "is_saved": job.is_saved,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
            },
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while saving job"
        )


@router.put("/jobs/{job_id}/unsave")
def unsave_job(job_id: int, db: Session = Depends(get_db)):
    try:
        job = (
            db.query(models.Job)
            .filter(models.Job.id == job_id, models.Job.is_deleted == False)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        job.is_saved = False
        db.commit()
        db.refresh(job)

        return {
            "message": "Job unsaved successfully",
            "job_id": job.id,
            "job": {
                "id": job.id,
                "customer_name": job.customer_name,
                "location": job.location,
                "issue": job.issue,
                "priority": job.priority,
                "status": job.status,
                "is_deleted": job.is_deleted,
                "is_saved": job.is_saved,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
            },
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while unsaving job"
        )