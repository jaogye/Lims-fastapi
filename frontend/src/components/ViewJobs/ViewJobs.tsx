import { useState, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, RowClickedEvent } from 'ag-grid-community';
import { apiService } from '../../services/api';
import type { SampleDetailResponse, QualityInfoItem } from '../../types';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

interface PendingTest {
  variable: string;
  min?: number;
  max?: number;
}

function ViewJobs() {
  const [sampleDate, setSampleDate] = useState<string>('');
  const [allSamples, setAllSamples] = useState<SampleDetailResponse[]>([]);
  const [incompleteSamples, setIncompleteSamples] = useState<SampleDetailResponse[]>([]);
  const [selectedSample, setSelectedSample] = useState<SampleDetailResponse | null>(null);
  const [pendingTests, setPendingTests] = useState<PendingTest[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const samplesGridRef = useRef<AgGridReact>(null);
  const pendingGridRef = useRef<AgGridReact>(null);

  // Helper function to check if a sample is incomplete
  const isSampleIncomplete = (sample: SampleDetailResponse): boolean => {
    return sample.quality_info.some(item => item.value === null || item.value === undefined);
  };

  // Helper function to get pending tests for a sample
  const getPendingTests = (sample: SampleDetailResponse): PendingTest[] => {
    return sample.quality_info
      .filter(item => item.value === null || item.value === undefined)
      .map(item => ({
        variable: item.variable,
        min: item.min,
        max: item.max
      }));
  };

  const handleSelectSamples = async () => {
    if (!sampleDate) {
      setError('Please select a date');
      return;
    }

    setLoading(true);
    setError('');
    setSelectedSample(null);
    setPendingTests([]);

    try {
      const data = await apiService.getSamples(sampleDate);
      setAllSamples(data);

      // Filter incomplete samples
      const incomplete = data.filter(isSampleIncomplete);
      setIncompleteSamples(incomplete);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load samples');
      setAllSamples([]);
      setIncompleteSamples([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRowClicked = (event: RowClickedEvent<SampleDetailResponse>) => {
    if (event.data) {
      setSelectedSample(event.data);
      const pending = getPendingTests(event.data);
      setPendingTests(pending);
    }
  };

  const samplesColumnDefs: ColDef<SampleDetailResponse>[] = [
    { field: 'sample_number', headerName: 'Sample Number', sortable: true, filter: true, flex: 1 },
    { field: 'product', headerName: 'Product', sortable: true, filter: true, flex: 1 },
    { field: 'quality', headerName: 'Quality', sortable: true, filter: true, flex: 1 },
    { field: 'tank', headerName: 'Tank', sortable: true, filter: true, flex: 1 },
  ];

  const pendingTestsColumnDefs: ColDef<PendingTest>[] = [
    { field: 'variable', headerName: 'Variable', sortable: true, filter: true, flex: 2 },
    {
      field: 'min',
      headerName: 'Min',
      sortable: true,
      filter: true,
      flex: 1,
      valueFormatter: (params) => params.value !== null && params.value !== undefined ? params.value.toString() : ''
    },
    {
      field: 'max',
      headerName: 'Max',
      sortable: true,
      filter: true,
      flex: 1,
      valueFormatter: (params) => params.value !== null && params.value !== undefined ? params.value.toString() : ''
    },
  ];

  const completedCount = allSamples.length - incompleteSamples.length;

  return (
    <div>
      <div className="page-header">
        <h1>Samples</h1>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Date Selection */}
      <div style={{ display: 'flex', gap: '20px', marginBottom: '20px', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <label htmlFor="sampleDate">Date:</label>
          <input
            id="sampleDate"
            type="date"
            value={sampleDate}
            onChange={(e) => setSampleDate(e.target.value)}
            disabled={loading}
          />
        </div>

        <button
          className="btn btn-primary"
          onClick={handleSelectSamples}
          disabled={loading || !sampleDate}
        >
          {loading ? 'Loading...' : 'Select'}
        </button>
      </div>

      {/* Samples Grid */}
      <div style={{ marginBottom: '20px' }}>
        <div className="ag-theme-alpine" style={{ height: '300px', width: '100%' }}>
          <AgGridReact
            ref={samplesGridRef}
            rowData={incompleteSamples}
            columnDefs={samplesColumnDefs}
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

      {/* Sample Counters */}
      <div style={{
        display: 'flex',
        gap: '20px',
        marginBottom: '30px',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontWeight: 'bold' }}>Total Samples:</label>
          <input
            type="text"
            value={allSamples.length}
            readOnly
            style={{ width: '60px', textAlign: 'center', backgroundColor: '#fff' }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontWeight: 'bold' }}>Completed Samples:</label>
          <input
            type="text"
            value={completedCount}
            readOnly
            style={{ width: '60px', textAlign: 'center', backgroundColor: '#fff' }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontWeight: 'bold' }}>Incompleted Samples:</label>
          <input
            type="text"
            value={incompleteSamples.length}
            readOnly
            style={{ width: '60px', textAlign: 'center', backgroundColor: '#fff' }}
          />
        </div>
      </div>

      {/* Pending Tests Section */}
      <div>
        <h2 style={{ fontSize: '24px', marginBottom: '15px', textAlign: 'center' }}>Pending to test</h2>
        <div className="ag-theme-alpine" style={{ height: '300px', width: '100%' }}>
          <AgGridReact
            ref={pendingGridRef}
            rowData={pendingTests}
            columnDefs={pendingTestsColumnDefs}
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
            }}
            animateRows={true}
          />
        </div>
      </div>
    </div>
  );
}

export default ViewJobs;
