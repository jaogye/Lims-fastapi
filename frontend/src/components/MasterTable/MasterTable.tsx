import { useState, useEffect, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import { apiService } from '../../services/api';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

const TABLE_TYPES = [
  { value: 'products', label: 'Products' },
  { value: 'qualities', label: 'Qualities' },
  { value: 'variables', label: 'Variables' },
  { value: 'holidays', label: 'Holidays' },
  { value: 'sample_points', label: 'Sample Points' },
  { value: 'spec-client', label: 'Spec - Client' },
  { value: 'spec-gen', label: 'Spec - General' },
  { value: 'samplematrix', label: 'Sample Matrix' },
  { value: 'maps', label: 'Maps' }
];

interface MasterDataRow {
  [key: string]: any;
}

function MasterTable() {
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [rowData, setRowData] = useState<MasterDataRow[]>([]);
  const [columnDefs, setColumnDefs] = useState<ColDef[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');

  // Error console state
  const [showErrorConsole, setShowErrorConsole] = useState(false);
  const [errorMessages, setErrorMessages] = useState<string>('');
  const [pendingData, setPendingData] = useState<MasterDataRow[]>([]);
  const [pendingColumnDefs, setPendingColumnDefs] = useState<ColDef[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const gridRef = useRef<AgGridReact>(null);
  const pendingGridRef = useRef<AgGridReact>(null);

  // Auto-size all columns to fit content
  const autoSizeAll = (skipHeader = false) => {
    if (gridRef.current?.api) {
      const allColumnIds: string[] = [];
      gridRef.current.api.getColumns()?.forEach((column) => {
        allColumnIds.push(column.getId());
      });
      gridRef.current.api.autoSizeColumns(allColumnIds, skipHeader);
    }
  };

  // Auto-size pending data grid columns
  const autoSizePending = (skipHeader = false) => {
    if (pendingGridRef.current?.api) {
      const allColumnIds: string[] = [];
      pendingGridRef.current.api.getColumns()?.forEach((column) => {
        allColumnIds.push(column.getId());
      });
      pendingGridRef.current.api.autoSizeColumns(allColumnIds, skipHeader);
    }
  };

  // Download error messages as text file
  const handleDownloadMessages = () => {
    const blob = new Blob([errorMessages], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${selectedTable}_errors.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  // Download pending data as Excel file
  const handleDownloadPendings = async () => {
    if (pendingData.length === 0) return;

    const XLSX = await import('xlsx');
    const worksheet = XLSX.utils.json_to_sheet(pendingData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Pending Data');
    XLSX.writeFile(workbook, `${selectedTable}_pending_data.xlsx`);
  };

  // Close error console
  const handleCloseErrorConsole = () => {
    setShowErrorConsole(false);
    setErrorMessages('');
    setPendingData([]);
    setPendingColumnDefs([]);
  };

  // Download data from backend
  const handleDownload = async () => {
    if (!selectedTable) {
      setError('Please select a table type first');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const blob = await apiService.downloadMasterData(selectedTable);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${selectedTable}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccessMessage(`Successfully downloaded ${selectedTable}.xlsx`);

      // Also load and display the data
      await loadTableData();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to download ${selectedTable}`);
    } finally {
      setLoading(false);
    }
  };

  // Load and display table data
  const loadTableData = async () => {
    if (!selectedTable) return;

    setLoading(true);
    setError('');

    try {
      const blob = await apiService.downloadMasterData(selectedTable);

      // Parse Excel blob to JSON for display
      const arrayBuffer = await blob.arrayBuffer();
      const XLSX = await import('xlsx');
      const workbook = XLSX.read(arrayBuffer, { type: 'array' });
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
      const jsonData = XLSX.utils.sheet_to_json(firstSheet);

      if (jsonData.length > 0) {
        // Generate column definitions from data
        const cols: ColDef[] = Object.keys(jsonData[0] as object).map((key) => ({
          field: key,
          headerName: key,
          sortable: true,
          filter: true,
          resizable: true,
          editable: false,
        }));

        setColumnDefs(cols);
        setRowData(jsonData as MasterDataRow[]);

        // Auto-size columns after data loads
        setTimeout(() => autoSizeAll(false), 100);
      } else {
        setRowData([]);
        setColumnDefs([]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to load ${selectedTable} data`);
      setRowData([]);
      setColumnDefs([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload
  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!selectedTable) {
      setError('Please select a table type first');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');
    setShowErrorConsole(false);

    try {
      const response = await apiService.uploadMasterData(selectedTable, file);

      // Check if there are errors or pending data
      if (response.pendingdata && response.pendingdata !== null) {
        // Parse pending data JSON string
        const pendingDataArray = JSON.parse(response.pendingdata);

        // Format error messages
        let errorText = '';
        if (response.errors && response.errors.length > 0) {
          errorText = response.errors.join('\n');
        }

        setErrorMessages(errorText);
        setPendingData(pendingDataArray);

        // Generate column definitions for pending data
        if (pendingDataArray.length > 0) {
          const cols: ColDef[] = Object.keys(pendingDataArray[0]).map((key) => ({
            field: key,
            headerName: key,
            sortable: true,
            filter: true,
            resizable: true,
          }));
          setPendingColumnDefs(cols);
        }

        // Show error console
        setShowErrorConsole(true);
        setError(`Upload completed with ${response.errors?.length || 0} validation errors. Check the error console below.`);
      } else if (response.success) {
        setSuccessMessage(`Successfully uploaded ${file.name}. ${response.rows_processed} rows processed.`);
        // Reload the table data
        await loadTableData();
      }
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail;
      if (typeof errorDetail === 'object' && errorDetail.errors) {
        setError(`Upload failed: ${errorDetail.message || 'Validation errors occurred'}`);
      } else {
        setError(errorDetail || `Failed to upload file to ${selectedTable}`);
      }
    } finally {
      setLoading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Load data when table type changes
  useEffect(() => {
    if (selectedTable) {
      loadTableData();
    } else {
      setRowData([]);
      setColumnDefs([]);
    }
  }, [selectedTable]);

  // Auto-size pending grid when data changes
  useEffect(() => {
    if (pendingData.length > 0) {
      setTimeout(() => autoSizePending(false), 100);
    }
  }, [pendingData]);

  return (
    <div>
      <div className="page-header">
        <h1>Master Tables</h1>
        <p>Download and upload Excel files for master data management</p>
      </div>

      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}

      <div className="button-group" style={{ marginBottom: '20px', alignItems: 'center' }}>
        <div className="form-group" style={{ marginBottom: 0, marginRight: '20px', minWidth: '250px' }}>
          <label htmlFor="table-select">Select Table Type:</label>
          <select
            id="table-select"
            value={selectedTable}
            onChange={(e) => setSelectedTable(e.target.value)}
            disabled={loading}
          >
            <option value="">-- Select a table --</option>
            {TABLE_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleDownload}
          disabled={!selectedTable || loading}
        >
          {loading ? 'Processing...' : 'Download'}
        </button>

        <button
          className="btn btn-secondary"
          onClick={() => fileInputRef.current?.click()}
          disabled={!selectedTable || loading}
        >
          Upload
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls"
          onChange={handleUpload}
          style={{ display: 'none' }}
        />
      </div>

      {/* Error Console */}
      {showErrorConsole && (
        <div style={{
          border: '2px solid #f44336',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px',
          backgroundColor: '#fff5f5'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h2 style={{ margin: 0, color: '#c62828' }}>Error Console</h2>
            <button className="btn btn-secondary" onClick={handleCloseErrorConsole}>
              Close
            </button>
          </div>

          {/* Error Messages */}
          <div className="form-group">
            <label>Error Messages:</label>
            <textarea
              value={errorMessages}
              readOnly
              rows={8}
              style={{
                width: '100%',
                fontFamily: 'monospace',
                fontSize: '12px',
                backgroundColor: '#fff',
                border: '1px solid #ddd',
                padding: '10px'
              }}
            />
          </div>

          {/* Pending Data Grid */}
          <div className="form-group">
            <label>Pending Data ({pendingData.length} rows):</label>
            <div className="ag-theme-alpine" style={{ height: '300px', width: '100%' }}>
              <AgGridReact
                ref={pendingGridRef}
                rowData={pendingData}
                columnDefs={pendingColumnDefs}
                defaultColDef={{
                  sortable: true,
                  filter: true,
                  resizable: true,
                }}
                animateRows={true}
                onGridReady={(params) => {
                  setTimeout(() => autoSizePending(false), 100);
                }}
              />
            </div>
          </div>

          {/* Download Buttons */}
          <div className="button-group" style={{ marginTop: '15px' }}>
            <button
              className="btn btn-secondary"
              onClick={handleDownloadMessages}
              disabled={!errorMessages}
            >
              Download Messages
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleDownloadPendings}
              disabled={pendingData.length === 0}
            >
              Download Pendings
            </button>
          </div>
        </div>
      )}

      {/* Main Data Grid */}
      <div className="ag-theme-alpine" style={{ height: '600px', width: '100%' }}>
        <AgGridReact
          ref={gridRef}
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={{
            sortable: true,
            filter: true,
            resizable: true,
          }}
          animateRows={true}
          rowSelection="multiple"
          onGridReady={(params) => {
            setTimeout(() => autoSizeAll(false), 100);
          }}
          onFirstDataRendered={(params) => {
            autoSizeAll(false);
          }}
        />
      </div>

      {rowData.length > 0 && (
        <div style={{ marginTop: '10px', color: '#666' }}>
          Showing {rowData.length} rows
        </div>
      )}
    </div>
  );
}

export default MasterTable;
