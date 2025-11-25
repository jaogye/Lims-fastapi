"""
Samples API endpoints module.

This module defines FastAPI routes for managing laboratory samples including
creation, retrieval, measurement management, and automated sample loading
from logistic data. Supports production, customer, and manual samples.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
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


class QualityInfoItem(BaseModel):
    variable: str
    min: Optional[float]
    max: Optional[float]
    value: Optional[float]


class SampleDetailResponse(BaseModel):
    sample_number: str
    customer_name: Optional[str]
    product: str
    quality: str
    tank: Optional[str]
    sample_date: str
    orderPVS: Optional[str]
    orderclient: Optional[str]
    batch_number: Optional[str]
    container_number: Optional[str]
    remark: Optional[str]
    sample_product_id: Optional[int]
    sample_quality_id: Optional[int]
    sample_samplepoint_id: Optional[int]
    sample_certificate: Optional[str]
    sample_coa: Optional[str]
    sample_coc: Optional[str]
    sample_day_coa: Optional[str]
    quality_info: List[QualityInfoItem]


class SampleUpdateRequest(BaseModel):
    sample_number: str
    customer_name: Optional[str]
    product: str
    quality: str
    tank: Optional[str]
    sample_date: str
    orderPVS: Optional[str]
    orderclient: Optional[str]
    batch_number: Optional[str]
    container_number: Optional[str]
    remark: Optional[str]
    sample_product_id: Optional[int] = None
    sample_quality_id: Optional[int] = None
    sample_samplepoint_id: Optional[int] = None
    sample_certificate: Optional[str] = None
    sample_coa: Optional[str] = None
    sample_coc: Optional[str] = None
    sample_day_coa: Optional[str] = None
    quality_info: List[QualityInfoItem]


@router.get("/get_samples", response_model=List[SampleDetailResponse])
async def get_samples_detailed(
    sample_date: str = Query(..., description="Sample date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get samples for a specific date with measurements (CLI and MAN types only).

    Args:
        sample_date: Date in YYYY-MM-DD format

    Returns:
        List of samples with their measurements
    """
    sample_service = SampleService(db)
    samples = await sample_service.get_samples_with_measurements(sample_date=sample_date)
    return samples


@router.post("/update_samples")
async def update_samples(
    samples: List[SampleUpdateRequest] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update samples and their measurements with validation.

    Validates that all measurement values are within the allowed min/max range
    before updating. If any value is out of range, raises an error.

    Args:
        samples: List of samples to update

    Returns:
        Success message with update count
    """
    sample_service = SampleService(db)
    # Convert Pydantic models to dictionaries
    samples_dict = [sample.model_dump() for sample in samples]
    result = await sample_service.update_samples_batch(samples=samples_dict)
    return result


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


@router.post("/create-sample")
async def create_sample(
    sample_date: str = Query(..., description="Sample date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Combined endpoint that loads both customer and production samples for the specified date.

    This endpoint:
    - First loads customer samples from logistic data
    - Then generates production samples based on sample matrix and frequency
    - Returns combined results from both operations

    Args:
        sample_date: Date in YYYY-MM-DD format for which to load samples

    Returns:
        Combined results containing success status, messages, and any errors from both operations
    """
    loading_service = SampleLoadingService(db)

    # Load customer samples
    customer_result = await loading_service.load_customer_samples(
        sample_date=sample_date,
        user_id=current_user.id
    )

    # Load production samples
    production_result = await loading_service.load_production_samples(
        sample_date=sample_date,
        user_id=current_user.id
    )

    # Combine results
    combined_success = customer_result['success'] and production_result['success']
    combined_errors = []

    if customer_result.get('errors'):
        combined_errors.extend([f"Customer: {err}" for err in customer_result['errors']])

    if production_result.get('errors'):
        combined_errors.extend([f"Production: {err}" for err in production_result['errors']])

    response = {
        "message": "Combined sample loading completed",
        "success": combined_success,
        "customer_result": {
            "message": customer_result['message'],
            "success": customer_result['success'],
            "errors": customer_result.get('errors'),
            "pending_data": customer_result.get('pending_data')
        },
        "production_result": {
            "message": production_result['message'],
            "success": production_result['success'],
            "errors": production_result.get('errors')
        }
    }

    if combined_errors:
        response["combined_errors"] = combined_errors

    # Raise exception if both operations failed
    if not combined_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response
        )

    return response


@router.post("/{sample_number}/refresh")
async def refresh_sample_specifications(
    sample_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    measurement = await sample_service.refresh_sample_specifications(sample_number)
    return {"message": "Sample specifications refreshed successfully", "measurement":measurement}


@router.get("/{sample_number}/status")
async def get_sample_status(
    sample_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    status_info = await sample_service.get_sample_completion_status(sample_number)
    return status_info



"""

@router.post("/", response_model=SampleResponse)
async def create_sample(
    sample_data: SampleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    sample = await sample_service.create_sample(sample_data, current_user.id)
    return sample



@router.get("/{sample_number}", response_model=SampleResponse)
async def get_sample(
    sample_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    sample = await sample_service.get_sample_by_id(sample_number)

    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found"
        )

    return sample


@router.get("/{sample_number}/measurements", response_model=List[MeasurementResponse])
async def get_sample_measurements(
    sample_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    measurements = await sample_service.get_sample_measurements(sample_number)
    return measurements


@router.post("/{sample_number}/measurements")
async def add_measurement(
    sample_number: str,
    variable: str,
    value: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sample_service = SampleService(db)
    measurement = await sample_service.add_measurement(
        sample_number=sample_number,
        variable=variable,
        value=value,
        tested_by_id=current_user.id
    )
    return {"message": "Measurement added successfully", "id": measurement.id}


"""
