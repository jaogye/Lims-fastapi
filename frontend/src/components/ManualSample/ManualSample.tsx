import { useState, useEffect, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, ICellRendererParams } from 'ag-grid-community';
import { apiService } from '../../services/api';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

interface ManualSample {
  id: number;
  sample_number?: string;
  sample_point?: string;
  product: string;
  quality: string;
  sample_date: string;
  sample_time: string;
  remark?: string;
}

interface DropdownOption {
  id: number;
  name: string;
}

function ManualSample() {
  const today = new Date().toISOString().split('T')[0];

  // Form state
  const [selectedDate, setSelectedDate] = useState<string>(today);
  const [samplePointId, setSamplePointId] = useState<number | ''>('');
  const [productId, setProductId] = useState<number | ''>('');
  const [qualityId, setQualityId] = useState<number | ''>('');
  const [specId, setSpecId] = useState<number | null>(null);
  const [sampleTime, setSampleTime] = useState<string>('08:00');
  const [remark, setRemark] = useState<string>('');

  // Dropdown data
  const [samplePoints, setSamplePoints] = useState<DropdownOption[]>([]);
  const [products, setProducts] = useState<DropdownOption[]>([]);
  const [qualities, setQualities] = useState<DropdownOption[]>([]);

  // Grid state
  const [samples, setSamples] = useState<ManualSample[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');

  // Edit mode state
  const [editingId, setEditingId] = useState<number | null>(null);

  const gridRef = useRef<AgGridReact>(null);

  // Auto-size all columns
  const autoSizeAll = (skipHeader = false) => {
    if (gridRef.current?.api) {
      const allColumnIds: string[] = [];
      gridRef.current.api.getColumns()?.forEach((column) => {
        allColumnIds.push(column.getId());
      });
      gridRef.current.api.autoSizeColumns(allColumnIds, skipHeader);
    }
  };

  // Load dropdown data on mount
  useEffect(() => {
    loadDropdownData();
  }, []);

  // Load samples when date changes
  useEffect(() => {
    if (selectedDate) {
      loadSamples();
    }
  }, [selectedDate]);

  // Load filtered qualities when product changes
  useEffect(() => {
    if (productId) {
      loadQualitiesByProduct(productId as number);
    } else {
      setQualities([]);
      setQualityId('');
      setSpecId(null);
    }
  }, [productId]);

  // Load spec_id when both product and quality are selected
  useEffect(() => {
    if (productId && qualityId) {
      loadSpecId(productId as number, qualityId as number);
    } else {
      setSpecId(null);
    }
  }, [productId, qualityId]);

  const loadDropdownData = async () => {
    try {
      const [samplePointsData, productsData] = await Promise.all([
        apiService.getSamplePoints(),
        apiService.getProducts()
      ]);

      setSamplePoints(samplePointsData);
      setProducts(productsData);
    } catch (err: any) {
      setError('Failed to load dropdown data');
    }
  };

  const loadQualitiesByProduct = async (productId: number) => {
    try {
      const qualitiesData = await apiService.getQualitiesByProduct(productId);
      setQualities(qualitiesData);
    } catch (err: any) {
      setError('Failed to load qualities for selected product');
      setQualities([]);
    }
  };

  const loadSpecId = async (productId: number, qualityId: number) => {
    try {
      const spec_id = await apiService.getSpecId(productId, qualityId);
      setSpecId(spec_id);
    } catch (err: any) {
      setError('Failed to load spec ID');
      setSpecId(null);
    }
  };

  const loadSamples = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await apiService.getManualSamples(selectedDate);
      setSamples(data);

      // Auto-size columns after data loads
      setTimeout(() => autoSizeAll(false), 100);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load manual samples');
      setSamples([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!samplePointId || !productId || !qualityId) {
      setError('Please fill in all required fields');
      return;
    }

    if (!specId) {
      setError('No specification found for selected product and quality combination');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const sampleData = {
        sample_point_id: Number(samplePointId),
        product_id: Number(productId),
        quality_id: Number(qualityId),
        spec_id: specId,
        sample_date: selectedDate,
        sample_time: sampleTime,
        remark: remark || undefined
      };

      if (editingId) {
        // Update existing sample
        await apiService.updateManualSample(editingId, sampleData);
        setSuccessMessage('Manual sample updated successfully');
        setEditingId(null);
      } else {
        // Create new sample
        await apiService.createManualSample(sampleData);
        setSuccessMessage('Manual sample created successfully');
      }

      // Reset form
      resetForm();

      // Reload samples
      await loadSamples();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save manual sample');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = async (sample: ManualSample) => {
    // Find the IDs from the dropdown options
    const samplePoint = samplePoints.find(sp => sp.name === sample.sample_point);
    const product = products.find(p => p.name === sample.product);

    setEditingId(sample.id);
    setSamplePointId(samplePoint?.id || '');
    setProductId(product?.id || '');

    // Ensure time is in HH:MM format (strip seconds if present)
    const timeValue = sample.sample_time ? sample.sample_time.substring(0, 5) : '08:00';
    setSampleTime(timeValue);

    setRemark(sample.remark || '');

    // Load qualities for the product, then set quality
    if (product?.id) {
      try {
        const qualitiesData = await apiService.getQualitiesByProduct(product.id);
        setQualities(qualitiesData);

        // Find and set quality after qualities are loaded
        const quality = qualitiesData.find(q => q.name === sample.quality);
        if (quality) {
          setQualityId(quality.id);
        }
      } catch (err: any) {
        setError('Failed to load qualities for editing');
      }
    }

    // Scroll to form
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDelete = async (sampleId: number) => {
    if (!window.confirm('Are you sure you want to delete this manual sample?')) {
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      await apiService.deleteManualSample(sampleId);
      setSuccessMessage('Manual sample deleted successfully');

      // Reload samples
      await loadSamples();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete manual sample');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setSamplePointId('');
    setProductId('');
    setQualityId('');
    setSpecId(null);
    setSampleTime('08:00');
    setRemark('');
    setEditingId(null);
  };

  const handleCancel = () => {
    resetForm();
    setError('');
  };

  // Action buttons cell renderer
  const ActionButtonsRenderer = (props: ICellRendererParams<ManualSample>) => {
    return (
      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          className="btn btn-secondary"
          onClick={() => handleEdit(props.data!)}
          style={{ padding: '4px 12px', fontSize: '12px' }}
        >
          Edit
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => handleDelete(props.data!.id)}
          style={{ padding: '4px 12px', fontSize: '12px', backgroundColor: '#d32f2f', borderColor: '#d32f2f' }}
        >
          Delete
        </button>
      </div>
    );
  };

  const columnDefs: ColDef<ManualSample>[] = [
    { field: 'sample_number', headerName: 'Sample Number', sortable: true, filter: true, resizable: true },
    { field: 'sample_point', headerName: 'Sample Point', sortable: true, filter: true, resizable: true },
    { field: 'product', headerName: 'Product', sortable: true, filter: true, resizable: true },
    { field: 'quality', headerName: 'Quality', sortable: true, filter: true, resizable: true },
    { field: 'sample_time', headerName: 'Time', sortable: true, filter: true, resizable: true, width: 100 },
    { field: 'remark', headerName: 'Remark', sortable: true, filter: true, resizable: true },
    {
      headerName: 'Actions',
      cellRenderer: ActionButtonsRenderer,
      width: 180,
      sortable: false,
      filter: false,
      resizable: false,
      pinned: 'right'
    }
  ];

  return (
    <div>
      <div className="page-header">
        <h1>Manual Sample</h1>
        <p>Create and manage manual samples</p>
      </div>

      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}

      {/* Form Section */}
      <div style={{
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        backgroundColor: '#f9f9f9'
      }}>
        <h2 style={{ marginBottom: '20px', fontSize: '18px' }}>
          {editingId ? 'Edit Manual Sample' : 'Create New Manual Sample'}
        </h2>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px', marginBottom: '15px' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="sample-date">Sample Date *</label>
              <input
                id="sample-date"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="sample-point">Sample Point *</label>
              <select
                id="sample-point"
                value={samplePointId}
                onChange={(e) => setSamplePointId(Number(e.target.value))}
                disabled={loading}
                required
              >
                <option value="">-- Select Sample Point --</option>
                {samplePoints.map((sp) => (
                  <option key={sp.id} value={sp.id}>
                    {sp.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="product">Product *</label>
              <select
                id="product"
                value={productId}
                onChange={(e) => setProductId(Number(e.target.value))}
                disabled={loading}
                required
              >
                <option value="">-- Select Product --</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="quality">Quality *</label>
              <select
                id="quality"
                value={qualityId}
                onChange={(e) => setQualityId(Number(e.target.value))}
                disabled={loading || !productId}
                required
              >
                <option value="">
                  {productId ? '-- Select Quality --' : '-- Select Product First --'}
                </option>
                {qualities.map((q) => (
                  <option key={q.id} value={q.id}>
                    {q.name}
                  </option>
                ))}
              </select>
              {productId && qualities.length === 0 && (
                <small style={{ color: '#d32f2f', display: 'block', marginTop: '4px' }}>
                  No qualities available for selected product
                </small>
              )}
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="sample-time">Sample Time *</label>
              <input
                id="sample-time"
                type="time"
                value={sampleTime}
                onChange={(e) => setSampleTime(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="remark">Remark</label>
              <input
                id="remark"
                type="text"
                value={remark}
                onChange={(e) => setRemark(e.target.value)}
                disabled={loading}
                placeholder="Optional remark"
              />
            </div>
          </div>

          <div className="button-group">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !specId}
            >
              {loading ? 'Processing...' : (editingId ? 'Update Sample' : 'Create Sample')}
            </button>

            {editingId && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleCancel}
                disabled={loading}
              >
                Cancel
              </button>
            )}
          </div>

          {productId && qualityId && specId && (
            <div style={{ marginTop: '10px', padding: '8px', backgroundColor: '#e3f2fd', borderRadius: '4px', fontSize: '13px' }}>
              ✓ Specification ID: {specId} (auto-calculated from product and quality)
            </div>
          )}

          {productId && qualityId && !specId && (
            <div style={{ marginTop: '10px', padding: '8px', backgroundColor: '#fff3e0', borderRadius: '4px', fontSize: '13px', color: '#f57c00' }}>
              ⚠ No specification found for this product-quality combination
            </div>
          )}
        </form>
      </div>

      {/* Grid Section */}
      <div>
        <h2 style={{ marginBottom: '10px', fontSize: '18px' }}>
          Manual Samples for {selectedDate}
        </h2>

        <div className="ag-theme-alpine" style={{ height: '500px', width: '100%' }}>
          <AgGridReact
            ref={gridRef}
            rowData={samples}
            columnDefs={columnDefs}
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
            }}
            animateRows={true}
            onGridReady={() => {
              setTimeout(() => autoSizeAll(false), 100);
            }}
            onFirstDataRendered={() => {
              autoSizeAll(false);
            }}
          />
        </div>

        {samples.length > 0 && (
          <div style={{ marginTop: '10px', color: '#666' }}>
            Showing {samples.length} manual sample{samples.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}

export default ManualSample;
