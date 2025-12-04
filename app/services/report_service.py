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
from ..models.laboratory import Product, Quality, SamplePoint, Variable
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
        sample_number: str,
        username: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Generate a Certificate of Analysis (COA) PDF report.

        Creates a formatted PDF document with sample information, test results,
        and measurements with pass/fail status based on specification limits.

        Args:
            sample_number (str): Number of the sample to report on.
            username (str): Name of the user generating the report.
            filename (Optional[str]): Custom filename for the PDF. Auto-generated if None.

        Returns:
            str: Path to the generated PDF file.

        Raises:
            ValueError: If the sample is not found.
        """
        # Get sample data with all related information
        sample = await self._get_sample_with_measurements(sample_number)
        
        if not sample:
            raise ValueError(f"Sample {sample_number} not found")

        # Create temporary PDF file
        if not filename:
            filename = f"COA_{sample_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
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
        sample_number: str,
        username: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Generate a Certificate of Conformity (COC) PDF report.

        Creates a PDF document certifying that the sample conforms to specifications,
        with sample information and conformity statement.

        Args:
            sample_number (str): Numbrer of the sample to report on.
            username (str): Name of the user generating the report.
            filename (Optional[str]): Custom filename for the PDF. Auto-generated if None.

        Returns:
            str: Path to the generated PDF file.

        Raises:
            ValueError: If the sample is not found.
        """
        # Similar to COA but with COC-specific formatting
        sample = await self._get_sample_with_measurements(sample_number)
        
        if not sample:
            raise ValueError(f"Sample {sample_number} not found")

        if not filename:
            filename = f"COC_{sample_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
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
        sample_number: str,
        username: str
    ) -> str:
        """
        Generate a day certificate report for a specific sample.

        Creates a portrait PDF with company header, sample information,
        measurements table, and signature section matching the template format.

        Args:
            sample_number (str): Sample number for the report.
            username (str): Name of the user generating the report.

        Returns:
            str: Path to the generated PDF file.
        """
        # Get sample data
        sample_data = await self._get_COA_Data(sample_number)

        if not sample_data:
            raise ValueError(f"Sample {sample_number} not found")

        filename = f"DayCertificate_{sample_number}.pdf"
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        content = []

        # Add company header
        content.extend(await self._create_day_certificate_header())

        # Add title
        title_style = ParagraphStyle(
            'DayTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=20,
            spaceBefore=10,
            alignment=0  # Left alignment
        )
        content.append(Paragraph("Day Certificate", title_style))
        content.append(Spacer(1, 0.3*inch))

        # Add sample information
        content.extend(await self._create_day_certificate_sample_info(sample_data))

        # Add spacer
        content.append(Spacer(1, 0.3*inch))

        # Add measurements table
        content.extend(await self._create_day_certificate_measurements_table(sample_data))

        # Add footer with quality control note and signatures
        content.extend(await self._create_day_certificate_footer(username))

        doc.build(content)
        return pdf_path

    async def _get_sample_with_measurements(self, sample_number: str) -> Optional[Dict[str, Any]]:
        sample = (
            self.db.query(Sample)
            .options(
                joinedload(Sample.product),
                joinedload(Sample.quality),
                joinedload(Sample.sample_point),
                joinedload(Sample.created_by),
                joinedload(Sample.measurements)
            )
            .filter(Sample.sample_number == sample_number)
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
                    "variable": m.variable.name if m.variable else "",
                    "unit": m.variable.unit if m.variable else "",
                    "value": float(m.value) if m.value else None,
                    "min_value": float(m.min_value) if m.min_value else None,
                    "max_value": float(m.max_value) if m.max_value else None,
                    "test_date": m.test_date
                }
                for m in sample.measurements
            ]
        }
        
    async def _get_COA_Data(self, sample_number: str) -> Dict[str, Any]:
        """
        Get Certificate of Analysis data for a sample.

        Translates MATLAB getCOAData function to Python.
        Retrieves sample information and measurements from the database
        by joining sample, product, quality, measurement, and variable tables.

        Args:
            sample_number (str): The sample number to retrieve data for.

        Returns:
            Dict[str, Any]: Dictionary containing 'sample' and 'measurements' data.
        """
        from sqlalchemy import func

        # First query: Get sample information with product and quality
        # Equivalent to MATLAB's first SELECT statement
        sample_query = (
            self.db.query(
                Product.name_coa.label('grade'),
                Quality.long_name.label('technical_grade'),
                Sample.customer,
                Sample.order_number_pvs,
                Sample.order_number_client,
                func.substring(Sample.date, 1, 10).label('sample_date'),
                Product.bruto,
                Sample.batch_number,
                Sample.container_number
            )
            .join(Product, Sample.product_id == Product.id)
            .join(Quality, Sample.quality_id == Quality.id)
            .filter(Sample.sample_number == sample_number)
            .first()
        )

        if not sample_query:
            return None

        # Convert sample query result to dictionary
        sample_data = {
            'grade': sample_query.grade,
            'technical_grade': sample_query.technical_grade,
            'customer': sample_query.customer,
            'order_number_pvs': sample_query.order_number_pvs,
            'order_number_client': sample_query.order_number_client,
            'sample_date': sample_query.sample_date,
            'bruto': sample_query.bruto,
            'batch_number': sample_query.batch_number,
            'container_number': sample_query.container_number
        }

        # Second query: Get measurements with variable information
        # Equivalent to MATLAB's second SELECT statement
        measurements_query = (
            self.db.query(
                Variable.test,
                Variable.element,
                Measurement.value.label('test_results'),
                Measurement.min_value,
                Measurement.max_value,
                Variable.unit,
                Measurement.less,
                Variable.typevar,
                Measurement.test_date
            )
            .join(Sample, Measurement.sample_id == Sample.id)
            .join(Variable, Measurement.variable_id == Variable.id)
            .filter(Sample.sample_number == sample_number)
            .order_by(Variable.ord)
            .all()
        )

        # Convert measurements to list of dictionaries
        # Handle NULL values similar to MATLAB's iif(m.min is null, '', cast(m.min as char))
        measurements_data = [
            {
                'test': m.test,
                'element': m.element,
                'test_results': float(m.test_results) if m.test_results is not None else None,
                'min': str(m.min_value) if m.min_value is not None else '',
                'max': str(m.max_value) if m.max_value is not None else '',
                'unit': m.unit,
                'less': m.less,
                'typevar': m.typevar,
                'test_date': m.test_date[:10] if m.test_date else None
            }
            for m in measurements_query
        ]

        return {
            'sample': sample_data,
            'measurements': measurements_data
        }

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
                    measurement.get('unit', ''),
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

    async def _create_day_certificate_header(self) -> List:
        """Create company header section for day certificate."""
        content = []

        # Add spacing
        content.append(Spacer(1, 0.3*inch))

        # Company information centered
        company_style = ParagraphStyle(
            'CompanyHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            alignment=1,  # Center
            spaceAfter=4
        )

        content.append(Paragraph("INC CHEMICALS BELGIUM", company_style))
        content.append(Paragraph("ADDRESS 80", company_style))
        content.append(Paragraph("9000 GHENT, BELGIUM", company_style))
        content.append(Spacer(1, 0.2*inch))

        return content

    async def _create_day_certificate_sample_info(self, sample_data: Dict[str, Any]) -> List:
        """Create sample information section for day certificate."""
        content = []

        sample = sample_data.get('sample', {})
        measurements = sample_data.get('measurements', [])

        # Get test date from first measurement if available
        test_date = measurements[0].get('test_date', '') if measurements else ''

        # Format the grade information
        grade_text = f"{sample.get('grade', 'N/A')} - {sample.get('technical_grade', 'N/A')}"

        # Create sample information with specific layout
        info_style = ParagraphStyle(
            'SampleInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=0.5*inch,
            spaceAfter=8
        )

        label_style = ParagraphStyle(
            'LabelBold',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            leftIndent=0.5*inch,
            spaceAfter=8
        )

        # Grade
        content.append(Paragraph(f"<b>Grade :</b> {grade_text}", info_style))

        # Customer
        content.append(Paragraph(f"<b>Customer :</b> {sample.get('customer', 'N/A')}", info_style))

        # PVS Chemicals Ref and Customer Ref (side by side)
        pvs_ref = sample.get('order_number_pvs', 'N/A')
        customer_ref = sample.get('order_number_client', 'N/A')
        content.append(Paragraph(
            f"<b>PVS Chemicals Ref :</b> {pvs_ref}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<b>Customer Ref :</b> {customer_ref}",
            info_style
        ))

        # Sampling Date and Test Date (side by side)
        content.append(Paragraph(
            f"<b>Sampling Date :</b> {sample.get('sample_date', 'N/A')}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<b>Test Date :</b> {test_date}",
            info_style
        ))

        # Batch number and Container number (side by side)
        content.append(Paragraph(
            f"<b>Batch number :</b> {sample.get('batch_number', 'N/A')}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<b>Container number :</b> {sample.get('container_number', 'N/A')}",
            info_style
        ))

        return content

    async def _create_day_certificate_measurements_table(self, sample_data: Dict[str, Any]) -> List:
        """Create measurements table for day certificate with Test/Results/Specification/Unit columns."""
        content = []

        measurements = sample_data.get('measurements', [])

        if measurements:
            # Table header
            data = [['Test', '', '', 'Test Results', 'Specification', 'Unit']]

            for m in measurements:
                # Format test results
                test_result = ''
                if m.get('test_results') is not None:
                    test_result = str(m.get('test_results'))
                    # Handle 'less' flag
                    if m.get('less'):
                        test_result = f"< {test_result}"

                # Format specification (combine min and max)
                spec = ''
                min_val = m.get('min', '')
                max_val = m.get('max', '')

                if min_val and max_val:
                    spec = f"{min_val} - {max_val}"
                elif min_val:
                    spec = f">= {min_val}"
                elif max_val:
                    spec = f"<= {max_val}"

                # Get test name (prefer 'test' over 'element')
                test_name = m.get('test', '') or m.get('element', '')

                data.append([
                    test_name,
                    '',
                    '',
                    test_result,
                    spec,
                    m.get('unit', '')
                ])

            # Create table with appropriate column widths
            table = Table(data, colWidths=[2*inch, 0.5*inch, 0.5*inch, 1.5*inch, 1.5*inch, 1*inch])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # Test Results centered
                ('ALIGN', (4, 0), (4, -1), 'CENTER'),  # Specification centered
                ('ALIGN', (5, 0), (5, -1), 'CENTER'),  # Unit centered
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            content.append(table)

        return content

    async def _create_day_certificate_footer(self, username: str) -> List:
        """Create footer with quality control note and signatures."""
        content = []

        content.append(Spacer(1, 0.5*inch))

        # Quality control note
        note_style = ParagraphStyle(
            'QCNote',
            parent=self.styles['Normal'],
            fontSize=9,
            leftIndent=0.5*inch,
            spaceAfter=20
        )
        content.append(Paragraph("Quality controle is based on a tank sample.", note_style))

        content.append(Spacer(1, 0.3*inch))

        # Signature section
        signature_data = [
            ['Completed by,', '', '', '', '', 'Approved by,'],
            ['', '', '', '', '', ''],
            ['', '', '', '', '', ''],
            [username, '', '', '', '', 'Laboratory Manager']
        ]

        signature_table = Table(signature_data, colWidths=[1.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 1.5*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (5, 0), (5, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))

        content.append(signature_table)

        return content
        