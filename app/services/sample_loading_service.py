"""
Sample loading service module.

This module provides automated sample loading functionality for both customer
and production samples. It integrates with logistic data to automatically generate
sample records with appropriate measurements based on specifications and sample matrices.
Migrated from MATLAB functions: loadCustomerSample.m and loadProductionSample.m

Key features:
- Automated customer sample loading from logistic data
- Production sample scheduling based on frequency (daily, weekly, monthly, etc.)
- Holiday-aware first-day-of-period calculations
- Automatic measurement generation based on specifications
- Article code mapping for customer orders
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SampleLoadingService:
    """
    Service for loading customer and production samples.

    Automates sample creation from logistic data for customer orders and
    scheduled production sampling based on frequency and sample matrices.

    Attributes:
        db (Session): SQLAlchemy database session.
    """

    def __init__(self, db: Session):
        """
        Initialize the sample loading service.

        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db

    def _get_spec_id(self, product_id: int, quality_id: int, customer: str = '') -> Tuple[Optional[int], Optional[str]]:
        """
        Get specification ID for given product, quality, and customer.
        First checks for customer-specific spec (CLI), then falls back to general spec (GEN).
        Returns (spec_id, certificate)
        """
        # Try to find customer-specific specification
        if customer:
            sql = text("""
                SELECT id, certificate FROM spec
                WHERE type_spec='CLI' AND product_id=:product_id
                AND quality_id=:quality_id AND customer=:customer
            """)
            result = self.db.execute(sql, {
                'product_id': product_id,
                'quality_id': quality_id,
                'customer': customer
            }).first()

            if result:
                return result[0], result[1].strip() if result[1] else None

        # Fall back to general specification
        sql = text("""
            SELECT id, certificate FROM spec
            WHERE type_spec='GEN' AND product_id=:product_id
            AND quality_id=:quality_id
        """)
        result = self.db.execute(sql, {
            'product_id': product_id,
            'quality_id': quality_id
        }).first()

        if result:
            return result[0], result[1].strip() if result[1] else None

        return None, None

    def _get_sample_number(self, sample_date: str, type_sample: str) -> str:
        """
        Generate next sample number for given date and type.
        Format: {Type_prefix}{DDMMYYYY}_{XXX}
        Example: C01012025_001 for CLI sample on 2025-01-01
        """
        sql = text("""
            SELECT COUNT(*) as cnt FROM sample
            WHERE type_sample=:type_sample
            AND SUBSTRING(date,1,10)=:sample_date
        """)
        result = self.db.execute(sql, {
            'type_sample': type_sample,
            'sample_date': sample_date
        }).first()

        if result and result[0] > 0:
            sql2 = text("""
                SELECT MAX(SUBSTRING(sample_number,11,3)) as lastsample
                FROM sample
                WHERE type_sample=:type_sample
                AND SUBSTRING(date,1,10)=:sample_date
            """)
            result2 = self.db.execute(sql2, {
                'type_sample': type_sample,
                'sample_date': sample_date
            }).first()

            try:
                next_num = int(result2[0]) + 1 if result2 and result2[0] else 1
            except:
                next_num = 1
        else:
            next_num = 1

        # Format: prefix + date + sequence
        prefix = type_sample[0]  # First character of type
        date_obj = datetime.strptime(sample_date, '%Y-%m-%d')
        date_str = date_obj.strftime('%d%m%Y')

        return f"{prefix}{date_str}_{next_num:03d}"

    def _insert_measurements(self, sample_id: int, limits: List[Dict]):
        """Insert measurements for a sample with limits from specification"""
        for limit in limits:
            variable_name = limit['variable']
            variable_id = limit['variable_id']
            min_val = limit.get('min')
            max_val = limit.get('max')

            # Convert None or negative values to NULL
            if min_val is None or (isinstance(min_val, (int, float)) and min_val < 0):
                min_val = None
            if max_val is None or (isinstance(max_val, (int, float)) and max_val < 0):
                max_val = None

            sql = text("""
                INSERT INTO measurement(sample_id, variable_id, variable_name, min_value, max_value, value)
                VALUES (:sample_id, :variable_id, :variable_name, :min_val, :max_val, NULL)
            """)

            self.db.execute(sql, {
                'sample_id': sample_id,
                'variable_id': variable_id,
                'variable_name': variable_name,
                'min_val': min_val,
                'max_val': max_val
            })

    def _update_measurements(self, sample_id: int, limits: List[Dict]):
        """Update or insert measurements for existing sample"""
        for limit in limits:
            variable_id = limit['variable_id']
            variable = limit['variable']
            min_val = limit.get('min')
            max_val = limit.get('max')

            # Check if measurement exists
            sql_check = text("""
                SELECT sample_id FROM measurement
                WHERE sample_id=:sample_id AND variable_id=:variable_id
            """)
            existing = self.db.execute(sql_check, {
                'sample_id': sample_id,
                'variable_id': variable_id
            }).first()

            if not existing:
                # Insert new measurement
                sql = text("""
                    INSERT INTO measurement(sample_id, variable_id, variable, min_value, max_value, value)
                    VALUES (:sample_id, :variable_id, :variable, :min_val, :max_val, NULL)
                """)
                self.db.execute(sql, {
                    'sample_id': sample_id,
                    'variable_id': variable_id,
                    'variable': variable,
                    'min_val': min_val if min_val and min_val >= 0 else None,
                    'max_val': max_val if max_val and max_val >= 0 else None
                })
            else:
                # Update existing measurement limits
                if min_val is not None and max_val is not None:
                    sql = text("""
                        UPDATE measurement SET min_value=:min_val, max_value=:max_val
                        WHERE sample_id=:sample_id AND variable_id=:variable_id
                    """)
                    self.db.execute(sql, {
                        'min_val': min_val,
                        'max_val': max_val,
                        'sample_id': sample_id,
                        'variable_id': variable_id
                    })
                elif min_val is not None:
                    sql = text("""
                        UPDATE measurement SET min_value=:min_val
                        WHERE sample_id=:sample_id AND variable_id=:variable_id
                    """)
                    self.db.execute(sql, {
                        'min_val': min_val,
                        'sample_id': sample_id,
                        'variable_id': variable_id
                    })
                elif max_val is not None:
                    sql = text("""
                        UPDATE measurement SET max_value=:max_val
                        WHERE sample_id=:sample_id AND variable_id=:variable_id
                    """)
                    self.db.execute(sql, {
                        'max_val': max_val,
                        'sample_id': sample_id,
                        'variable_id': variable_id
                    })

    async def load_customer_samples(self, sample_date: str, user_id: int) -> Dict[str, Any]:
        """
        Load customer samples from logistic data for given date.
        Migrated from loadCustomerSample.m
        """
        errors = []
        pending_data = []

        try:
            # First, clean up samples that don't have corresponding logistic data
            sql_cleanup = text("""
                DELETE FROM sample
                WHERE type_sample='CLI' AND NOT EXISTS(
                    SELECT * FROM logisticdata l
                    WHERE sample.date=SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10)
                    AND sample.order_number_pvs=l.order_number_pvs
                )
            """)
            self.db.execute(sql_cleanup)
            self.db.commit()

            # Get logistic data and check for existing samples
            sql_main = text("""
                SELECT 'U' as typerow, s.id,
                    l.date as loadingdate, l.time, l.name_client, l.order_number_pvs,
                    l.article_no, l.order_number_client, l.Description, l.loading_ton, s.test_date,
                    p.name as product, q.name as quality, s.customer, s.product_id, s.quality_id, s.article_code,
                    s.created_by_id, SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10) as date2, sp.coa, sp.certificate,
                    sp.coc, sp.day_coa, sp.opm, sp.onedecimal
                FROM sample s, product p, quality q, logisticdata l, spec sp
                WHERE s.spec_id=sp.id AND s.date=:sample_date AND s.product_id=p.id AND
                s.quality_id=q.id AND s.type_sample='CLI' AND s.order_number_pvs = l.order_number_pvs
                AND s.date=SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10)

                UNION

                SELECT 'E1' as typerow, 0 as id, l.date as loadingdate, l.time, l.name_client, l.order_number_pvs,
                l.article_no, l.order_number_client, l.Description, l.loading_ton, '' as test_date,
                ' ' as product, ' ' as quality, ' ' as customer,
                0 as product_id, 0 as quality_id, 0 as article_code, 0 as created_by_id, ' ' as date2,
                ' ' as coa, ' ' as certificate, ' ' as coc, ' ' as day_coa, ' ' as opm, ' ' as onedecimal
                FROM logisticdata l
                WHERE SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10) =:sample_date
                AND NOT EXISTS(SELECT * FROM map m WHERE l.article_no = m.article_code)

                UNION

                SELECT 'E2' as typerow, 0 as id, l.date as loadingdate, l.time, l.name_client, l.order_number_pvs,
                l.article_no, l.order_number_client, l.Description, l.loading_ton, '' as test_date,
                p.name as product, q.name as quality, ' ' as customer,
                m.product_id, m.quality_id, m.article_code, 0 as created_by_id, ' ' as date2,
                ' ' as coa, ' ' as certificate, ' ' as coc, ' ' as day_coa, ' ' as opm, ' ' as onedecimal
                FROM logisticdata l, map m, product p, quality q
                WHERE SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10) =:sample_date
                AND m.product_id=p.id AND m.quality_id=q.id
                AND l.article_no = m.article_code AND NOT EXISTS(
                    SELECT * FROM spec s
                    WHERE s.product_id=m.product_id AND s.quality_id=m.quality_id AND s.customer=l.name_client
                )

                UNION

                SELECT 'N' as typerow, 0 as id, l.date as loadingdate, l.time, l.name_client, l.order_number_pvs,
                l.article_no, l.order_number_client, l.Description, l.loading_ton, '' as test_date, p.name as product,
                q.name as quality, s.customer,  m.product_id, m.quality_id, m.article_code,
                :user_id as created_by_id, SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10) as date2,
                s.coa, s.certificate, s.coc, s.day_coa, s.opm, s.onedecimal
                FROM logisticdata l, map m, product p, quality q, spec s
                WHERE SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10) = :sample_date
                AND l.article_no = m.article_code
                AND s.product_id=m.product_id AND s.quality_id=m.quality_id AND s.customer=l.name_client
                AND m.product_id=p.id AND m.quality_id=q.id
                AND NOT EXISTS(
                    SELECT * FROM sample s
                    WHERE s.order_number_pvs = l.order_number_pvs
                    AND s.date=SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10)
                )
            """)

            data = self.db.execute(sql_main, {
                'sample_date': sample_date,
                'user_id': user_id
            }).fetchall()

            for row in data:
                row_dict = dict(row._mapping)
                typerow = row_dict['typerow']
                
                # Handle error cases
                if typerow == 'E1':
                    errors.append(f"Article code {row_dict['article_no']} not found in Map table")
                    pending_data.append(row_dict)
                    continue
                
                if typerow == 'E2':
                    errors.append(
                        f"No specification found for combination: "
                        f"Customer={row_dict['name_client']}, Product={row_dict['product']}, "
                        f"Quality={row_dict['quality']}, Article={row_dict['article_no']}"
                    )
                    pending_data.append(row_dict)
                    continue
                
                # Get spec_id and limits
                spec_id, _ = self._get_spec_id(
                    row_dict['product_id'],
                    row_dict['quality_id'],
                    row_dict.get('customer', '')
                )

                if not spec_id:
                    errors.append(
                        f"No specification found for Product={row_dict['product']}, "
                        f"Quality={row_dict['quality']}, Customer={row_dict.get('customer', '')}"
                    )
                    continue

                # Get variable limits from spec
                sql_limits = text("""
                    SELECT v.name as variable, d.variable_id, d.min_value as min, d.max_value as max
                    FROM dspec d, variable v
                    WHERE d.variable_id=v.id AND d.spec_id=:spec_id
                """)
                limits = [dict(r._mapping) for r in self.db.execute(sql_limits, {'spec_id': spec_id})]

                # Process based on typerow
                sample_number = self._get_sample_number(sample_date, 'CLI')

                if typerow == 'N':
                    # Insert new sample
                    current_time = datetime.now()

                    sql_insert = text("""
                        INSERT INTO sample(
                            type_sample, spec_id, product_id, quality_id, article_code, customer,
                            created_by_id, creation_date, date, time, order_number_pvs, article_no,
                            order_number_client, description, loading_ton, sample_number,
                            remark, batch_number, container_number,
                            certificate, coa, coc, day_coa, opm, onedecimal
                        )
                        OUTPUT INSERTED.id
                        VALUES (
                            'CLI', :spec_id, :product_id, :quality_id, :article_code, :customer,
                            :user_id, :creation_date, :date, :time, :order_number_pvs, :article_no,
                            :order_number_client, :description, :loading_ton, :sample_number,
                            '', '', '',
                            :certificate, :coa, :coc, :day_coa, :opm, :onedecimal
                        )
                    """)

                    result = self.db.execute(sql_insert, {
                        'spec_id': spec_id,
                        'product_id': row_dict['product_id'],
                        'quality_id': row_dict['quality_id'],
                        'article_code': row_dict['article_code'],
                        'customer': row_dict['customer'],
                        'user_id': user_id,
                        'creation_date': current_time,
                        'date': row_dict['date2'],
                        'time': row_dict['time'],
                        'order_number_pvs': row_dict['order_number_pvs'],
                        'article_no': row_dict['article_no'],
                        'order_number_client': row_dict['order_number_client'],
                        'description': row_dict['Description'],
                        'loading_ton': row_dict['loading_ton'],
                        'sample_number': sample_number,
                        'certificate': row_dict.get('certificate', ''),
                        'coa': row_dict.get('coa', ''),
                        'coc': row_dict.get('coc', ''),
                        'day_coa': row_dict.get('day_coa', ''),
                        'opm': row_dict.get('opm', ''),
                        'onedecimal': row_dict.get('onedecimal', '')
                    })

                    # Get inserted sample ID from OUTPUT clause
                    row = result.first()
                    if row:
                        sample_id = int(row[0]) if row[0] is not None else None
                    else:
                        sample_id = None

                    if sample_id is None:
                        raise ValueError("Failed to retrieve inserted sample ID")

                    # Insert measurements if COA or Day_COA is required
                    if row_dict.get('coa') == 'X' or row_dict.get('day_coa') == 'X':
                        self._insert_measurements(sample_id, limits)

                    self.db.commit()

                elif typerow == 'U':
                    # Update existing sample
                    sql_update = text("""
                        UPDATE sample SET
                            sample_number=:sample_number,
                            coa=:coa,
                            certificate=:certificate,
                            coc=:coc,
                            day_coa=:day_coa,
                            opm=:opm,
                            onedecimal=:onedecimal
                        WHERE date=:date AND order_number_pvs=:order_number_pvs
                    """)

                    self.db.execute(sql_update, {
                        'sample_number': sample_number,
                        'coa': row_dict.get('coa', ''),
                        'certificate': row_dict.get('certificate', ''),
                        'coc': row_dict.get('coc', ''),
                        'day_coa': row_dict.get('day_coa', ''),
                        'opm': row_dict.get('opm', ''),
                        'onedecimal': row_dict.get('onedecimal', ''),
                        'date': row_dict['date2'],
                        'order_number_pvs': row_dict['order_number_pvs']
                    })

                    # Update measurements
                    sample_id = row_dict['id']
                    self._update_measurements(sample_id, limits)

                    self.db.commit()

            return {
                'success': len(errors) == 0,
                'message': f"Processed {len(data)} records",
                'errors': errors if errors else None,
                'pending_data': pending_data if pending_data else None
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error loading customer samples: {e}")
            raise

    def _get_first_day_of_period(self, date_obj: datetime, frequency: str) -> str:
        """Get the first non-holiday day of the period based on frequency"""

        if frequency == '1/2 year':
            # First day of semester (Jan 1 or Jul 1)
            month = 1 if date_obj.month <= 6 else 7
            first_day = datetime(date_obj.year, month, 1)

        elif frequency == 'Month':
            # First day of month
            first_day = datetime(date_obj.year, date_obj.month, 1)

        elif frequency == 'Quarter':
            # First day of quarter
            quarter = (date_obj.month - 1) // 3 + 1
            month = (quarter - 1) * 3 + 1
            first_day = datetime(date_obj.year, month, 1)

        elif frequency == 'Week':
            # First day of week (Monday)
            days_since_monday = date_obj.weekday()
            first_day = date_obj - timedelta(days=days_since_monday)

        else:
            # For 'Day' or others, return the date itself
            return date_obj.strftime('%Y-%m-%d')

        # Check for holidays and skip to next non-holiday
        offset = 0
        while True:
            check_date = first_day + timedelta(days=offset)
            date_str = check_date.strftime('%Y-%m-%d')

            sql = text("SELECT * FROM holidays WHERE date=:date")
            result = self.db.execute(sql, {'date': date_str}).first()

            if not result:
                return date_str

            offset += 1

    async def load_production_samples(self, sample_date: str, user_id: int) -> Dict[str, Any]:
        """
        Load production samples based on sample matrix and frequency.
        Migrated from loadProductionSample.m
        """
        errors = []
        date_obj = datetime.strptime(sample_date, '%Y-%m-%d')

        try:
            # Check each frequency type
            frequencies = ['1/2 year', 'Week', 'Month', 'Quarter']

            for frequency in frequencies:
                first_day = self._get_first_day_of_period(date_obj, frequency)

                # Only process if sample_date is the first day of the period
                if first_day == sample_date:
                    description = {
                        '1/2 year': '1/2 year sample',
                        'Week': 'Weekly sample',
                        'Month': 'Monthly sample',
                        'Quarter': 'Quarterly sample'
                    }.get(frequency, f'{frequency} sample')

                    freq_errors = await self._load_production_samples_by_frequency(
                        sample_date, frequency, user_id, description, 'PRO'
                    )
                    errors.extend(freq_errors)

            # Always process daily samples
            daily_errors = await self._load_production_samples_by_frequency(
                sample_date, 'Day', user_id, 'Daily sample', 'PRO'
            )
            errors.extend(daily_errors)

            return {
                'success': len(errors) == 0,
                'message': f"Production samples loaded for {sample_date}",
                'errors': errors if errors else None
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error loading production samples: {e}")
            raise

    async def _load_production_samples_by_frequency(
        self,
        sample_date: str,
        frequency: str,
        user_id: int,
        description: str,
        type_sample: str
    ) -> List[str]:
        """Load production samples for a specific frequency"""
        errors = []

        # Get sample matrix entries for this frequency that don't have samples yet
        sql_matrix = text("""
            SELECT x.id, x.sample_point_id, x.spec_id, x.product_id, x.quality_id, p.name as Product, 
                q.name as Quality, sp.name as SamplePoint
            FROM samplematrix x, product p, quality q, samplepoint sp
            WHERE frequency=:frequency
            AND x.product_id=p.id
            AND x.quality_id=q.id
            AND x.sample_point_id=sp.id
            AND NOT EXISTS(
                SELECT * FROM sample s
                WHERE type_sample=:type_sample
                AND s.date=:sample_date
                AND x.product_id=s.product_id
            )
        """)

        matrix_entries = self.db.execute(sql_matrix, {
            'frequency': frequency,
            'type_sample': type_sample,
            'sample_date': sample_date
        }).fetchall()

        # Generate time offsets for each sample (starting from 06:00, +1 minute each)
        base_time = datetime.strptime('06:00', '%H:%M')

        for idx, entry in enumerate(matrix_entries):
            entry_dict = dict(entry._mapping)
            sample_time = (base_time + timedelta(minutes=idx)).strftime('%H:%M')

            error = await self._insert_production_sample(
                entry_dict, user_id, sample_date, description, type_sample, sample_time
            )

            if error:
                errors.append(error)

        self.db.commit()
        return errors

    async def _insert_production_sample(
        self,
        matrix_entry: Dict,
        user_id: int,
        sample_date: str,
        description: str,
        type_sample: str,
        sample_time: str
    ) -> Optional[str]:
        """Insert a single production sample"""
        product_id = matrix_entry['product_id']
        quality_id = matrix_entry['quality_id']
        sample_matrix_id = matrix_entry['id']
        sample_point_id = matrix_entry['sample_point_id']

        # Check for duplicates
        sql_check = text("""
            SELECT id FROM sample
            WHERE type_sample=:type_sample
            AND sample_matrix_id=:sample_matrix_id
            AND date=:sample_date
            AND time=:sample_time
        """)
        existing = self.db.execute(sql_check, {
            'type_sample': type_sample,
            'sample_matrix_id': sample_matrix_id,
            'sample_date': sample_date,
            'sample_time': sample_time
        }).first()

        if existing:
            return None  # Skip duplicates silently

        # Get spec ID
        spec_id, _ = self._get_spec_id(product_id, quality_id, '')

        if not spec_id:
            return (
                f"No specification found for Product={matrix_entry['Product']}, "
                f"Quality={matrix_entry['Quality']}"
            )

        # Get variable limits
        sql_limits = text("""
            SELECT v.name as variable, d.variable_id, NULL as min, NULL as max
            FROM dsamplematrix d, variable v
            WHERE d.variable_id=v.id AND d.sample_matrix_id=:sample_matrix_id
            AND NOT EXISTS(
                SELECT * FROM dspec d2, samplematrix sm, spec sp
                WHERE sm.product_id=sp.product_id
                AND sm.quality_id=sp.quality_id
                AND sp.type_spec='GEN'
                AND d.variable_id = d2.variable_id
            )
            UNION
            SELECT v.name as variable, d.variable_id, d2.min_value as min, d2.max_value as max
            FROM dsamplematrix d, variable v, dspec d2, samplematrix sm, spec sp
            WHERE d.variable_id=v.id
            AND d.sample_matrix_id=:sample_matrix_id
            AND sp.type_spec='GEN'
            AND d.sample_matrix_id=sm.id
            AND d2.spec_id=sp.id
            AND sm.product_id=sp.product_id
            AND sm.quality_id=sp.quality_id
            AND d.variable_id = d2.variable_id
        """)

        limits = [dict(r._mapping) for r in self.db.execute(sql_limits, {
            'sample_matrix_id': sample_matrix_id
        })]

        if not limits:
            return (
                f"No variables found for Product={matrix_entry['Product']}, "
                f"Quality={matrix_entry['Quality']}, SamplePoint={matrix_entry['SamplePoint']}"
            )

        # Generate sample number
        sample_number = self._get_sample_number(sample_date, type_sample)

        # Insert sample
        current_time = datetime.now()

        sql_insert = text("""
            INSERT INTO sample(
                type_sample, spec_id, customer, sample_matrix_id,
                product_id, quality_id, created_by_id, creation_date,
                date, time, description, sample_number, sample_point_id, article_no
            )
            OUTPUT INSERTED.id
            VALUES (
                :type_sample, :spec_id, 'INC', :sample_matrix_id,
                :product_id, :quality_id, :user_id, :creation_date,
                :date, :time, :description, :sample_number, :sample_point_id, 0
            )
        """)

        result = self.db.execute(sql_insert, {
            'type_sample': type_sample,
            'spec_id': spec_id,
            'sample_matrix_id': sample_matrix_id,
            'product_id': product_id,
            'quality_id': quality_id,
            'user_id': user_id,
            'creation_date': current_time,
            'date': sample_date,
            'time': sample_time,
            'description': description,
            'sample_number': sample_number,
            'sample_point_id': sample_point_id
        })

        # Get inserted sample ID from OUTPUT clause
        row = result.first()
        if row:
            sample_id = int(row[0]) if row[0] is not None else None
        else:
            sample_id = None

        if sample_id is None:
            raise ValueError("Failed to retrieve inserted sample ID for production sample")

        # Insert measurements
        self._insert_measurements(sample_id, limits)

        return None
