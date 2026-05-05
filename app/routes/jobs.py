from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas


router = APIRouter(
    tags=["Jobs"]
)


@router.post("/jobs/")
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    print(" CREATE JOB API CALLED")
    print("Received data:", job)

    new_job = models.Job(
        customer_name=job.customer_name,
        location=job.location,
        issue=job.issue,
        priority=job.priority,
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    print(" Saved job ID:", new_job.id)

    return {
        "message": "Job created successfully",
        "job": {
            "id": new_job.id,
            "customer_name": new_job.customer_name,
            "location": new_job.location,
            "issue": new_job.issue,
            "priority": new_job.priority,
            "status": new_job.status,
            "created_at": new_job.created_at,
            "updated_at": new_job.updated_at,
        },
    }


@router.get("/jobs/")
def get_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).order_by(models.Job.id.desc()).all()

    return {
        "message": "Jobs fetched successfully",
        "count": len(jobs),
        "jobs": jobs,
    }


@router.get("/jobs/{job_id}")
def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "message": "Job fetched successfully",
        "job": job,
    }


@router.put("/jobs/{job_id}")
def update_job(job_id: int, job_data: schemas.JobCreate, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.customer_name = job_data.customer_name
    job.location = job_data.location
    job.issue = job_data.issue
    job.priority = job_data.priority

    db.commit()
    db.refresh(job)

    return {
        "message": "Job updated successfully",
        "job": job,
    }


@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully",
        "deleted_job_id": job_id,
    }