"""
Master data API endpoints module.

This module defines FastAPI routes for managing master data including
products, qualities, variables, specifications, and sample matrices.
Provides Excel import/export functionality for batch data management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os
import tempfile

from ..database.connection import get_db
from ..services.master_data_service import MasterDataService, MasterDataQuery
from ..services.auth_service import get_current_user
from ..models.user import User
import openpyxl

router = APIRouter(prefix="/api/master-data", tags=["master-data"])

class ProductResponse(BaseModel):
    id: int
    name: str
    bruto: Optional[str]

    class Config:
        from_attributes = True


class QualityResponse(BaseModel):
    id: int
    name: str
    long_name: Optional[str]

    class Config:
        from_attributes = True


class VariableResponse(BaseModel):
    id: int
    short_name: str
    test: str
    element: Optional[str]
    unit: Optional[str]
    ord: Optional[int]

    class Config:
        from_attributes = True


class SamplePointResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True



@router.get("/download/{table_type}")
async def download_master_data_template(
    table_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    master_data_query = MasterDataQuery(db)
    
    try:
        excel_path = await master_data_query.export_to_excel(table_type)
        
        return FileResponse(
            path=excel_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f"{table_type}.xlsx"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Excel file: {str(e)}"
        )


@router.post("/upload")
async def upload_master_data(
    table_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can upload master data"
        )

    master_data_service = MasterDataService(db)

    try:
        # Validate file format
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Excel files (.xlsx, .xls) are supported"
            )

        # Process the uploaded file
        result = await master_data_service.import_from_excel(
            file=file,
            table_type=table_type
        )

        response = {
            "message": "Master data processing completed",
            "processed_records": result["processed"],
            "errors": result.get("errors", []),
            "has_errors": result.get("has_errors", False)
        }

        # Add error file download link if available
        if result.get("error_file"):
            response["error_file_url"] = f"/api/master-data/download-errors/{result['error_file']}"

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Excel file: \n {str(e)}"
        )


@router.get("/download-errors/{filename}")
async def download_error_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Download the Excel file containing non-processed rows"""
    try:
        # Get the file path from temp directory
        persistent_dir = tempfile.gettempdir()
        file_path = os.path.join(persistent_dir, filename)

        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error file not found or has expired"
            )

        # Return the file
        return FileResponse(
            path=file_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading error file: {str(e)}"
        )


