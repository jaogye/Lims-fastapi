import { useState, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, ICellRendererParams, RowClickedEvent } from 'ag-grid-community';
import { apiService } from '../../services/api';
import type { SampleDetailResponse } from '../../types';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

function ReportGeneration() {
  const [sampleDate, setSampleDate] = useState<string>('');
  const [samples, setSamples] = useState<SampleDetailResponse[]>([]);
  const [selectedSample, setSelectedSample] = useState<SampleDetailResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const gridRef = useRef<AgGridReact>(null);

  const handleSelectSamples = async () => {
    if (!sampleDate) {
      setError('Please select a date');
      return;
    }

    setLoading(true);
    setError('');
    setSelectedSample(null);

    try {
      const data = await apiService.getSamples(sampleDate);
      setSamples(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load samples');
      setSamples([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRowClicked = (event: RowClickedEvent<SampleDetailResponse>) => {
    if (event.data) {
      setSelectedSample(event.data);
    }
  };

  const handleGenerateReport = async (reportType: 'coa' | 'coc' | 'day') => {
    if (!selectedSample) return;

    setLoading(true);
    setError('');

    try {
      let blob: Blob;
      let filename: string;

      switch (reportType) {
        case 'coa':
          blob = await apiService.generateCOA(selectedSample.sample_number);
          filename = `COA_${selectedSample.sample_number}.pdf`;
          break;
        case 'coc':
          blob = await apiService.generateCOC(selectedSample.sample_number);
          filename = `COC_${selectedSample.sample_number}.pdf`;
          break;
        case 'day':
          blob = await apiService.generateDayCertificate(selectedSample.sample_number);
          filename = `DayCert_${selectedSample.sample_number}.pdf`;
          break;
      }

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to generate ${reportType.toUpperCase()} report`);
    } finally {
      setLoading(false);
    }
  };

  const columnDefs: ColDef<SampleDetailResponse>[] = [
    { field: 'sample_number', headerName: 'Sample Number', sortable: true, filter: true, flex: 1 },
    { field: 'product', headerName: 'Product', sortable: true, filter: true, flex: 1 },
    { field: 'quality', headerName: 'Quality', sortable: true, filter: true, flex: 1 },
    { field: 'tank', headerName: 'Tank', sortable: true, filter: true, flex: 1 },
  ];

  return (
    <div>
      <div className="page-header">
        <h1>Report Generation</h1>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Date Selection and Report Buttons */}
      <div style={{ display: 'flex', gap: '20px', marginBottom: '20px', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <label htmlFor="sampleDate">Date:</label>
          <input
            id="sampleDate"
            type="date"
            value={sampleDate}
            onChange={(e) => setSampleDate(e.target.value)}
            disabled={loading}
          />
          <button
            className="btn btn-primary"
            onClick={handleSelectSamples}
            disabled={loading || !sampleDate}
          >
            {loading ? 'Loading...' : 'Select'}
          </button>
        </div>

        <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px' }}>
          <button
            className="btn btn-primary"
            onClick={() => handleGenerateReport('coa')}
            disabled={!selectedSample || selectedSample.sample_coa !== 'X' || loading}
          >
            COA
          </button>
          <button
            className="btn btn-primary"
            onClick={() => handleGenerateReport('coc')}
            disabled={!selectedSample || selectedSample.sample_coc !== 'X' || loading}
          >
            COC
          </button>
          <button
            className="btn btn-primary"
            onClick={() => handleGenerateReport('day')}
            disabled={!selectedSample || selectedSample.sample_day_coa !== 'X' || loading}
          >
            C of Day
          </button>
        </div>
      </div>

      {/* Main Layout: Grid and Sample Details */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '20px' }}>
        {/* Samples Grid */}
        <div>
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
              rowSelection="single"
              onRowClicked={handleRowClicked}
              animateRows={true}
            />
          </div>
        </div>

        {/* Sample Details */}
        <div style={{
          border: '1px solid #ddd',
          borderRadius: '8px',
          padding: '20px',
          backgroundColor: '#f9f9f9'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Sample Details</h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div className="form-group">
              <label>Sample Number</label>
              <input
                type="text"
                value={selectedSample?.sample_number || ''}
                readOnly
                style={{ backgroundColor: '#fff' }}
              />
            </div>

            <div className="form-group">
              <label>Product</label>
              <input
                type="text"
                value={selectedSample?.product || ''}
                readOnly
                style={{ backgroundColor: '#fff' }}
              />
            </div>

            <div className="form-group">
              <label>Quality</label>
              <input
                type="text"
                value={selectedSample?.quality || ''}
                readOnly
                style={{ backgroundColor: '#fff' }}
              />
            </div>

            <div className="form-group">
              <label>SamplePoint</label>
              <input
                type="text"
                value={selectedSample?.tank || ''}
                readOnly
                style={{ backgroundColor: '#fff' }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              <div className="form-group">
                <label>Date</label>
                <input
                  type="text"
                  value={selectedSample?.sample_date || ''}
                  readOnly
                  style={{ backgroundColor: '#fff' }}
                />
              </div>

              <div className="form-group">
                <label>Time</label>
                <input
                  type="text"
                  value={''} // Time is not available in the response
                  readOnly
                  style={{ backgroundColor: '#fff' }}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Remark</label>
              <input
                type="text"
                value={selectedSample?.remark || ''}
                readOnly
                style={{ backgroundColor: '#fff' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportGeneration;
