"""
Samples API endpoints module.

This module defines FastAPI routes for managing laboratory samples including
creation, retrieval, measurement management, and automated sample loading
from logistic data. Supports production, customer, and manual samples.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from ..database.connection import get_db
from ..services.sample_service import SampleService
from ..services.sample_loading_service import SampleLoadingService
from ..services.auth_service import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/samples", tags=["samples"])


class SampleResponse(BaseModel):
    id: int
    sample_number: Optional[str]
    product: str
    quality: str
    sample_point: Optional[str]
    sample_date: Optional[str]
    sample_time: Optional[str]
    remark: Optional[str]
    coa: Optional[str]
    day_coa: Optional[str]
    coc: Optional[str]
    type_sample: str

    class Config:
        from_attributes = True


class SampleCreateRequest(BaseModel):
    type_sample: str  # PRO, CLI, MAN
    product_id: int
    quality_id: int
    sample_point_id: Optional[int] = None
    description: Optional[str] = None
    remark: Optional[str] = None
    customer: Optional[str] = None
    order_number_client: Optional[str] = None


class MeasurementResponse(BaseModel):
    id: int
    variable: str
    value: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    test_date: Optional[str]
    tested_by: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SampleResponse])
async def get_samples(
    sample_date: Optional[str] = Query(None, description="Sample date (YYYY-MM-DD)"),
    type_sample: Optional[str] = Query(None, description="Sample type: PRO, CLI, MAN"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    samples = await sample_service.get_samples(
        sample_date=sample_date,
        type_sample=type_sample
    )
    return samples


@router.post("/", response_model=SampleResponse)
async def create_sample(
    sample_data: SampleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    sample = await sample_service.create_sample(sample_data, current_user.id)
    return sample


@router.get("/{sample_id}", response_model=SampleResponse)
async def get_sample(
    sample_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    sample = await sample_service.get_sample_by_id(sample_id)
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found"
        )
    
    return sample


@router.get("/{sample_id}/measurements", response_model=List[MeasurementResponse])
async def get_sample_measurements(
    sample_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    measurements = await sample_service.get_sample_measurements(sample_id)
    return measurements


@router.post("/{sample_id}/measurements")
async def add_measurement(
    sample_id: int,
    variable: str,
    value: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    measurement = await sample_service.add_measurement(
        sample_id=sample_id,
        variable=variable,
        value=value,
        tested_by_id=current_user.id
    )
    return {"message": "Measurement added successfully", "id": measurement.id}


@router.post("/{sample_id}/refresh")
async def refresh_sample_specifications(
    sample_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    await sample_service.refresh_sample_specifications(sample_id)
    return {"message": "Sample specifications refreshed successfully"}


@router.get("/{sample_id}/status")
async def get_sample_status(
    sample_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    status_info = await sample_service.get_sample_completion_status(sample_id)
    return status_info


@router.post("/load-customer-samples")
async def load_customer_samples(
    sample_date: str = Query(..., description="Sample date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Load customer samples from logistic data for the specified date.

    This endpoint:
    - Retrieves logistic data for the given date
    - Validates article codes against the map table
    - Checks for customer specifications
    - Creates or updates customer samples
    - Creates measurements based on specifications

    Migrated from MATLAB function: loadCustomerSample.m
    """
    loading_service = SampleLoadingService(db)
    result = await loading_service.load_customer_samples(
        sample_date=sample_date,
        user_id=current_user.id
    )

    if not result['success'] and result.get('errors'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Customer samples loaded with errors",
                "errors": result['errors'],
                "pending_data": result.get('pending_data')
            }
        )

    return {
        "message": result['message'],
        "success": result['success'],
        "errors": result.get('errors'),
        "pending_data": result.get('pending_data')
    }


@router.post("/load-production-samples")
async def load_production_samples(
    sample_date: str = Query(..., description="Sample date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate production samples based on sample matrix and frequency for the specified date.

    This endpoint:
    - Checks if the date is the first day of any period (semester, quarter, month, week)
    - Generates samples based on the sample matrix for matching frequencies
    - Always generates daily samples
    - Creates measurements based on specifications

    Migrated from MATLAB function: loadProductionSample.m
    """
    loading_service = SampleLoadingService(db)
    result = await loading_service.load_production_samples(
        sample_date=sample_date,
        user_id=current_user.id
    )

    if not result['success'] and result.get('errors'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Production samples loaded with errors",
                "errors": result['errors']
            }
        )

    return {
        "message": result['message'],
        "success": result['success'],
        "errors": result.get('errors')
    }