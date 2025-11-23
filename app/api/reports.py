"""
Report API endpoints module.

This module defines FastAPI routes for generating PDF reports including
Certificates of Analysis (COA), Certificates of Conformity (COC), and
daily certificate reports.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from ..database.connection import get_db
from ..services.report_service import ReportService
from ..services.auth_service import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportRequest(BaseModel):
    sample_number: str
    report_type: str  # COA, COC, DAY_COA
    filename: Optional[str] = None


@router.get("/coa/{sample_number}")
async def generate_coa_report(
    sample_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report_service = ReportService(db)
    
    try:
        pdf_path = await report_service.generate_coa_report(
            sample_number=sample_number,
            username=current_user.name
        )
        
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=f"COA_{sample_number}.pdf"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating COA report: {str(e)}"
        )


@router.get("/coc/{sample_number}")
async def generate_coc_report(
    sample_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report_service = ReportService(db)
    
    try:
        pdf_path = await report_service.generate_coc_report(
            sample_number=sample_number,
            username=current_user.name
        )
        
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=f"COC_{sample_number}.pdf"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating COC report: {str(e)}"
        )


@router.get("/day-certificate/{sample_number}")
async def generate_day_certificate_report(
    sample_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report_service = ReportService(db)
    
    try:
        pdf_path = await report_service.generate_day_certificate_report(
            sample_number=sample_number,
            username=current_user.name
        )
        
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=f"DayCertificate_{sample_number}.pdf"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating day certificate report: {str(e)}"
        )

"""

@router.post("/generate")
async def generate_custom_report(
    report_request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report_service = ReportService(db)
    
    try:
        if report_request.report_type == "COA":
            pdf_path = await report_service.generate_coa_report(
                sample_number=report_request.sample_number,
                username=current_user.name,
                filename=report_request.filename
            )
        elif report_request.report_type == "COC":
            pdf_path = await report_service.generate_coc_report(
                sample_number=report_request.sample_number,
                username=current_user.name,
                filename=report_request.filename
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported report type: {report_request.report_type}"
            )

        filename = report_request.filename or f"{report_request.report_type}_{report_request.sample_number}.pdf"

        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )
"""