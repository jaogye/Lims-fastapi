"""
Sample service module.

This module provides business logic for managing laboratory samples and their
measurements. It handles sample creation, retrieval, measurement management,
and specification-based measurement generation for different sample types.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import logging

from ..models.sample import Sample, Measurement
from ..models.laboratory import Product, Quality, SamplePoint, Variable
from ..models.specification import SampleMatrix, Spec
from ..models.user import User

logger = logging.getLogger(__name__)


class SampleService:
    """
    Service class for sample management operations.

    Provides methods for creating, retrieving, and managing laboratory samples
    and their associated measurements. Handles automatic measurement generation
    based on sample type and specifications.

    Attributes:
        db (Session): SQLAlchemy database session.
    """

    def __init__(self, db: Session):
        """
        Initialize the sample service.

        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db

    async def get_samples(
        self,
        sample_date: Optional[str] = None,
        type_sample: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve samples with optional filtering.

        Fetches samples from the database with optional filters for date and sample type.
        Eagerly loads related entities (product, quality, sample_point) for efficiency.

        Args:
            sample_date (Optional[str]): Filter by sample date (YYYY-MM-DD format).
            type_sample (Optional[str]): Filter by sample type (PRO, CLI, MAN).

        Returns:
            List[Dict[str, Any]]: List of sample dictionaries with related data.
        """
        query = (
            self.db.query(Sample)
            .options(
                joinedload(Sample.product),
                joinedload(Sample.quality),
                joinedload(Sample.sample_point)
            )
        )

        if sample_date:
            query = query.filter(Sample.date == sample_date)
        
        if type_sample:
            query = query.filter(Sample.type_sample == type_sample)

        samples = query.all()
        
        result = []
        for sample in samples:
            sample_dict = {
                "id": sample.id,
                "sample_number": sample.sample_number.strip(),
                "product": sample.product.name.strip() if sample.product else "",
                "quality": sample.quality.name.strip() if sample.quality else "",
                "sample_point": sample.sample_point.name if sample.sample_point else "",
                "sample_date": sample.date.strip(),
                "sample_time": sample.time.strip(),
                "remark": sample.remark.strip() if sample.remark else "",
                "coa": sample.coa if sample.coa else "",
                "day_coa": sample.day_coa if sample.day_coa else "",
                "coc": sample.coc if sample.coc else "",
                "type_sample": sample.type_sample
            }
            result.append(sample_dict)
        
        return result

    async def get_sample_by_id(self, sample_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single sample by ID.

        Args:
            sample_id (int): The ID of the sample to retrieve.

        Returns:
            Optional[Dict[str, Any]]: Sample dictionary with related data, or None if not found.
        """
        sample = (
            self.db.query(Sample)
            .options(
                joinedload(Sample.product),
                joinedload(Sample.quality),
                joinedload(Sample.sample_point)
            )
            .filter(Sample.id == sample_id)
            .first()
        )

        if not sample:
            return None

        return {
            "id": sample.id,
            "sample_number": sample.sample_number,
            "product": sample.product.name if sample.product else "",
            "quality": sample.quality.name if sample.quality else "",
            "sample_point": sample.sample_point.name if sample.sample_point else "",
            "sample_date": sample.date,
            "sample_time": sample.time,
            "remark": sample.remark,
            "coa": sample.coa,
            "day_coa": sample.day_coa,
            "coc": sample.coc,
            "type_sample": sample.type_sample
        }

    async def create_sample(self, sample_data: Dict[str, Any], created_by_id: int) -> Sample:
        """
        Create a new sample.

        Generates a unique sample number, creates the sample record, and automatically
        generates required measurements based on the sample type and specifications.

        Args:
            sample_data (Dict[str, Any]): Sample data including type_sample, product_id,
                quality_id, and optional fields.
            created_by_id (int): ID of the user creating the sample.

        Returns:
            Sample: The newly created sample object.
        """
        # Generate sample number
        sample_number = await self._generate_sample_number(sample_data["type_sample"])
        
        # Get current date and time
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        
        sample = Sample(
            type_sample=sample_data["type_sample"],
            product_id=sample_data["product_id"],
            quality_id=sample_data["quality_id"],
            sample_point_id=sample_data.get("sample_point_id"),
            created_by_id=created_by_id,
            creation_date=current_date + " " + current_time,
            date=current_date,
            time=current_time,
            sample_number=sample_number,
            description=sample_data.get("description"),
            remark=sample_data.get("remark"),
            customer=sample_data.get("customer"),
            order_number_client=sample_data.get("order_number_client")
        )

        self.db.add(sample)
        self.db.commit()
        self.db.refresh(sample)

        # Generate measurements based on sample type
        await self._generate_sample_measurements(sample)

        return sample

    async def get_sample_measurements(self, sample_id: int) -> List[Dict[str, Any]]:
        """
        Get all measurements for a specific sample.

        Args:
            sample_id (int): The ID of the sample.

        Returns:
            List[Dict[str, Any]]: List of measurement dictionaries with variable,
                value, limits, test date, and tested_by information.
        """
        measurements = (
            self.db.query(Measurement)
            .options(
                joinedload(Measurement.tested_by),
                joinedload(Measurement.variable)
            )
            .filter(Measurement.sample_id == sample_id)
            .all()
        )

        result = []
        for measurement in measurements:
            measurement_dict = {
                "id": measurement.id,
                "variable": measurement.variable,
                "value": float(measurement.value) if measurement.value else None,
                "min_value": float(measurement.min_value) if measurement.min_value else None,
                "max_value": float(measurement.max_value) if measurement.max_value else None,
                "test_date": measurement.test_date,
                "tested_by": measurement.tested_by.name if measurement.tested_by else None
            }
            result.append(measurement_dict)

        return result

    async def add_measurement(
        self,
        sample_id: int,
        variable: str,
        value: float,
        tested_by_id: int
    ) -> Measurement:
        """
        Add or update a measurement for a sample.

        If a measurement for the specified variable already exists, it updates the value.
        Otherwise, creates a new measurement record.

        Args:
            sample_id (int): The ID of the sample.
            variable (str): The variable name being measured.
            value (float): The measured value.
            tested_by_id (int): ID of the user performing the test.

        Returns:
            Measurement: The created or updated measurement object.
        """
        # Check if measurement already exists
        existing = (
            self.db.query(Measurement)
            .filter(
                and_(
                    Measurement.sample_id == sample_id,
                    Measurement.variable == variable
                )
            )
            .first()
        )

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if existing:
            # Update existing measurement
            existing.value = value
            existing.tested_by_id = tested_by_id
            existing.test_date = current_datetime
            measurement = existing
        else:
            # Create new measurement
            measurement = Measurement(
                sample_id=sample_id,
                variable=variable,
                value=value,
                tested_by_id=tested_by_id,
                test_date=current_datetime
            )
            self.db.add(measurement)

        self.db.commit()
        self.db.refresh(measurement)
        
        return measurement

    async def refresh_sample_specifications(self, sample_number: str):
        """
        Refresh sample measurements based on current specifications.

        Regenerates measurements for a sample if specifications have changed.

        Args:
            sample_number (str): The sample number to refresh.

        Raises:
            ValueError: If the sample is not found.
        """
        sample = self.db.query(Sample).filter(Sample.sample_number == sample_number).first()

        if not sample:
            raise ValueError(f"Sample {sample_number} not found")

        # Refresh measurements based on current specifications
        measurement = await self._generate_sample_measurements(sample)
        return measurement
    
    async def get_samples_with_measurements(self, sample_date: str) -> List[Dict[str, Any]]:
        """
        Get samples for a specific date with measurements (CLI and MAN types only).

        Args:
            sample_date (str): Sample date in YYYY-MM-DD format.

        Returns:
            List[Dict[str, Any]]: List of samples with nested measurements.
        """
        # Query samples for the date with type_sample = 'CLI' or 'MAN'
        samples = (
            self.db.query(Sample)
            .options(
                joinedload(Sample.product),
                joinedload(Sample.quality),
                joinedload(Sample.sample_point),
                joinedload(Sample.measurements).joinedload(Measurement.variable)
            )
            .filter(
                and_(
                    Sample.date == sample_date,
                    or_(Sample.type_sample == 'CLI', Sample.type_sample == 'MAN')
                )
            )
            .all()
        )

        result = []
        for sample in samples:
            # Build quality_info list from measurements
            quality_info = []
            for measurement in sample.measurements:
                quality_info.append({
                    "variable": measurement.variable.name.strip() if measurement.variable else "",
                    "min": float(measurement.min_value) if measurement.min_value is not None else None,
                    "max": float(measurement.max_value) if measurement.max_value is not None else None,
                    "value": float(measurement.value) if measurement.value is not None else None
                })

            sample_dict = {
                "sample_number": sample.sample_number.strip() if sample.sample_number else "",
                "customer_name": sample.customer.strip() if sample.customer else None,
                "product": sample.product.name.strip() if sample.product else "",
                "quality": sample.quality.name.strip() if sample.quality else "",
                "tank": sample.sample_point.name.strip() if sample.sample_point else None,
                "sample_date": sample.date.strip() if sample.date else "",
                "orderPVS": str(sample.order_number_pvs) if sample.order_number_pvs is not None else None,
                "orderclient": sample.order_number_client.strip() if sample.order_number_client else None,
                "batch_number": sample.batch_number.strip() if sample.batch_number else None,
                "container_number": sample.container_number.strip() if sample.container_number else None,
                "remark": sample.remark.strip() if sample.remark else None,
                "sample_product_id": sample.product_id,
                "sample_quality_id": sample.quality_id,
                "sample_samplepoint_id": sample.sample_point_id,
                "sample_certificate": sample.certificate.strip() if sample.certificate else None,
                "sample_coa": sample.coa.strip() if sample.coa else None,
                "sample_coc": sample.coc.strip() if sample.coc else None,
                "sample_day_coa": sample.day_coa.strip() if sample.day_coa else None,
                "quality_info": quality_info
            }
            result.append(sample_dict)

        return result

    async def update_samples_batch(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update samples and their measurements with validation.

        Validates that all measurement values are within allowed ranges before updating.
        Updates sample fields and measurement values.

        Args:
            samples (List[Dict[str, Any]]): List of samples to update.

        Returns:
            Dict[str, Any]: Result with success status and updated count.

        Raises:
            HTTPException: If any measurement value is out of range.
        """
        from fastapi import HTTPException

        validation_errors = []

        # Get maximum field lengths from Sample model column definitions
        samplepoint_name_max_length = Sample.__table__.columns['samplepoint_name'].type.length
        container_number_max_length = Sample.__table__.columns['container_number'].type.length
        batch_number_max_length = Sample.__table__.columns['batch_number'].type.length
        remark_max_length = Sample.__table__.columns['remark'].type.length

        # First pass: validate all measurements
        for sample_data in samples:
            sample_number = sample_data.get("sample_number")

            # Check if sample exists
            sample = self.db.query(Sample).filter(Sample.sample_number == sample_number).first()
            if not sample:
                validation_errors.append(f"Sample {sample_number} not found")
                continue

            # Validate tank field if provided
            tank_name = sample_data.get("tank")
            if tank_name is not None and tank_name:  # Only validate if tank is provided and not empty
                sample_point = self.db.query(SamplePoint).filter(SamplePoint.name == tank_name).first()
                if not sample_point:
                    validation_errors.append(
                        f"Sample {sample_number}: tank '{tank_name}' not found in samplepoint table"
                    )

            # Validate field lengths to prevent database truncation errors
            if sample_data.get("tank") and len(sample_data["tank"]) > samplepoint_name_max_length:
                validation_errors.append(
                    f"Sample {sample_number}: tank name exceeds maximum length of {samplepoint_name_max_length} characters (current: {len(sample_data['tank'])})"
                )

            if sample_data.get("container_number") and len(sample_data["container_number"]) > container_number_max_length:
                validation_errors.append(
                    f"Sample {sample_number}: container_number exceeds maximum length of {container_number_max_length} characters (current: {len(sample_data['container_number'])})"
                )

            if sample_data.get("batch_number") and len(sample_data["batch_number"]) > batch_number_max_length:
                validation_errors.append(
                    f"Sample {sample_number}: batch_number exceeds maximum length of {batch_number_max_length} characters (current: {len(sample_data['batch_number'])})"
                )

            if sample_data.get("remark") and len(sample_data["remark"]) > remark_max_length:
                validation_errors.append(
                    f"Sample {sample_number}: remark exceeds maximum length of {remark_max_length} characters (current: {len(sample_data['remark'])})"
                )

            # Validate each measurement value
            for quality_item in sample_data.get("quality_info", []):
                variable_name = quality_item.get("variable")
                value = quality_item.get("value")
                min_val = quality_item.get("min")
                max_val = quality_item.get("max")

                # Only validate if value is provided and not None
                if value is not None:
                    # Check min constraint
                    if min_val is not None and value < min_val:
                        validation_errors.append(
                            f"Sample {sample_number}, variable '{variable_name}': "
                            f"value {value} is below minimum {min_val}"
                        )

                    # Check max constraint
                    if max_val is not None and value > max_val:
                        validation_errors.append(
                            f"Sample {sample_number}, variable '{variable_name}': "
                            f"value {value} exceeds maximum {max_val}"
                        )

        # If there are validation errors, raise exception
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Validation failed: measurements out of range",
                    "errors": validation_errors
                }
            )

        # Second pass: perform updates if all validations passed
        updated_count = 0
        for sample_data in samples:
            sample_number = sample_data.get("sample_number")

            # Get the sample
            sample = self.db.query(Sample).filter(Sample.sample_number == sample_number).first()
            if not sample:
                continue

            # Update only the allowed fields: tank, container_number, batch_number, remark

            # Resolve sample_point_id from tank name and store tank name
            if sample_data.get("tank") is not None:
                if sample_data.get("tank"):
                    tank_name = sample_data["tank"]
                    sample_point = self.db.query(SamplePoint).filter(SamplePoint.name == tank_name).first()
                    if sample_point:
                        sample.sample_point_id = sample_point.id
                        sample.samplepoint_name = tank_name  # Store the tank name
                else:
                    sample.sample_point_id = None
                    sample.samplepoint_name = None

            if sample_data.get("batch_number") is not None:
                sample.batch_number = sample_data["batch_number"]

            if sample_data.get("container_number") is not None:
                sample.container_number = sample_data["container_number"]

            if sample_data.get("remark") is not None:
                sample.remark = sample_data["remark"]

            # Update measurements
            for quality_item in sample_data.get("quality_info", []):
                variable_name = quality_item.get("variable")
                value = quality_item.get("value")

                # Get variable_id from variable name
                variable = self.db.query(Variable).filter(Variable.name == variable_name).first()
                if not variable:
                    logger.warning(f"Variable '{variable_name}' not found")
                    continue

                # Find existing measurement
                measurement = (
                    self.db.query(Measurement)
                    .filter(
                        and_(
                            Measurement.sample_id == sample.id,
                            Measurement.variable_id == variable.id
                        )
                    )
                    .first()
                )

                if measurement:
                    # Update existing measurement
                    measurement.value = value
                    measurement.test_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # Create new measurement if it doesn't exist
                    new_measurement = Measurement(
                        sample_id=sample.id,
                        variable_id=variable.id,
                        variable=variable_name,
                        value=value,
                        min_value=quality_item.get("min"),
                        max_value=quality_item.get("max"),
                        test_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    self.db.add(new_measurement)

            updated_count += 1

        # Commit all changes
        self.db.commit()

        return {
            "message": f"Successfully updated {updated_count} samples",
            "updated_count": updated_count
        }

    async def get_sample_completion_status(self, sample_number: str) -> Dict[str, Any]:
        """
        Calculate sample testing completion status.

        Args:
            sample_number (str): The number of the sample.

        Returns:
            Dict[str, Any]: Dictionary containing total_measurements, completed_measurements,
                completion_percentage, and is_complete flag.
        """
        sample = (
            self.db.query(Sample)
            .filter(Sample.sample_number == sample_number)
            .first()
        )

        if not sample:
            raise ValueError(f"Sample {sample_number} not found")

        measurements = (
            self.db.query(Measurement)
            .filter(Measurement.sample_id == sample.id)
            .all()
        )

        total_measurements = len(measurements)
        completed_measurements = len([m for m in measurements if m.value is not None])
        
        completion_percentage = (
            (completed_measurements / total_measurements * 100) 
            if total_measurements > 0 
            else 0
        )

        return {
            "sample_number": sample_number,
            "total_measurements": total_measurements,
            "completed_measurements": completed_measurements,
            "completion_percentage": round(completion_percentage, 2),
            "is_complete": completion_percentage == 100
        }

    async def _generate_sample_number(self, type_sample: str) -> str:
        """
        Generate unique sample number.
    
        Creates a unique sample number in the format: {TYPE}{YYYYMMDD}{SEQUENCE}
        where SEQUENCE is a 3-digit counter for samples of this type on this date.
    
        Args:
            type_sample (str): Sample type (PRO, CLI, MAN).
    
        Returns:
            str: Generated unique sample number.
        """
        # Generate unique sample number based on type and date
        today = datetime.now()
        date_str = today.strftime("%Y%m%d")
    
        # Count samples of this type today
        count = (
            self.db.query(Sample)
            .filter(
                and_(
                    Sample.type_sample == type_sample,
                    Sample.date == today.strftime("%Y-%m-%d")
                )
            )
            .count()
        )
    
        sequence = f"{count + 1:03d}"
        return f"{type_sample}{date_str}{sequence}"
    
     
    async def _generate_sample_measurements(self, sample: Sample):
        """
        Generate measurements for a sample based on its type.
        
        Routes to appropriate measurement generation method based on sample type:
        - PRO: Uses sample matrix configuration
        - CLI: Uses customer-specific specification
        - MAN: Uses general specification
        
        Args:
            sample (Sample): The sample object to generate measurements for.
        """
        if sample.type_sample == "PRO":
            # Production sample - use SampleMatrix
            measurement = await self._generate_production_measurements(sample)
        elif sample.type_sample == "CLI":
            # Customer sample - use customer specification
            measurement = await self._generate_customer_measurements(sample)
        elif sample.type_sample == "MAN":
            # Manual sample - use general specification
            measurement = await self._generate_manual_measurements(sample)
        
        return measurement 

    async def _generate_production_measurements(self, sample: Sample):
        """
        Generate measurements for production samples.

        Uses sample matrix to determine which tests to perform based on
        product/quality/sample point combination.

        Args:
            sample (Sample): The production sample object.
        """
        # Find sample matrix for this product/quality/sample_point combination
        sample_matrix = (
            self.db.query(SampleMatrix)
            .filter(
                and_(
                    SampleMatrix.product_id == sample.product_id,
                    SampleMatrix.quality_id == sample.quality_id,
                    SampleMatrix.sample_point_id == sample.sample_point_id
                )
            )
            .first()
        )
        
        if not sample_matrix:
            logger.warning(f"No sample matrix found for sample {sample.id}")
            return
        
        # Create measurements based on sample matrix flags
        measurement = await self._create_measurements_from_matrix(sample, sample_matrix)
        return measurement

    async def _generate_customer_measurements(self, sample: Sample):
        """
        Generate measurements for customer samples.
        
        Uses customer-specific specification to determine required tests.
        
        Args:
            sample (Sample): The customer sample object.
        """
        # Find customer specification
        spec = (
            self.db.query(Spec)
            .filter(
                and_(
                    Spec.type_spec == "CLI",
                    Spec.product_id == sample.product_id,
                    Spec.quality_id == sample.quality_id,
                    Spec.customer == sample.customer.strip()
                )
            )
            .first()
        )
        measurement = None
        if spec:
            measurement = await self._create_measurements_from_spec(sample, spec)
        
        return measurement     

    async def _generate_manual_measurements(self, sample: Sample):
        """
        Generate measurements for manual samples.
        
        Uses general specification to determine required tests.
        
        Args:
            sample (Sample): The manual sample object.
        """
        # Find general specification
        spec = (
            self.db.query(Spec)
            .filter(
                and_(
                    Spec.type_spec == "GEN",
                    Spec.product_id == sample.product_id,
                    Spec.quality_id == sample.quality_id
                )
            )
            .first()
        )
        
        if spec:
            measurement = await self._create_measurements_from_spec(sample, spec)
        
        return measurement    


    async def _create_measurements_from_matrix(self, sample: Sample, matrix: SampleMatrix):
        """
        Create measurement records based on sample matrix configuration.
    
        Placeholder method for creating measurements based on boolean flags
        in the sample matrix that indicate which tests should be performed.

        Args:
            sample (Sample): The sample object.
            matrix (SampleMatrix): The sample matrix configuration.
        """
        # This would create measurements based on the boolean flags in SampleMatrix
        # Implementation would check each has_* field and create corresponding measurements
        pass

    async def _create_measurements_from_spec(self, sample: Sample, spec: Spec):
        """
        Create measurement records based on specification limits.

        Retrieves and processes measurements for a sample, adding string representations
        and handling special cases like less-than values and missing limits.

        Args:
            sample (Sample): The sample object.
            spec (Spec): The specification object with defined limits.

        Returns:
            List[Dict[str, Any]]: List of processed measurement dictionaries with formatted values.
        """
        # Query measurements joined with sample and variable, ordered by variable.ord
        measurements = (
            self.db.query(Measurement)
            .join(Variable, Measurement.variable_id == Variable.id)
            .join(Sample, Measurement.sample_id == Sample.id)
            .filter(Sample.sample_number == sample.sample_number)
            .order_by(Variable.ord)
            .all()
        )

        # Process measurements to create formatted result
        result = []
        for measurement in measurements:
            # Get variable information
            variable = (
                self.db.query(Variable)
                .filter(Variable.id == measurement.variable_id)
                .first()
            )

            # Initialize str_value
            str_value = ""

            # Convert value to string representation
            if measurement.value is not None and measurement.value != -1:
                # If less flag is set, prepend "<"
                if measurement.less:
                    str_value = f"<{float(measurement.value)}"
                else:
                    str_value = str(float(measurement.value))
            # If value is -1 or None, str_value remains empty

            # Handle missing min/max values
            min_value = float(measurement.min_value) if measurement.min_value is not None else float('-inf')
            max_value = float(measurement.max_value) if measurement.max_value is not None else float('inf')

            # Create measurement dictionary
            measurement_dict = {
                "sample_number": sample.sample_number.strip(),
                "id": measurement.id,
                "sample_id": measurement.sample_id,
                "variable_id": measurement.variable_id,
                "variable": measurement.variable,
                "value": float(measurement.value) if measurement.value is not None else None,
                "min_value": min_value,
                "max_value": max_value,
                "str_value": str_value,
                "less": measurement.less if measurement.less is not None else False,
                "test_date": measurement.test_date,
                "tested_by_id": measurement.tested_by_id,
                "typevar": variable.typevar if variable else None,
                "modified": 0  # Default value as in MATLAB code
            }

            result.append(measurement_dict)

        return result