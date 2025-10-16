"""
Report generation service module.

This module provides PDF report generation functionality for laboratory samples,
including Certificates of Analysis (COA), Certificates of Conformity (COC), and
daily certificate reports using ReportLab library.
"""

from sqlalchemy.orm import Session, joinedload
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import tempfile
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..models.sample import Sample, Measurement
from ..models.laboratory import Product, Quality, SamplePoint
from ..models.user import User


class ReportService:
    """
    Service class for generating laboratory reports.

    Provides methods for generating various PDF reports including COA, COC,
    and daily certificates with formatted tables and sample information.

    Attributes:
        db (Session): SQLAlchemy database session.
        styles: ReportLab stylesheet for document formatting.
    """

    def __init__(self, db: Session):
        """
        Initialize the report service.

        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db
        self.styles = getSampleStyleSheet()

    async def generate_coa_report(
        self,
        sample_id: int,
        username: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Generate a Certificate of Analysis (COA) PDF report.

        Creates a formatted PDF document with sample information, test results,
        and measurements with pass/fail status based on specification limits.

        Args:
            sample_id (int): ID of the sample to report on.
            username (str): Name of the user generating the report.
            filename (Optional[str]): Custom filename for the PDF. Auto-generated if None.

        Returns:
            str: Path to the generated PDF file.

        Raises:
            ValueError: If the sample is not found.
        """
        # Get sample data with all related information
        sample = await self._get_sample_with_measurements(sample_id)
        
        if not sample:
            raise ValueError(f"Sample {sample_id} not found")

        # Create temporary PDF file
        if not filename:
            filename = f"COA_{sample_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, filename)

        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=1*inch,
            bottomMargin=0.5*inch
        )

        # Build content
        content = []
        
        # Add header
        content.extend(await self._create_coa_header(sample))
        
        # Add sample information
        content.extend(await self._create_sample_info_table(sample))
        
        # Add spacer
        content.append(Spacer(1, 0.2*inch))
        
        # Add measurements table
        content.extend(await self._create_measurements_table(sample))
        
        # Add footer with signatures
        content.extend(await self._create_coa_footer(username))

        # Build PDF
        doc.build(content)
        
        return pdf_path

    async def generate_coc_report(
        self,
        sample_id: int,
        username: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Generate a Certificate of Conformity (COC) PDF report.

        Creates a PDF document certifying that the sample conforms to specifications,
        with sample information and conformity statement.

        Args:
            sample_id (int): ID of the sample to report on.
            username (str): Name of the user generating the report.
            filename (Optional[str]): Custom filename for the PDF. Auto-generated if None.

        Returns:
            str: Path to the generated PDF file.

        Raises:
            ValueError: If the sample is not found.
        """
        # Similar to COA but with COC-specific formatting
        sample = await self._get_sample_with_measurements(sample_id)
        
        if not sample:
            raise ValueError(f"Sample {sample_id} not found")

        if not filename:
            filename = f"COC_{sample_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, filename)

        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        content = []
        
        # Add COC-specific header
        content.extend(await self._create_coc_header(sample))
        
        # Add sample information
        content.extend(await self._create_sample_info_table(sample))
        
        # Add conformity statement
        content.extend(await self._create_conformity_statement(sample))
        
        # Add footer
        content.extend(await self._create_coc_footer(username))

        doc.build(content)
        return pdf_path

    async def generate_day_certificate_report(
        self,
        report_date: str,
        username: str
    ) -> str:
        """
        Generate a daily certificate report for all samples on a given date.

        Creates a landscape PDF with a summary table of all samples collected
        on the specified date.

        Args:
            report_date (str): Date for the report (YYYY-MM-DD format).
            username (str): Name of the user generating the report.

        Returns:
            str: Path to the generated PDF file.
        """
        # Get all samples for the specified date
        samples = await self._get_samples_by_date(report_date)
        
        filename = f"DayCertificate_{report_date}.pdf"
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, filename)

        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
        content = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        content.append(Paragraph(f"Daily Certificate Report - {report_date}", title_style))
        
        # Add samples summary table
        content.extend(await self._create_daily_summary_table(samples))

        doc.build(content)
        return pdf_path

    async def _get_sample_with_measurements(self, sample_id: int) -> Optional[Dict[str, Any]]:
        sample = (
            self.db.query(Sample)
            .options(
                joinedload(Sample.product),
                joinedload(Sample.quality),
                joinedload(Sample.sample_point),
                joinedload(Sample.created_by),
                joinedload(Sample.measurements)
            )
            .filter(Sample.id == sample_id)
            .first()
        )

        if not sample:
            return None

        # Convert to dictionary with all related data
        return {
            "id": sample.id,
            "sample_number": sample.sample_number,
            "product": sample.product.name if sample.product else "",
            "quality": sample.quality.name if sample.quality else "",
            "sample_point": sample.sample_point.name if sample.sample_point else "",
            "sample_date": sample.date,
            "sample_time": sample.time,
            "customer": sample.customer,
            "batch_number": sample.batch_number,
            "container_number": sample.container_number,
            "loading_ton": float(sample.loading_ton) if sample.loading_ton else None,
            "measurements": [
                {
                    "variable": m.variable,
                    "value": float(m.value) if m.value else None,
                    "min_value": float(m.min_value) if m.min_value else None,
                    "max_value": float(m.max_value) if m.max_value else None,
                    "test_date": m.test_date
                }
                for m in sample.measurements
            ]
        }

    async def _get_samples_by_date(self, report_date: str) -> List[Dict[str, Any]]:
        samples = (
            self.db.query(Sample)
            .options(
                joinedload(Sample.product),
                joinedload(Sample.quality),
                joinedload(Sample.sample_point)
            )
            .filter(Sample.date == report_date)
            .all()
        )

        return [
            {
                "id": sample.id,
                "sample_number": sample.sample_number,
                "product": sample.product.name if sample.product else "",
                "quality": sample.quality.name if sample.quality else "",
                "sample_point": sample.sample_point.name if sample.sample_point else "",
                "customer": sample.customer
            }
            for sample in samples
        ]

    async def _create_coa_header(self, sample: Dict[str, Any]) -> List:
        content = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1
        )
        
        content.append(Paragraph("CERTIFICATE OF ANALYSIS", title_style))
        content.append(Spacer(1, 0.2*inch))
        
        return content

    async def _create_coc_header(self, sample: Dict[str, Any]) -> List:
        content = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1
        )
        
        content.append(Paragraph("CERTIFICATE OF CONFORMITY", title_style))
        content.append(Spacer(1, 0.2*inch))
        
        return content

    async def _create_sample_info_table(self, sample: Dict[str, Any]) -> List:
        content = []
        
        # Sample information table
        data = [
            ['Sample Number:', sample.get('sample_number', 'N/A')],
            ['Product:', sample.get('product', 'N/A')],
            ['Quality:', sample.get('quality', 'N/A')],
            ['Sample Point:', sample.get('sample_point', 'N/A')],
            ['Sample Date:', sample.get('sample_date', 'N/A')],
            ['Sample Time:', sample.get('sample_time', 'N/A')],
            ['Customer:', sample.get('customer', 'N/A')],
            ['Batch Number:', sample.get('batch_number', 'N/A')],
        ]

        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        content.append(table)
        return content

    async def _create_measurements_table(self, sample: Dict[str, Any]) -> List:
        content = []
        
        # Measurements table
        measurements = sample.get('measurements', [])
        
        if measurements:
            # Table header
            data = [['Test Parameter', 'Result', 'Unit', 'Min Limit', 'Max Limit', 'Status']]
            
            for measurement in measurements:
                value = measurement.get('value')
                min_val = measurement.get('min_value')
                max_val = measurement.get('max_value')
                
                # Determine status
                status = 'PASS'
                if value is not None:
                    if min_val is not None and value < min_val:
                        status = 'FAIL'
                    elif max_val is not None and value > max_val:
                        status = 'FAIL'
                
                data.append([
                    measurement.get('variable', ''),
                    str(value) if value is not None else 'N/A',
                    '',  # Unit would come from variable definition
                    str(min_val) if min_val is not None else 'N/A',
                    str(max_val) if max_val is not None else 'N/A',
                    status
                ])

            table = Table(data, colWidths=[2*inch, 1*inch, 0.8*inch, 1*inch, 1*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ]))

            content.append(table)
        
        return content

    async def _create_conformity_statement(self, sample: Dict[str, Any]) -> List:
        content = []
        
        content.append(Spacer(1, 0.3*inch))
        
        statement_style = ParagraphStyle(
            'Statement',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            alignment=1
        )
        
        statement = """
        This is to certify that the above mentioned product conforms to the 
        specification requirements and has been manufactured under our quality 
        control system.
        """
        
        content.append(Paragraph(statement, statement_style))
        
        return content

    async def _create_coa_footer(self, username: str) -> List:
        content = []
        
        content.append(Spacer(1, 0.5*inch))
        
        # Signature section
        signature_data = [
            ['Tested by:', 'Approved by:'],
            ['', ''],
            [f'{username}', 'Laboratory Manager'],
            [f'Date: {datetime.now().strftime("%Y-%m-%d")}', f'Date: {datetime.now().strftime("%Y-%m-%d")}']
        ]

        signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ]))

        content.append(signature_table)
        
        return content

    async def _create_coc_footer(self, username: str) -> List:
        return await self._create_coa_footer(username)

    async def _create_daily_summary_table(self, samples: List[Dict[str, Any]]) -> List:
        content = []
        
        if samples:
            data = [['Sample Number', 'Product', 'Quality', 'Sample Point', 'Customer']]
            
            for sample in samples:
                data.append([
                    sample.get('sample_number', ''),
                    sample.get('product', ''),
                    sample.get('quality', ''),
                    sample.get('sample_point', ''),
                    sample.get('customer', '')
                ])

            table = Table(data, colWidths=[1.5*inch, 2*inch, 2*inch, 1.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ]))

            content.append(table)
        else:
            content.append(Paragraph("No samples found for the specified date.", self.styles['Normal']))
        
        return content